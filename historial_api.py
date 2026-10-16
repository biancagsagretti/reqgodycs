"""
Receptor de webhooks de ClickUp.
Guarda cada cambio de estado en historial_estados.csv.

Ejecutar:
    export CLICKUP_TOKEN="pk_..."
    export CLICKUP_WEBHOOK_SECRET="..."   # el 'secret' que devuelve registrar_webhook.py
    uvicorn historial_api:app --host 0.0.0.0 --port 8000
"""
import csv
import hashlib
import hmac
import json
import os
import threading
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import requests
from fastapi import FastAPI, HTTPException, Request

CLICKUP_TOKEN = os.environ["CLICKUP_TOKEN"]
WEBHOOK_SECRET = os.environ.get("CLICKUP_WEBHOOK_SECRET", "")
CSV_PATH = Path(os.environ.get("HISTORIAL_CSV", "historial_estados.csv"))
TZ = ZoneInfo("America/Argentina/Buenos_Aires")

COLUMNAS = [
    "ID de tarea",
    "Nombre de la tarea",
    "Estado anterior",
    "Estado nuevo",
    "Fecha del cambio",
    "Responsable",
]

app = FastAPI()
lock = threading.Lock()


def nombre_tarea(task_id: str) -> str:
    """El webhook no trae el nombre de la tarea, hay que pedirlo a la API."""
    try:
        r = requests.get(
            f"https://api.clickup.com/api/v2/task/{task_id}",
            headers={"Authorization": CLICKUP_TOKEN},
            timeout=10,
        )
        r.raise_for_status()
        return r.json().get("name", "")
    except Exception as e:
        print(f"No se pudo obtener el nombre de {task_id}: {e}")
        return ""


def firma_valida(body: bytes, firma: str) -> bool:
    esperada = hmac.new(WEBHOOK_SECRET.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(esperada, firma or "")


def guardar_fila(fila: list):
    with lock:
        nuevo = not CSV_PATH.exists()
        with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            if nuevo:
                w.writerow(COLUMNAS)
            w.writerow(fila)


@app.get("/")
def salud():
    return {"ok": True}


@app.post("/webhook")
async def webhook(request: Request):
    body = await request.body()

    if WEBHOOK_SECRET and not firma_valida(body, request.headers.get("X-Signature", "")):
        raise HTTPException(status_code=401, detail="Firma inválida")

    data = json.loads(body)

    if data.get("event") != "taskStatusUpdated":
        return {"ignorado": True}

    task_id = data["task_id"]
    nombre = nombre_tarea(task_id)

    for item in data.get("history_items", []):
        if item.get("field") != "status":
            continue

        fecha = datetime.fromtimestamp(int(item["date"]) / 1000, TZ)
        guardar_fila([
            task_id,
            nombre,
            (item.get("before") or {}).get("status", ""),
            (item.get("after") or {}).get("status", ""),
            fecha.strftime("%d/%m/%Y %H:%M:%S"),
            (item.get("user") or {}).get("username", ""),
        ])

    return {"ok": True}

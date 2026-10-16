"""
Registra el webhook en ClickUp (se ejecuta UNA sola vez).

    export CLICKUP_TOKEN="pk_..."
    python registrar_webhook.py https://TU-URL-PUBLICA/webhook
"""
import os
import sys

import requests

TOKEN = os.environ["CLICKUP_TOKEN"]
LIST_ID = "901303346872"  # la misma lista que usás en app.py
HEADERS = {"Authorization": TOKEN, "Content-Type": "application/json"}
BASE = "https://api.clickup.com/api/v2"

if len(sys.argv) < 2:
    sys.exit("Uso: python registrar_webhook.py https://TU-URL-PUBLICA/webhook")

endpoint = sys.argv[1]

# 1) Obtener el team_id (Workspace)
r = requests.get(f"{BASE}/team", headers=HEADERS, timeout=15)
r.raise_for_status()
teams = r.json()["teams"]
for t in teams:
    print(f"Workspace: {t['name']} -> {t['id']}")
team_id = teams[0]["id"]  # si tenés varios workspaces, elegí el correcto

# 2) Crear el webhook filtrado por lista
payload = {
    "endpoint": endpoint,
    "events": ["taskStatusUpdated"],
    "list_id": LIST_ID,
}
r = requests.post(f"{BASE}/team/{team_id}/webhook", headers=HEADERS, json=payload, timeout=15)
print(r.status_code, r.text)
r.raise_for_status()

wh = r.json()["webhook"]
print("\nWebhook creado. Guardá estos datos:")
print("  id:    ", wh["id"])
print("  secret:", wh["secret"], " <- usalo como CLICKUP_WEBHOOK_SECRET")

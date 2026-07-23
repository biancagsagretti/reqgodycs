import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sb
import plotly.express as px
import requests
import json
##################################
# LECTURA DE LOS ARCHIVOS
##################################

try:
    sheet_url1 = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQA8Myx6exmmDQBzrTUAsh669fAI8K3i_PGmwKfJTrXINaZJ8FZV5blmk8ZShVSTyzm97oq1ZZxsFnF/pub?gid=0&single=true&output=csv'

    df = pd.read_csv(sheet_url1,index_col=0)

except Exception as e: 
    print(f"ERROR importando archivo1 {e}")

try:
    sheet_url2 = 'https://docs.google.com/spreadsheets/d/1MfYXz8lKmjvb9kK9eD1bONuLL4nKbw07YwfEUop47js/export?format=csv&gid=498017106'

    # Leer el contenido directamente en un DataFrame
    df = pd.read_csv(sheet_url2)

except Exception as e: 
    print(f"ERROR importando     archivo2 {e}")


##################################
# ESTILOS
##################################

# Cambiar el color de fondo usando CSS
st.markdown(
    """
    <style>
    .stApp {
        background-color: #035c80;  /* Cambia este valor al color que desees */
        color: #fcfcfc
    }
    </style>
    """,
    unsafe_allow_html=True
)

##################################
# MUESTREO DE LOS DATOS
##################################

st.title('Indicadores de Requerimientos Godycs')

st.write('Lista de Requerimientos de formulario de Google')

# Crear nueva columna unificada
df.drop(columns=['Nombre y Apellido:'])

# Cambiar el nombre de una columna
df.rename(columns={'Nombre y Apellido:.1': 'Nombre_Responsable'}, inplace=True)
st.write(df)


st.write('Requerimientos por DG')

# Obtener la columna de interés
columna_dg = '¿A qué área pertenece?'

# Contar ocurrencias de cada área
conteo_dg = df[columna_dg].value_counts()

# Separar en mayores o iguales a 10 y menores a 10
conteo_filtrado = conteo_dg[conteo_dg >= 10]
conteo_otras = conteo_dg[conteo_dg < 10]

# Agregar la suma de las categorías pequeñas como "Otras"
conteo_final = conteo_filtrado.copy()
conteo_final['Otras'] = conteo_otras.sum()

# Mostrar datos
st.write("Conteo por área:")
#st.write(conteo_final)

# ==========================
# FILTRO
# ==========================

col1, col2, col3 = st.columns(3)

with col1:
    filtro_req = st.text_input(
        "🔎 Buscar requerimiento"
    )

with col2:
    filtro_nombre = st.multiselect(
        "👤 Responsable",
        options=sorted(df["Nombre_Responsable"].dropna().unique()),
        default=sorted(df["Nombre_Responsable"].dropna().unique())
    )

with col3:
    filtro_area = st.multiselect(
        "🏢 Área",
        options=sorted(df["¿A qué área pertenece?"].dropna().unique()),
        default=sorted(df["¿A qué área pertenece?"].dropna().unique())
    )

# ==========================
# APLICAR FILTROS
# ==========================

df_filtrado = df[
    (df["Nombre_Responsable"].isin(filtro_nombre)) &
    (df["¿A qué área pertenece?"].isin(filtro_area))
]

if filtro_req:
    # Reemplaza "Requerimiento" por el nombre real de la columna
    df_filtrado = df_filtrado[
        df_filtrado["Requerimiento"].str.contains(
            filtro_req,
            case=False,
            na=False
        )
    ]

# Mostrar tabla filtrada
st.dataframe(
    df_filtrado,
    use_container_width=True,
    hide_index=True
)

# Crear gráfico de torta
fig, ax = plt.subplots()
fig.patch.set_facecolor('#f0f2f6')  # color del fondo de la figura
ax.pie(conteo_final, labels=conteo_final.index, autopct='%1.1f%%', startangle=90)
ax.axis('equal')  # Para que el gráfico sea un círculo
st.pyplot(fig)


######################################################################

# Asegurar que la columna de fecha está en datetime
df['Marca temporal'] = pd.to_datetime(df['Marca temporal'])

# Agrupar la cantidad de requerimientos por fecha (sin hora)
conteo_diario = df['Marca temporal'].dt.date.value_counts()
conteo_diario = conteo_diario.sort_index()

# Convertir a Serie con datetime index
serie_conteo = pd.Series(conteo_diario.values, index=pd.to_datetime(conteo_diario.index))

# Obtener lista de años únicos
años_disponibles = sorted(serie_conteo.index.year.unique(), reverse=True)

# Mostrar selector de año
año_seleccionado = st.selectbox("Seleccioná un año", años_disponibles)

# Filtrar datos del año seleccionado
serie_filtrada = serie_conteo[serie_conteo.index.year == año_seleccionado]

# Mostrar tabla opcional
st.write(f"Requerimientos por fecha en {año_seleccionado}:")
# st.dataframe(serie_filtrada)

# Crear el heatmap estilo GitHub
# fig, ax = plt.subplots(figsize=(12, 4))
# calmap.calendarplot(serie_filtrada, how='sum', cmap='YlGn', fillcolor='lightgray', linewidth=0.5)
# fig = plt.gcf()
# st.pyplot(fig)

# Supongamos que ya tenés una serie con fechas
# serie_filtrada = pd.Series(...)

df = serie_filtrada.reset_index()
print(df)
df.columns = ["date", "value"]

df["date"] = pd.to_datetime(df["date"])
df["day"] = df["date"].dt.dayofweek
# df["week"] = df["date"].dt.isocalendar().week
# df["year"] = df["date"].dt.year
df["month"] = df["date"].dt.month

fig = px.density_heatmap(
    df,
    x="month",
    y="day",
    z="value",
    histfunc="sum",
    nbinsx=12,
    nbinsy=7,
    color_continuous_scale="Blues",
    range_x=[1, 12],
    # range_y=[0, 6]   
)

fig.update_layout(
    yaxis=dict(
        tickmode='array',
        tickvals=[0,1,2,3,4,5,6],
        ticktext=['Lun','Mar','Mié','Jue','Vie','Sáb','Dom']
    ),
    xaxis=dict(
        tickmode='array',
        tickvals=[1,2,3,4,5,6,7,8,9,10,11,12],
        ticktext=['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic']
    )
)

st.plotly_chart(fig)

######################################################################
#Se utilizarán datos de la API de ClickUp para obtener información sobre los requerimientos y su estado.



url = "https://api.clickup.com/api/v2/list/901303346872/task"

headers = {
    "accept": "application/json",
    "Authorization": "pk_82139533_GCB373LPD9N9IH997EY3L8EGP7C1ZM91"
}

response = requests.get(url, headers=headers)
response.raise_for_status()

jsondata = response.json()

df = pd.json_normalize(jsondata["tasks"])




print(df.head())

#Requerimientos por Miembro del Equipo

df["asignado"] = df["assignees"].apply(
    lambda x: x[0]["username"] if isinstance(x, list) and len(x) > 0 else "Sin asignar"
)

asig = (
    df.groupby("asignado")
      .size()
      .sort_values(ascending=False)
)

print(asig)


st.write('Cantidad de requerimientos asignados por persona en ClickUp')

fig, ax = plt.subplots(figsize=(10,5))

df["asignado"].value_counts().plot.bar(ax=ax)

st.pyplot(fig)


#Requerimientos por Estado

st.write('Porcentaje de requerimientos por estado en ClickUp')
# Contar tareas por estado
estado = df["status.status"].value_counts()

# Crear figura
fig, ax = plt.subplots(figsize=(8, 8))

ax.pie(
    estado,
    labels=estado.index,
    autopct="%1.1f%%",
    startangle=90
)

ax.set_title("Porcentaje de tareas por estado")

# Mostrar en Streamlit
st.pyplot(fig)


#Tabla de requerimientos




# Crear la columna Asignado
df["Asignado"] = df["assignees"].apply(
    lambda x: x[0]["username"] if isinstance(x, list) and len(x) > 0 else "Sin asignar"
)

# Crear la tabla
tabla = df[["Asignado", "name", "status.status"]].copy()

tabla.columns = [
    "Asignado",
    "Requerimiento",
    "Status"
]

st.subheader("Tabla de requerimientos y asignaciones ClickUp")

# ==========================
# FILTROS ARRIBA DE LA TABLA
# ==========================

col1, col2, col3 = st.columns(3)

with col1:
    persona = st.multiselect(
        "Asignado",
        options=sorted(tabla["Asignado"].unique()),
        default=sorted(tabla["Asignado"].unique())
    )

with col2:
    status = st.multiselect(
        "Status",
        options=sorted(tabla["Status"].unique()),
        default=sorted(tabla["Status"].unique())
    )

with col3:
    texto = st.text_input(
        "Buscar requerimiento"
    )

# Aplicar filtros
tabla_filtrada = tabla[
    (tabla["Asignado"].isin(persona)) &
    (tabla["Status"].isin(status))
]

if texto:
    tabla_filtrada = tabla_filtrada[
        tabla_filtrada["Requerimiento"].str.contains(
            texto,
            case=False,
            na=False
        )
    ]

# Mostrar tabla
st.dataframe(
    tabla_filtrada,
    use_container_width=True,
    hide_index=True
)
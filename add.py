import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import geopandas as gpd
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import folium_static
from branca.colormap import linear
import leafmap
import zipfile
import os

# Para datos vectoriales
import geopandas as gpd

# Para datos raster
import rasterio

# Para gráficos
import matplotlib.pyplot as plt

# Para crear rampas de colores
from matplotlib.colors import LinearSegmentedColormap

# Para álgebra lineal
import numpy as np

# Para descargar archivos
import requests
import zipfile
# URLs de los datos
df_data = 'https://raw.githubusercontent.com/chrismse19/proyecto_progra/refs/heads/main/merged_data.csv'
df_transporte = 'https://raw.githubusercontent.com/chrismse19/proyecto_progra/refs/heads/main/transporte_aereo.csv'
df_pib = 'https://raw.githubusercontent.com/chrismse19/proyecto_progra/refs/heads/main/pib.csv'
df_partidas = 'https://raw.githubusercontent.com/chrismse19/proyecto_progra/refs/heads/main/partidas_vuelos.csv'
URL_DATOS_PAISES = 'datos/paises.gpkg'

# Título de la app
st.title("Transporte de viajes aéreos")

# Función para cargar los datos con caché
@st.cache_data
def cargar_datos(url):
    try:
        datos = pd.read_csv(url)
        return datos
    except Exception as e:
        st.error(f"Error al cargar los datos desde {url}: {e}")
        return None

#Función para cargar los datos de los países

@st.cache_data
def cargar_datos_paises():
    paises = gpd.read_file(URL_DATOS_PAISES)
    return paises

# Cargar los datos desde las URLs
datos = cargar_datos(df_data)
datos_pib = cargar_datos(df_pib)
datos_transporte = cargar_datos(df_transporte)
datos_partidas = cargar_datos(df_partidas)

# Validar que los datos se hayan cargado correctamente
if datos is None or datos_pib is None or datos_transporte is None or datos_partidas is None:
    st.stop()

# Renombrar columnas en `datos`
columnas_espaniol = {
    'SOVEREIGNT': 'País',
    'SOV_A3': 'Código ISO',
    'TYPE': 'Tipo',
    'LABEL_X': 'Coordenada x',
    'LABEL_Y': 'Coordenada y'
}
datos = datos.rename(columns=columnas_espaniol)

# Seleccionar columnas relevantes
columnas = ['País', 'Código ISO', 'Tipo', 'Coordenada x', 'Coordenada y']
datos = datos[columnas]

# Obtener la lista de países únicos
lista_paises = datos['País'].unique().tolist()
lista_paises.sort()

# Añadir la opción "Todos" al inicio de la lista
opciones_paises = ['Todos'] + lista_paises

# Crear el selectbox en la barra lateral
pais_seleccionado = st.sidebar.selectbox(
    'Selecciona un país',
    opciones_paises
)


# ----- Filtrar datos según la selección -----

if pais_seleccionado != 'Todos':
    # Filtrar los datos para el país seleccionado
    datos_filtrados = datos[datos['País'] == pais_seleccionado]
    # Obtener el Código ISO del país seleccionado
    codigo_iso_seleccionado = datos_filtrados['Código ISO'].iloc[0]
else:
    # No aplicar filtro
    datos_filtrados = datos.copy()
    codigo_iso_seleccionado = None


# Mostrar tabla de datos cargados
st.subheader("Datos de Interés")
st.dataframe(datos, hide_index=True)

# Crear gráfico de PIB global
if 'pais' in datos_transporte.columns:
    # Transformar datos de transporte a formato largo
    df_transporte_melted = datos_transporte.melt(id_vars=['pais'], var_name='Year', value_name='GDP')

    # Limpiar datos de transporte
    df_cleaned_t = df_transporte_melted.dropna(subset=['GDP'])
    df_cleaned_t['GDP'] = pd.to_numeric(df_cleaned_t['GDP'], errors='coerce')

    # Agrupar datos de transporte por año
    df_global_t = df_cleaned_t.groupby('Year')['GDP'].sum().reset_index()
    df_global_t['pais'] = 'Mundo'

    # Crear gráfico de línea para el transporte aéreo
    fig_transporte = px.line(
        df_global_t,
        x='Year',
        y='GDP',
        title='Transporte aéreo, pasajeros transportados',
        labels={'GDP': 'Pasajeros Transportados', 'Year': 'Año'}
    )

    # Mostrar el gráfico en Streamlit
    st.subheader('Transporte aéreo: pasajeros transportados a lo largo del tiempo')
    st.plotly_chart(fig_transporte)
else:
    st.error("Los datos de transporte no tienen la columna 'pais'. Verifica el archivo.")

# MAPA


import streamlit as st
import pandas as pd
import folium
import requests
from streamlit_folium import folium_static

# Título de la aplicación
st.title("Mapa Coroplético con Streamlit y Folium")

# Cargar archivo GeoJSON desde GitHub
geojson_url = 'https://raw.githubusercontent.com/chrismse19/proyecto_progra/refs/heads/main/datos.geojson'
try:
    geojson_response = requests.get(geojson_url)
    geojson_response.raise_for_status()  # Verificar si la solicitud fue exitosa
    geojson_data = geojson_response.json()
except requests.exceptions.RequestException as e:
    st.error(f"Error al cargar el archivo GeoJSON: {e}")
    st.stop()

# Cargar archivo CSV desde GitHub
csv_url = 'https://raw.githubusercontent.com/chrismse19/proyecto_progra/refs/heads/main/datos.csv'
try:
    df = pd.read_csv(csv_url)
except Exception as e:
    st.error(f"Error al cargar el archivo CSV: {e}")
    st.stop()

# Crear un mapa base centrado en las coordenadas promedio de tus datos
m = folium.Map(location=[10, -84], zoom_start=6)  # Ajusta las coordenadas según tu región de interés

# Añadir el mapa coroplético
try:
    folium.Choropleth(
        geo_data=geojson_data,
        data=df,
        columns=['pais', '2019'],  # Ajusta las columnas según tus datos
        key_on='feature.properties.pais',
        fill_color='YlGnBu',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='Datos 2019'
    ).add_to(m)

    # Añadir información emergente (popups)
    folium.GeoJson(
        geojson_data,
        name="Datos detallados",
        tooltip=folium.features.GeoJsonTooltip(
            fields=["pais", "2019"],  # Ajusta los campos según tu GeoJSON
            aliases=["País:", "Transporte aéreo:"],  # Títulos personalizados
            localize=True
        )
    ).add_to(m)

    # Añadir control de capas
    folium.LayerControl().add_to(m)
except Exception as e:
    st.error(f"Error al crear el mapa: {e}")
    st.stop()

# Desplegar el mapa en Streamlit
st.subheader("Mapa con Transporte de pasajeros aéreos 2019")
folium_static(m)


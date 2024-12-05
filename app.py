
import streamlit as st
import pandas as pd
import plotly.express as px
import geopandas as gpd
import folium
from streamlit_folium import folium_static
from branca.colormap import linear
import requests

# URLs de los datos
df_data = 'https://raw.githubusercontent.com/chrismse19/proyecto_progra/refs/heads/main/merged_data.csv'
df_transporte = 'https://raw.githubusercontent.com/chrismse19/proyecto_progra/refs/heads/main/transporte_aereo.csv'
df_pib = 'https://raw.githubusercontent.com/chrismse19/proyecto_progra/refs/heads/main/pib.csv'
df_partidas = 'https://raw.githubusercontent.com/chrismse19/proyecto_progra/refs/heads/main/partidas_vuelos.csv'
URL_DATOS_PAISES = 'datos/paises.gpkg'

# Título de la app
st.title("Transporte de viajes aéreos")

csv_url = 'https://raw.githubusercontent.com/chrismse19/proyecto_progra/refs/heads/main/datos.csv'

@st.cache_data
def cargar_datos(url):
    """Función para cargar los datos desde una URL."""
    return pd.read_csv(url)

# Cargar datos
datos = cargar_datos(csv_url)

# Verificar que la columna '2019' está presente
if '2019' in datos.columns:
    # Seleccionar las columnas relevantes
    datos = datos[['pais', 'x', 'y', '2019']].dropna()
    datos = datos.rename(columns={'2019': 'Viajes aéreos', 'pais': 'País', 'x': 'Coordenada x', 'y': 'Coordenada y'})
else:
    st.error("La columna '2019' no está disponible en los datos.")
    st.stop()

# Crear barra lateral con lista de países
st.sidebar.title("Opciones de Filtro")
opciones_paises = ['Todos'] + sorted(datos['País'].unique())
pais_seleccionado = st.sidebar.selectbox("Selecciona un país:", opciones_paises)

# Filtrar datos según la selección
if pais_seleccionado != 'Todos':
    datos_filtrados = datos[datos['País'] == pais_seleccionado]
else:
    datos_filtrados = datos

# Título de la página principal
st.title("Datos de Viajes Aéreos y Gráfico Interactivo (2019)")

# Mostrar tabla de datos filtrados
st.subheader("Datos de Viajes Aéreos (2019)")
st.dataframe(datos_filtrados, hide_index=True)

# Crear gráfico interactivo con Plotly
fig = px.bar(
    datos_filtrados,
    x='País',
    y='Viajes aéreos',
    title=f"Viajes Aéreos en {pais_seleccionado if pais_seleccionado != 'Todos' else 'Todos los Países'} (2019)",
    labels={'País': 'País', 'Viajes aéreos': 'Viajes Aéreos'},
    color='Viajes aéreos',
    color_continuous_scale='viridis'
)

# Personalizar gráfico
fig.update_layout(
    xaxis_title='País',
    yaxis_title='Viajes Aéreos',
    template='plotly_white'
)

# Mostrar gráfico en Streamlit
st.plotly_chart(fig, use_container_width=True)



# MAPA COROPLÉTICO
import streamlit as st
import pandas as pd
import folium
import requests
from streamlit_folium import folium_static

# Título de la aplicación
st.title("Mapa interactivo")

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


import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de página
st.set_page_config(
    page_title="Tablero de Registros Automotores - DNRPA",
    page_icon="🚗",
    layout="wide"
)

# Carga de datos con cache para optimizar rendimiento
@st.cache_data
def load_data():
    df = pd.read_csv("DNRPA.csv")
    df['fecha'] = pd.to_datetime(df['fecha'])
    df['anio'] = df['fecha'].dt.year
    return df

df = load_data()

st.title("🚗 Tablero de Tramites de Registro Automotor (DNRPA)")
st.markdown("Análisis interactivo de patentamientos y trámites por provincia y tipo de vehículo.")

# --- BARRA LATERAL (FILTROS) ---
st.sidebar.header("Filtros de Búsqueda")

# Filtro de Años
anios_disponibles = sorted(df['anio'].unique())
anios_seleccionados = st.sidebar.slider(
    "Seleccionar Rango de Años:",
    min_value=int(min(anios_disponibles)),
    max_value=int(max(anios_disponibles)),
    value=(int(min(anios_disponibles)), int(max(anios_disponibles)))
)

# Filtro de Provincia
provincias = sorted(df['nombre_provincia_indec'].unique())
provincias_seleccionadas = st.sidebar.multiselect(
    "Provincias:",
    options=provincias,
    default=provincias
)

# Filtro de Tipo de Vehículo
tipos_vehiculo = df['tipo_vehiculo'].unique().tolist()
tipos_seleccionados = st.sidebar.multiselect(
    "Tipo de Vehículo:",
    options=tipos_vehiculo,
    default=tipos_vehiculo
)

# Filtrado del DataFrame
df_filtered = df[
    (df['anio'] >= anios_seleccionados[0]) &
    (df['anio'] <= anios_seleccionados[1]) &
    (df['nombre_provincia_indec'].isin(provincias_seleccionadas)) &
    (df['tipo_vehiculo'].isin(tipos_seleccionados))
]

# --- TARJETAS KPI ---
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Trámites Registrados", f"{df_filtered['cantidad'].sum():,}")
with col2:
    st.metric("Promedio Mensual por Provincia", f"{int(df_filtered['cantidad'].mean()):,}")
with col3:
    st.metric("Provincias Seleccionadas", f"{len(provincias_seleccionadas)}")

st.divider()

# --- GRÁFICOS PRINCIPALES ---
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Evolución Temporal de Trámites")
    df_trend = df_filtered.groupby(['fecha', 'tipo_vehiculo'])['cantidad'].sum().reset_index()
    fig_line = px.line(
        df_trend,
        x='fecha',
        y='cantidad',
        color='tipo_vehiculo',
        labels={'fecha': 'Fecha', 'cantidad': 'Cantidad', 'tipo_vehiculo': 'Tipo'},
        template="plotly_white"
    )
    st.plotly_chart(fig_line, use_container_width=True)

with col_right:
    st.subheader("Trámites Totales por Provincia")
    df_prov = df_filtered.groupby('nombre_provincia_indec')['cantidad'].sum().reset_index()
    df_prov = df_prov.sort_values(by='cantidad', ascending=True)
    fig_bar = px.bar(
        df_prov,
        x='cantidad',
        y='nombre_provincia_indec',
        orientation='h',
        labels={'cantidad': 'Cantidad Total', 'nombre_provincia_indec': 'Provincia'},
        template="plotly_white"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# --- DETALLE DE DATOS ---
with st.expander("Ver Tabla de Datos Filtrados"):
    st.dataframe(df_filtered, use_container_width=True)
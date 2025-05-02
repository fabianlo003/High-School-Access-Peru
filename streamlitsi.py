import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
from PIL import Image
import os
import streamlit.components.v1 as components


st.set_page_config(
    page_title="High School Access Peru",
    page_icon="🇵🇪",
    layout="wide"
)

def display_image(image_path):
    if os.path.exists(image_path):
        image = Image.open(image_path)
        st.image(image, caption=f"Mapa: {os.path.basename(image_path)}", use_container_width=True)
    else:
        st.warning(f"Imagen no encontrada: {image_path}")

def display_html_file(html_path):
    if os.path.exists(html_path):
        with open(html_path, 'r', encoding='utf-8') as f:
            html_data = f.read()
        components.html(html_data, height=600, scrolling=True)
    else:
        st.error(f"No se encontró el archivo: {html_path}")
        m = folium.Map(location=[-13.0456, -74.2178], zoom_start=8)
        folium.Marker([-13.0456, -74.2178], popup="Mapa de respaldo").add_to(m)
        folium_static(m)

def create_info_table(data_dict):
    return pd.DataFrame(list(data_dict.items()), columns=['Nivel', 'Cantidad'])

# Datos
huancavelica = {"Inicial": 1582, "Primaria": 1224, "Secundaria": 397}
ayacucho = {"Inicial": 1764, "Primaria": 1435, "Secundaria": 542}
total_dep = {"Inicial": 54837, "Primaria": 39274, "Secundaria": 15789}

# App
st.title("Datos colegios")
st.subheader("Departamentos de Huancavelica y Ayacucho")

tab1, tab2, tab3 = st.tabs(["Data Description", "Mapas Estáticos", "Mapas Dinámicos"])

# pestaña 1
with tab1:
    st.header("Descripción de Datos")
    st.subheader("Cantidad total de colegios")
    st.markdown("""
    Podemos observar la cantidad de colegios de inicial, primaria y secundaria en todo el Perú, 
    además de cuántos hay en los departamentos de Ayacucho y Huancavelica.
    """)

    col1, col2, col3 = st.columns(3)
    col1.subheader("En todo el país")
    col1.table(create_info_table(total_dep))

    col2.subheader("Huancavelica")
    col2.table(create_info_table(huancavelica))

    col3.subheader("Ayacucho")
    col3.table(create_info_table(ayacucho))

    st.subheader("Fuentes")
    st.markdown("""
    Para la representación de estadísticas y gráficos se ha hecho uso de un dataset proporcionado por MINEDU. 
    En él se encuentra no solo información sobre qué escuelas se encuentran en qué provincias, distritos y departamentos, 
    sino también su lugar geográfico en el mapa peruano. Para la elección de cada nivel escolar se eligieron los colegios 
    categorizados como inicial, primaria y secundaria; dejando de lado los que no tuviesen esas palabras en su descripción 
    de Modalidad. Por último, para la realización de gráficos se hizo uso de un shapefile de los distritos del Perú proporcionado por los docentes.
    """)

# pestaña 2
with tab2:
    st.header("Mapas Estáticos")

    col1, col2, col3 = st.columns(3)

     
    display_image("mapa_inicial.png")

     
    display_image("mapa_primaria.png")

     
    display_image("mapa_secundaria.png")

    st.markdown("---")
    st.subheader("Acceso a Secundarias desde Escuelas Primarias")
    col4, col5 = st.columns(2)

    with col4:
        st.markdown("### Huancavelica")
        display_image("HUANCAVELICA_min.png")
        display_image("HUANCAVELICA_max.png")

    with col5:
        st.markdown("### Ayacucho")
        display_image("AYACUCHO_min.png")
        display_image("AYACUCHO_max.png")

# pestaña 3
with tab3:
    st.header("Mapas Dinámicos")
    st.subheader("Mapa Coroplético por nivel educativo")
    display_html_file("choropleth_map_educacion.html")

    st.markdown("---")
    st.subheader("Mapas Interactivos Regionales")
    col6, col7 = st.columns(2)

    with col6:
        st.markdown("### Ayacucho")
        display_html_file("mapa_3_ayacucho.html")

    with col7:
        st.markdown("### Huancavelica")
        display_html_file("mapa_3_huancavelica.html")
    st.markdown("""
    Tanto Ayacucho como Huancavelica están ubicados en la Sierra sur-central del Perú, una región dominada por la Cordillera de los Andes.
    El terreno es mayoritariamente montañoso y accidentado por lo que crea condiciones difíciles para la construcción de infraestructura, incluyendo caminos y escuelas, y representa un gran reto para la conectividad entre comunidades.
    La accesibilidad en ambas regiones es limitada. Muchas localidades están conectadas solo por caminos rurales no asfaltados, y algunas zonas son accesibles únicamente a pie.
    Las distancias no necesariamente son largas en kilómetros, pero el tiempo de desplazamiento puede ser muy alto por el relieve accidentado y el mal estado de las vías. Esto impacta especialmente a la población estudiantil, dificultando el acceso diario a colegios secundarios desde comunidades remotas.
    Además de ello, en Huancavelica, más del 80 porciento de la población vive en zonas rurales mientras que en Ayacucho, si bien hay centros urbanos como Huamanga, el entorno sigue siendo predominantemente rural. Esta configuración implica que muchas comunidades tienen baja densidad poblacional, lo cual hace económicamente inviable construir colegios secundarios en cada localidad. Como resultado, muchos estudiantes deben trasladarse a otras comunidades para continuar su educación, aumentando las tasas de deserción escolar.
    """)


if st.sidebar.checkbox("Mostrar rutas de archivos"):
    rutas = [
        "mapa_inicial.png", "mapa_primaria.png", "mapa_secundaria.png",
        "HUANCAVELICA_min.png", "HUANCAVELICA_max.png",
        "AYACUCHO_min.png", "AYACUCHO_max.png"
    ]
    for path in rutas:
        st.sidebar.code(path)
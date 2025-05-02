import pandas as pd
import geopandas as gpd
import folium
import os

# === RUTAS ===
script_dir = os.path.dirname(__file__)  # Carpeta actual del script
os.chdir(script_dir)

# === CARGA DE DATOS ===
df = pd.read_html('listado_iiee.xls')[0]
geo_distrito = gpd.read_file('../High-School-Access-Peru/shape_file/DISTRITOS.shp')

# === FILTROS POR NIVEL EDUCATIVO ===
inicial = df[df['Nivel / Modalidad'].str.contains('Inicial', case=False, na=False)]
primaria = df[df['Nivel / Modalidad'].str.contains('Primaria', case=False, na=False)]
secundaria = df[df['Nivel / Modalidad'].str.contains('Secundaria', case=False, na=False)]

# === CONTEO POR DISTRITO ===
conteo_inicial = inicial.groupby('Ubigeo').size().reset_index(name='conteo_inicial')
conteo_primaria = primaria.groupby('Ubigeo').size().reset_index(name='conteo_primaria')
conteo_secundaria = secundaria.groupby('Ubigeo').size().reset_index(name='conteo_secundaria')

# === MERGE CON SHAPEFILE ===
geo_distrito['IDDIST'] = geo_distrito['IDDIST'].astype(str)
conteo_inicial['Ubigeo'] = conteo_inicial['Ubigeo'].astype(str)
conteo_primaria['Ubigeo'] = conteo_primaria['Ubigeo'].astype(str)
conteo_secundaria['Ubigeo'] = conteo_secundaria['Ubigeo'].astype(str)

geo_distrito = geo_distrito.merge(conteo_inicial, left_on='IDDIST', right_on='Ubigeo', how='left').drop(columns='Ubigeo')
geo_distrito = geo_distrito.merge(conteo_primaria, left_on='IDDIST', right_on='Ubigeo', how='left').drop(columns='Ubigeo')
geo_distrito = geo_distrito.merge(conteo_secundaria, left_on='IDDIST', right_on='Ubigeo', how='left').drop(columns='Ubigeo')

geo_distrito.fillna(0, inplace=True)

# === SIMPLIFICAR GEOMETRÍA PARA REDUCIR TAMAÑO ===
geo_distrito = geo_distrito.to_crs(epsg=4326)
geo_distrito['geometry'] = geo_distrito['geometry'].simplify(tolerance=0.01)

geojson_distritos = geo_distrito.to_json()

# === CREAR MAPA BASE ===
m = folium.Map(location=[-9.19, -75.0152], zoom_start=5, tiles='cartodbpositron')

# === FUNCIONES PARA AÑADIR CAPAS CHOROPLETH ===
def agregar_capa(nombre, columna, color, leyenda):
    folium.Choropleth(
        geo_data=geojson_distritos,
        name=nombre,
        data=geo_distrito,
        columns=['IDDIST', columna],
        key_on='feature.properties.IDDIST',
        fill_color=color,
        fill_opacity=0.6,
        line_opacity=0.8,
        line_color='black',
        legend_name=leyenda,
    ).add_to(m)

agregar_capa("Inicial", "conteo_inicial", "YlGnBu", "Escuelas Inicial")
agregar_capa("Primaria", "conteo_primaria", "YlOrRd", "Escuelas Primaria")
agregar_capa("Secundaria", "conteo_secundaria", "Reds", "Escuelas Secundaria")

folium.LayerControl().add_to(m)

# === GUARDAR MAPA HTML ===
m.save("choropleth_map_educacion.html")
print("✅ Mapa HTML generado con éxito.")


#Mapas centroide
import pandas as pd
import geopandas as gpd
import folium
from folium import Circle, CircleMarker
from shapely.geometry import Point

geo_distrito = gpd.read_file('../High-School-Access-Peru/shape_file/DISTRITOS.shp')
geo_distrito = geo_distrito.to_crs(epsg=4326)


archivo_html = 'listado_iiee.xls'
df = pd.read_html(archivo_html)[0]
df = df.dropna(subset=["Latitud", "Longitud"]).copy()

# Crear geometría
df["geometry"] = df.apply(lambda row: Point(row["Longitud"], row["Latitud"]), axis=1)
gdf = gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326").to_crs(epsg=32718)
gdf = gdf.to_crs(epsg=4326)

def crear_mapa_dep(nombre_dep):
    gdf_dep = gdf[gdf['Departamento'].str.upper() == nombre_dep.upper()]
    
    primarias = gdf_dep[gdf_dep['Nivel / Modalidad'].str.contains("Primaria", case=False, na=False)].copy()
    secundarias = gdf_dep[gdf_dep['Nivel / Modalidad'].str.contains("Secundaria", case=False, na=False)].copy()

    primarias_m = primarias.to_crs(epsg=32718)
    secundarias_m = secundarias.to_crs(epsg=32718)

    primarias_m['buffer5km'] = primarias_m.geometry.buffer(5000)
    conteos = []
    ids_secundarias = []

    for idx, primaria in primarias_m.iterrows():
        buffer_geom = primaria['buffer5km']
        dentro = secundarias_m[secundarias_m.geometry.within(buffer_geom)]
        conteos.append(len(dentro))
        ids_secundarias.append(dentro.index.tolist())

    primarias['secundcerc'] = conteos
    primarias['cod_secundarias'] = ids_secundarias

    # Mínimo y máximo
    min_val = primarias['secundcerc'].min()
    max_val = primarias['secundcerc'].max()

    primarias_min = primarias[primarias['secundcerc'] == min_val]
    primarias_max = primarias[primarias['secundcerc'] == max_val]

    # Centro del mapa
    centro = primarias.geometry.centroid.unary_union.centroid
    mapa = folium.Map(location=[centro.y, centro.x], zoom_start=8)

    def adding(grupo, color, titulo):
        for _, primaria in grupo.iterrows():
            lat, lon = primaria.geometry.y, primaria.geometry.x

            folium.Marker(
                location=[lat, lon],
                popup=f"{titulo}: {primaria['Nombre de SS.EE.']}<br>Secundarias cercanas: {primaria['secundcerc']}",
                icon=folium.Icon(color=color)
            ).add_to(mapa)

            Circle(
                location=[lat, lon],
                radius=5000,
                color=color,
                fill=True,
                fill_opacity=0.1
            ).add_to(mapa)

            # Añadir secundarias cercanas (solo para las con máximo)
            if primaria['secundcerc'] > 0:
                ids = primaria['cod_secundarias']
                secundarias_dentro = secundarias.loc[ids]
                for _, row in secundarias_dentro.iterrows():
                    CircleMarker(
                        location=[row.geometry.y, row.geometry.x],
                        radius=3,
                        color='blue',
                        fill=True,
                        fill_opacity=0.7
                    ).add_to(mapa)

    # Agregar primarias sin secundarias (rojo) y con más secundarias (verde)
    adding(primarias_min, 'red', 'codigo 0 secundarias')
    adding(primarias_max, 'green', 'codigo máx secundarias')

    mapa.save(f"mapa_3_{nombre_dep.lower()}.html")
    print(f" {nombre_dep.title()} guardado.")

# Ejecutar para ambos
crear_mapa_dep('HUANCAVELICA')
crear_mapa_dep('AYACUCHO')


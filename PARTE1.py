


import pandas as pd
import os
import geopandas as gpd
import matplotlib.pyplot as plt

import pandas as pd
#Task 1
script_dir = os.path.dirname(__file__)  # Esto obtiene la ruta del script actual
os.chdir(script_dir)
 
df = pd.read_html(r'../High-School-Access-Peru/listado_iiee.xls')[0]
print(df.head())
geo_distrito = gpd.read_file( r'../High-School-Access-Peru/shape_file/DISTRITOS.shp')
print(geo_distrito.tail())
inicial = df[df['Nivel / Modalidad'].str.contains('Inicial', case=False, na=False)]
primaria = df[df['Nivel / Modalidad'].str.contains('Primaria', case=False, na=False)]
secundaria = df[df['Nivel / Modalidad'].str.contains('Secundaria', case=False, na=False)]
# Contar las escuelas por distrito
conteo_inicial = inicial.groupby('Ubigeo').size().reset_index(name='conteo_inicial')
conteo_primaria = primaria.groupby('Ubigeo').size().reset_index(name='conteo_primaria')
conteo_secundaria = secundaria.groupby('Ubigeo').size().reset_index(name='conteo_secundaria')


geo_distrito['IDDIST'] = geo_distrito['IDDIST'].astype(str)
conteo_inicial['Ubigeo'] = conteo_inicial['Ubigeo'].astype(str)
conteo_primaria['Ubigeo'] = conteo_primaria['Ubigeo'].astype(str)
conteo_secundaria['Ubigeo'] = conteo_secundaria['Ubigeo'].astype(str)
# Unir los conteos con el shapefile de distritos
geo_distrito = geo_distrito.merge(conteo_inicial, left_on='IDDIST', right_on='Ubigeo', how='left' )
geo_distrito.drop(columns=['Ubigeo'], inplace=True)  # Borrar Ubigeo duplicado
geo_distrito = geo_distrito.merge(conteo_primaria, left_on='IDDIST', right_on='Ubigeo', how='left' )
geo_distrito.drop(columns=['Ubigeo'], inplace=True)  # Borrar Ubigeo duplicado
geo_distrito = geo_distrito.merge(conteo_secundaria, left_on='IDDIST', right_on='Ubigeo', how='left' )
geo_distrito.drop(columns=['Ubigeo'], inplace=True)  # Borrar Ubigeo duplicado
# Rellenar NaN (distritos sin escuelas) con 0
geo_distrito[['conteo_inicial', 'conteo_primaria', 'conteo_secundaria']] = geo_distrito[['conteo_inicial', 'conteo_primaria', 'conteo_secundaria']].fillna(0)

import matplotlib.pyplot as plt

# Mapa de Inicial
fig, ax = plt.subplots(1, 1, figsize=(10, 12))
geo_distrito.plot(column='conteo_inicial', 
                  cmap='Blues', 
                  linewidth=0.8, 
                  edgecolor='0.8', 
                  legend=True, 
                  ax=ax)

ax.set_title('Distribución de Escuelas Inicial por Distrito', fontsize=15)
ax.axis('off')
plt.savefig('mapa_inicial.png', dpi=300, bbox_inches='tight')
# Mapa de Primaria
fig, ax = plt.subplots(1, 1, figsize=(10, 12))
geo_distrito.plot(column='conteo_primaria', 
                  cmap='Greens', 
                  linewidth=0.8, 
                  edgecolor='0.8', 
                  legend=True, 
                  ax=ax)

ax.set_title('Distribución de Escuelas Primaria por Distrito', fontsize=15)
ax.axis('off')
plt.savefig('mapa_primaria.png', dpi=300, bbox_inches='tight')
# Mapa de Secundaria
fig, ax = plt.subplots(1, 1, figsize=(10, 12))
geo_distrito.plot(column='conteo_secundaria', 
                  cmap='Reds', 
                  linewidth=0.8, 
                  edgecolor='0.8', 
                  legend=True, 
                  ax=ax)

ax.set_title('Distribución de Escuelas Secundaria por Distrito', fontsize=15)
ax.axis('off')
plt.savefig('mapa_secundaria.png', dpi=300, bbox_inches='tight')


#Task 2
import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt

# crear geo
df2 = df.dropna(subset=['Latitud', 'Longitud']).copy()
df2['geometry'] = df2.apply(lambda row: Point(row['Longitud'], row['Latitud']), axis=1)
gdf = gpd.GeoDataFrame(df2, geometry='geometry', crs='EPSG:4326').to_crs(epsg=32718)

# Filtrar por dep
gdf_huancavelica = gdf[gdf['Departamento'].str.upper() == 'HUANCAVELICA']
gdf_ayacucho = gdf[gdf['Departamento'].str.upper() == 'AYACUCHO']

def analizar_dep(gdf_dep, nombre_dep, guardar=False):
    print(f"\n Resultados {nombre_dep}")

    # Filtrar por nivel
    primarias = gdf_dep[gdf_dep["Nivel / Modalidad"].str.contains("Primaria", case=False, na=False)].copy()
    secundarias = gdf_dep[gdf_dep["Nivel / Modalidad"].str.contains("Secundaria", case=False, na=False)].copy()

    # Buffer
    primarias['buffer5km'] = primarias.geometry.buffer(5000)
    primarias['secundarias_cercanas'] = primarias['buffer5km'].apply(
        lambda buf: secundarias[secundarias.geometry.within(buf)].shape[0]
    )

    min_primaria = primarias.loc[primarias['secundarias_cercanas'].idxmin()]
    max_primaria = primarias.loc[primarias['secundarias_cercanas'].idxmax()]

    print(f" Colegio menos secundarias: {min_primaria['Nombre de SS.EE.']} - {min_primaria['secundarias_cercanas']}")
    print(f" Colegio más secundarias: {max_primaria['Nombre de SS.EE.']} - {max_primaria['secundarias_cercanas']}")

    def graficar(primaria, titulo, nombre_archivo):
        buffer_geom = primaria['buffer5km']
        centro_geom = primaria.geometry
        secundarias_en_radio = secundarias[secundarias.geometry.within(buffer_geom)]

        fig, ax = plt.subplots(figsize=(10, 10))
        ax.set_facecolor("#f9f9f9")

        # Estilo de buffer
        gpd.GeoSeries(buffer_geom).plot(ax=ax, facecolor='#ffc2c2', edgecolor='red', alpha=0.3, linewidth=2, label='Radio 5 km')

        # Punto de primaria
        gpd.GeoSeries([centro_geom]).plot(ax=ax, color='#d00000', markersize=150, marker='o', label='Primaria')

        # Puntos de secundarias
        secundarias_en_radio.plot(ax=ax, color='#005f73', markersize=40, alpha=0.8, label='Secundarias')

        # Título y leyenda
        ax.set_title(f'{titulo}\n{primaria["Nombre de SS.EE."]} ({nombre_dep})', fontsize=15, fontweight='bold', pad=15)
        ax.text(0.5, -0.08, f'Secundarias cercanas: {primaria["secundarias_cercanas"]}',
                transform=ax.transAxes, ha='center', fontsize=12, bbox=dict(facecolor='white', alpha=0.8, edgecolor='gray'))

        ax.legend(loc='lower right', frameon=True)
        ax.axis('off')

        if guardar:
            plt.savefig(f"{nombre_archivo}.png", dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor())
        

    graficar(min_primaria, 'Colegio con menos secundarias cerca', f"{nombre_dep}_min")
    graficar(max_primaria, 'Colegio con mas secundarias cerca', f"{nombre_dep}_max")

analizar_dep(gdf_huancavelica, "HUANCAVELICA", guardar=True)
analizar_dep(gdf_ayacucho, "AYACUCHO", guardar=True)

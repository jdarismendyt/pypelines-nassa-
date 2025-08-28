import folium
import pandas as pd
import logging
import os
from folium.plugins import HeatMap
import numpy as np

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_fire_map(df: pd.DataFrame, country: str, output_path: str) -> str:
    """
    Crea un mapa interactivo de focos de calor usando Folium
    
    Args:
        df: DataFrame con datos procesados
        country: Código de país para título
        output_path: Ruta para guardar el mapa HTML
    
    Returns:
        Ruta del archivo HTML generado
    """
    try:
        # Verificar que tenemos las columnas necesarias
        required_columns = {'latitude', 'longitude'}
        if not required_columns.issubset(df.columns):
            missing = required_columns - set(df.columns)
            logging.error(f"Columnas faltantes para el mapa: {missing}")
            return None
        
        # Obtener centro del país basado en los datos
        avg_lat = df['latitude'].mean()
        avg_lon = df['longitude'].mean()
        
        # Crear mapa base
        fire_map = folium.Map(
            location=[avg_lat, avg_lon],
            zoom_start=6,
            tiles='CartoDB dark_matter'
        )
        
        # Añadir capa de calor
        heat_data = []
        for _, row in df.iterrows():
            # Usar temperatura si está disponible, de lo contrario valor por defecto
            intensity = row.get('brightness_ti4', 1) if 'brightness_ti4' in df.columns else 1
            heat_data.append([row['latitude'], row['longitude'], intensity])
        
        HeatMap(
            heat_data,
            radius=15,
            gradient={0.4: 'blue', 0.6: 'lime', 0.7: 'yellow', 0.8: 'orange', 1.0: 'red'}
        ).add_to(fire_map)
        
        # Añadir marcadores para los focos más intensos si tenemos datos de intensidad
        if 'intensity' in df.columns:
            top_fires = df[df['intensity'].isin(['High', 'Extreme'])]
            for _, row in top_fires.iterrows():
                popup_text = (
                    f"<b>Intensity:</b> {row['intensity']}<br>"
                    f"<b>Brightness:</b> {row.get('brightness_ti4', 'N/A')} K<br>"
                    f"<b>Date:</b> {row.get('acquisition_date', 'N/A')}"
                )
                folium.CircleMarker(
                    location=[row['latitude'], row['longitude']],
                    radius=5,
                    color='red',
                    fill=True,
                    fill_color='red',
                    popup=popup_text
                ).add_to(fire_map)
        
        # Añadir título
        date_range = f"{df['acquisition_date'].min()} to {df['acquisition_date'].max()}"
        title_html = f'''
            <h3 align="center" style="font-size:16px">
                <b>Fire Hotspots - {country} ({date_range})</b>
            </h3>
        '''
        fire_map.get_root().html.add_child(folium.Element(title_html))
        
        # Guardar mapa
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fire_map.save(output_path)
        logging.info(f"Mapa guardado en: {output_path}")
        
        return output_path
    
    except Exception as e:
        logging.error(f"Error creando mapa: {str(e)}")
        return None
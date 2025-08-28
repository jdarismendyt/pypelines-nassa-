import pandas as pd
import numpy as np
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_fire_data(input_path: str, country: str) -> pd.DataFrame:
    """
    Procesa los datos crudos de incendios y extrae información relevante
    
    Args:
        input_path: Ruta al archivo CSV crudo
        country: Código de país para filtrar datos
    
    Returns:
        DataFrame procesado con información relevante
    """
    try:
        # Leer datos crudos
        df = pd.read_csv(input_path)
        logging.info(f"Datos crudos cargados: {len(df)} registros")
        logging.info(f"Columnas disponibles: {', '.join(df.columns)}")
        
        # Renombrar columnas según diferentes nombres posibles
        column_mapping = {
            'brightness': 'brightness_ti4',  # Nombre en este archivo
            'bright_ti4': 'brightness_ti4',  # Nombre común en otros datasets
            'acq_date': 'acquisition_date',
            'acq_time': 'acquisition_time',
            'latitude': 'latitude',
            'longitude': 'longitude',
            'frp': 'frp',
            'confidence': 'confidence',
            'daynight': 'day_night'
        }
        
        # Aplicar renombrado solo para columnas existentes
        rename_dict = {}
        for orig, new in column_mapping.items():
            if orig in df.columns:
                rename_dict[orig] = new
        df = df.rename(columns=rename_dict)
        
        logging.info(f"Columnas después de renombrar: {', '.join(df.columns)}")
        
        # Crear columna de fecha/hora si es posible
        if 'acquisition_date' in df.columns and 'acquisition_time' in df.columns:
            try:
                # Convertir tiempo a string de 4 dígitos
                df['acquisition_time'] = df['acquisition_time'].astype(str).str.zfill(4)
                
                # Crear columna combinada
                df['datetime'] = pd.to_datetime(
                    df['acquisition_date'] + ' ' + df['acquisition_time'],
                    format='%Y-%m-%d %H%M',
                    errors='coerce'
                )
                
                # Si la conversión falla, mantener solo la fecha
                if df['datetime'].isnull().any():
                    df['acquisition_date'] = pd.to_datetime(df['acquisition_date'], errors='coerce')
            except Exception as e:
                logging.warning(f"Error procesando fechas: {str(e)}")
                df['acquisition_date'] = pd.to_datetime(df['acquisition_date'], errors='coerce')
        
        # Calcular intensidad si tenemos datos de temperatura
        if 'brightness_ti4' in df.columns:
            # Calcular bins dinámicamente basados en los datos
            min_val = df['brightness_ti4'].min()
            max_val = df['brightness_ti4'].max()
            
            bins = [
                min_val - 1,
                min_val + (max_val - min_val) * 0.3,
                min_val + (max_val - min_val) * 0.6,
                min_val + (max_val - min_val) * 0.8,
                max_val + 1
            ]
            
            df['intensity'] = pd.cut(
                df['brightness_ti4'],
                bins=bins,
                labels=['Low', 'Medium', 'High', 'Extreme'],
                right=False
            )
        else:
            logging.warning("No se encontró columna de temperatura (brightness_ti4)")
        
        # Añadir columna de país
        df['country'] = country
        
        # Eliminar filas sin ubicación
        if 'latitude' in df.columns and 'longitude' in df.columns:
            initial_count = len(df)
            df = df.dropna(subset=['latitude', 'longitude'])
            if len(df) < initial_count:
                logging.warning(f"Se eliminaron {initial_count - len(df)} registros sin coordenadas")
        
        logging.info(f"Datos procesados: {len(df)} registros válidos")
        return df
    
    except Exception as e:
        logging.error(f"Error procesando datos: {str(e)}")
        return None
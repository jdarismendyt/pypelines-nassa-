import requests
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Tuple

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def download_data(api_key: str, dataset: str, country: str, days: int, end_date: str, output_path: str) -> None:
    """
    Descarga datos de FIRMS con manejo de timeout y reintentos
    
    Args:
        api_key: Clave API de FIRMS
        dataset: Nombre del dataset (ej. MODIS_SP)
        country: Código de país (3 letras)
        days: Número de días hacia atrás desde end_date
        end_date: Fecha final del período (YYYY-MM-DD)
        output_path: Ruta de salida para el archivo CSV
    """
    base_url = "https://firms.modaps.eosdis.nasa.gov/api/country/csv"
    url = f"{base_url}/{api_key}/{dataset}/{country}/{days}/{end_date}"
    
    headers = {
        'User-Agent': 'FireDataPipeline/1.0 (danielarysmendi@hotmail.com)'
    }
    
    logging.info(f"Solicitando datos: {url}")
    
    max_retries = 3
    retry_delay = 5  # segundos
    
    for attempt in range(max_retries):
        try:
            # Aumentamos el timeout a 45 segundos
            response = requests.get(url, headers=headers, timeout=45)
            
            # Verificar si la respuesta es válida
            if response.status_code == 200:
                content = response.text.strip()
                
                # Manejar respuestas vacías o de error
                if not content or "Invalid" in content:
                    logging.warning(f"Respuesta inválida: {content[:100]}...")
                    return
                    
                # Crear directorios si no existen
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                # Guardar datos en CSV
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                logging.info(f"Datos guardados en: {output_path} ({len(content)} bytes)")
                return
                
            # Manejar otros códigos de estado
            elif response.status_code == 404:
                logging.error("Recurso no encontrado - verifica parámetros")
                return
            elif response.status_code == 401:
                logging.error("API_KEY inválida o no autorizada")
                return
            else:
                logging.warning(f"Respuesta inesperada: {response.status_code}")
                
        except requests.exceptions.Timeout:
            logging.warning(f"Timeout en intento {attempt+1}/{max_retries}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay * (attempt + 1))  # Backoff incremental
                continue
            else:
                logging.error("Timeout después de múltiples intentos")
                return
                
        except requests.exceptions.RequestException as e:
            logging.error(f"Error de conexión: {str(e)}")
            return
    
    logging.error("No se pudo completar la solicitud después de reintentos")

def calculate_date_range(end_date: str, days: int) -> Tuple[str, str]:
    """Calcula el rango de fechas basado en end_date y days"""
    try:
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        start_dt = end_dt - timedelta(days=days-1)
        return start_dt.strftime("%Y-%m-%d"), end_date
    except ValueError:
        logging.error("Formato de fecha inválido")
        return "0000-00-00", "0000-00-00"
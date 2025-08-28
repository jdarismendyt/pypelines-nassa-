from dotenv import load_dotenv
load_dotenv()
from src.utils import load_config
from src.api_client import download_data
from src.process import process_fire_data
from src.visualize import create_fire_map
from src.report import generate_fire_report
import os
import pandas as pd
from datetime import datetime
import logging

# Configuración básica de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("pipeline.log")
    ]
)

# Cargar configuración
cfg = load_config("config/settings.yaml")
logging.info("Configuración cargada:")
logging.info(f"- Dataset: {cfg['dataset']}")
logging.info(f"- País: {cfg['country']}")
logging.info(f"- Días: {cfg['days']}")
logging.info(f"- Fecha final: {cfg['end_date']}")

# Crear nombre de archivo basado en fecha y país
file_date = datetime.now().strftime("%Y%m%d_%H%M%S")
country = cfg["country"]
dataset = cfg["dataset"]

# 1. Descargar datos
raw_file = f"data/raw/{file_date}_{country}_{dataset}_raw.csv"
logging.info(f"Descargando datos a: {raw_file}")
download_data(
    api_key=cfg["api_key"],
    dataset=cfg["dataset"],
    country=cfg["country"],
    days=cfg["days"],
    end_date=cfg["end_date"],
    output_path=raw_file
)

# 2. Procesar datos
processed_file = f"data/processed/{file_date}_{country}_processed.csv"
logging.info(f"Procesando datos: {raw_file}")
df = process_fire_data(raw_file, cfg["country"])

# Guardar datos procesados si existen
if df is not None and not df.empty:
    df.to_csv(processed_file, index=False)
    logging.info(f"Datos procesados guardados en: {processed_file}")
    
    # 3. Crear visualización (mapa HTML)
    map_file = f"reports/figures/{file_date}_{country}_fire_map.html"
    logging.info(f"Creando mapa: {map_file}")
    map_path = create_fire_map(df, cfg["country"], map_file)
    
    # 4. Generar reporte (PDF sin mapa)
    report_file = f"reports/pdfs/{file_date}_{country}_fire_report.pdf"
    logging.info(f"Generando reporte: {report_file}")
    generate_fire_report(df, cfg["country"], report_file)
    
    # Resumen final
    logging.info("\n✅ Pipeline completado exitosamente!")
    logging.info(f"  - Datos crudos: {raw_file}")
    logging.info(f"  - Datos procesados: {processed_file}")
    if map_path:
        logging.info(f"  - Mapa interactivo: {map_path}")
    logging.info(f"  - Reporte PDF: {report_file}")
    print("\n✅ Proceso completado! Ver archivos generados.")
else:
    logging.warning("⚠️ No se encontraron focos de calor en el período analizado")
    print("⚠️ Pipeline ejecutado, pero no se encontraron datos para visualizar")
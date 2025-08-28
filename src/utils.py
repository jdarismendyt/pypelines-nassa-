import os
from dotenv import load_dotenv
import yaml
import datetime

def load_config(path: str) -> dict:
    load_dotenv()
    
    with open(path, 'r', encoding='utf-8') as f:
        raw_cfg = yaml.safe_load(f)
    
    api_key_env = os.getenv('API_KEY')
    if api_key_env is None:
        raise RuntimeError("API_KEY no está definido en .env")
    
    if raw_cfg.get('api_key') == '${API_KEY}':
        raw_cfg['api_key'] = api_key_env
    
    # Convertir días a entero
    if 'days' in raw_cfg:
        try:
            raw_cfg['days'] = int(raw_cfg['days'])
        except ValueError:
            raise ValueError("El valor de 'days' debe ser un número entero")
    
    # Manejar end_date: convertir datetime.date a string si es necesario
    if 'end_date' in raw_cfg:
        if isinstance(raw_cfg['end_date'], datetime.date):
            # Convertir objeto date a string ISO
            raw_cfg['end_date'] = raw_cfg['end_date'].isoformat()
        else:
            # Validar formato si es string
            try:
                datetime.datetime.strptime(raw_cfg['end_date'], '%Y-%m-%d')
            except (ValueError, TypeError):
                raise ValueError("Formato de fecha inválido en end_date. Use YYYY-MM-DD")
    
    return raw_cfg
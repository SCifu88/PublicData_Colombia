import pandas as pd
from datetime import datetime, timedelta
import requests
import os

api_url = 'https://www.datos.gov.co/resource/kekd-7v7h.json'
limit = 50000

raw_data = 'data/raw/calidad_aire.csv'

def get_last_year_date_str():
    """Retorna la fecha de hace un año en el formato YYYY para la API."""
    date_last_year = datetime.now()
    last_year = date_last_year.year
    return int(last_year)

def fetch_data(where_clause):
    """
    Extrae datos del API de Socrata con paginación y un filtro WHERE.
    """
    params = {
        "$limit": limit,
        "$where": where_clause
    }
    try:
        # El timeout es importante para peticiones que pueden tardar
        response = requests.get(api_url, params=params, timeout=60)
        print(response.url)
        response.raise_for_status()  # Lanza un error si la petición HTTP falla
        print(f"Extrayendo datos con Status: {response.status_code}")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error en la petición a la API: {e}")
        return None

def extract_air_quality_data():
    """
    Ciclo para extraer datos de calidad del aire del último año.
    """
    all_records = []

    # Filtro SoQL para obtener datos del último año para ciudades de interés
    # Puedes modificar o quitar este filtro para obtener más datos
    date_filter = get_last_year_date_str()
    where_clause = f"a_o > 2015"

    print(f"Iniciando extracción con el filtro: {where_clause}")

    while True:
        data = fetch_data(where_clause)
        if not data:
            print("No se recibieron más datos. Finalizando extracción.")
            break

        all_records.extend(data)

        if len(data) < limit:
            print("Última página de datos alcanzada.")
            break

    if not all_records:
        print("No se extrajo ningún registro con los filtros aplicados.")
        return

    df = pd.DataFrame(all_records)
    print(f"Extracción completa. Total de registros: {len(df)}")

    os.makedirs(os.path.dirname(raw_data), exist_ok=True)
    df.to_csv(raw_data, index=False, encoding='utf-8')
    print(f"Datos guardados exitosamente en: {raw_data}")

if __name__ == "__main__":
    extract_air_quality_data()
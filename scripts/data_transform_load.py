import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from datetime import datetime, timedelta

load_dotenv()

raw_data = os.getenv("RAW_DATA_ORIGINAL")
raw_data_transformed = os.getenv("RAW_DATA_TRANSFORMED")

db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSW")
db_name = os.getenv("DB_NAME")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")

db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

try:
    engine = create_engine(db_url)
    print("Conexión a la base de datos exitosa.")
except Exception as e:
    print(f"Error al conectar con la base de datos: {e}")
    exit()

def decodificar_fecha(serial_excel):
    """
    Convierte un número de serie de fecha de Excel a un string con formato dd/mm/aaaa HH:MM.
    """
    # El epoch de Excel es el 30 de diciembre de 1899.
    # Usamos esta fecha para compensar que Excel empieza a contar desde 1
    # y su error de creer que 1900 fue un año bisiesto.
    epoch = datetime(1899, 12, 30)
    
    # Creamos una duración de tiempo a partir del número serial.
    # timedelta maneja correctamente la parte entera (días) y la decimal (fracción del día).
    delta = timedelta(days=float(serial_excel))
    
    # Calculamos la fecha final sumando la duración al epoch.
    fecha_final = epoch + delta
    
    # Devolvemos la fecha formateada como un string.
    return fecha_final.strftime('%d/%m/%Y %H:%M')

def transform_data():
    """
    Funcion encargada de:
    * Cargar archivo csv.
    * Cambiar nombres de columnas.
    * Verificar tipo de dato de columna y colocar los valores nulos.
    
    Entrega un nuevo DataFrame de Pandas listo para ser guardado en la base de datos.
    """

    try:
        df = pd.read_csv(raw_data, encoding='utf_8_sig', sep=';')
        print(f"Datos encontrados \n Total de datos: {len(df)}")
    except FileNotFoundError:
        print(f'No se encontró el archivo {raw_data}')
        return
    
    df_copy = df.copy()

    df_transform = df_copy

    new_columns = ['id_estacion', 'autoridad_ambiental', 'estacion', 'latitud', 'longitud',
        'variable', 'unidades', 'tiempo_de_exposicion_horas', 'anno', 'promedio',
        'suma', 'no_de_datos', 'representatividad_temporal',
        'excedencias_limite_actual', 'porcentaje_excedencias_limite', 'mediana',
        'percentil_98', 'maximo', 'fechas_horas_del_maximo', 'minimo',
        'fechas_horas_del_minimo', 'dias_de_excedencias',
        'codigo_del_departamento', 'nombre_del_departamento',
        'codigo_del_municipio', 'nombre_del_municipio', 'tipo_de_estacion',
        'ubicacion']

    del_columns = ['id_estacion','codigo_del_municipio', 'codigo_del_departamento']

    df_transform.columns = new_columns
    df_transform.drop(labels=del_columns, axis=1, inplace=True)

    for columna in df_transform:
        tipo_dato = df_transform[columna].dtypes
        if tipo_dato == 'int64':
            df_transform[columna] = df_transform[columna].fillna(0)
        elif tipo_dato == 'float64':
            df_transform[columna] = df_transform[columna].fillna(0.0)
        elif tipo_dato == 'object':
            df_transform[columna] = df_transform[columna].fillna('N/A')
        else:
            print(f"La columna {columna} no tiene tipo de dato")
    i_max = 0
    for date_max in df_transform["fechas_horas_del_maximo"]:
        date = str(date_max)

        if '-' in date:
            guion = date.find('-')
            new_date = date[:guion-1]
        else:
            new_date = date

        if '/' not in new_date:
            new_date = decodificar_fecha(new_date)
        
        if len(new_date) < 14:
            new_date = new_date + ' 00:00'
        elif len(new_date) > 16:
            new_date = new_date[:16]
        
        date_format = datetime.strptime(new_date, "%d/%m/%Y %H:%M")
        df_transform.loc[i_max, "fechas_horas_del_maximo"] = date_format
        i_max += 1

    i_min = 0
    for date_max in df_transform["fechas_horas_del_minimo"]:
        date = str(date_max)

        if '-' in date:
            guion = date.find('-')
            new_date = date[:guion-1]
        else:
            new_date = date

        if '/' not in new_date:
            new_date = decodificar_fecha(new_date)
        
        if len(new_date) < 14:
            new_date = new_date + ' 00:00'
        elif len(new_date) > 16:
            new_date = new_date[:16]
        
        date_format = datetime.strptime(new_date, "%d/%m/%Y %H:%M")
        df_transform.loc[i_min, "fechas_horas_del_minimo"] = date_format
        i_min += 1

    df_transform["fechas_horas_del_maximo"] = pd.to_datetime(df_transform["fechas_horas_del_maximo"])
    df_transform["fechas_horas_del_minimo"] = pd.to_datetime(df_transform["fechas_horas_del_minimo"])

    #df_transform.to_csv(raw_data_transformed, encoding='utf_8_sig', sep=';', index=False)
    return df_transform

def load_data():
    """
    Función encargada de subir los datos a la base de datos.
    """
    df = transform_data()
    print("Inicio del modelado")

    # Tabla Dim_Estacion
    df_dim_estacion = df[["autoridad_ambiental", "estacion", "latitud", "longitud","nombre_del_departamento", "nombre_del_municipio", "tipo_de_estacion", "ubicacion"]].drop_duplicates().reset_index(drop=True)
    df_dim_estacion["id_estacion"] = df_dim_estacion.index + 1

    #Tabla Dim_Variable
    df_dim_variable = df[["variable", "unidades"]].drop_duplicates().reset_index(drop=True)
    df_dim_variable["id_variable"] = df_dim_variable.index + 1

    #Tabla Dim_Tiempo
    df_dim_tiempo = pd.DataFrame({'fechas_horas_del_maximo':df["fechas_horas_del_maximo"].drop_duplicates()})
    df_dim_tiempo["id_tiempo"] = df_dim_tiempo.index + 1
    df_dim_tiempo['fecha'] = df_dim_tiempo['fechas_horas_del_maximo'].dt.date
    df_dim_tiempo['hora'] = df_dim_tiempo['fechas_horas_del_maximo'].dt.time
    df_dim_tiempo['dia_semana'] = df_dim_tiempo['fechas_horas_del_maximo'].dt.day_name()
    df_dim_tiempo['mes'] = df_dim_tiempo['fechas_horas_del_maximo'].dt.month
    df_dim_tiempo['anio'] = df_dim_tiempo['fechas_horas_del_maximo'].dt.year

    #Tabla hechos
    df_fact = pd.merge(df, df_dim_estacion, on=["autoridad_ambiental", "estacion", "latitud", "longitud","nombre_del_departamento", "nombre_del_municipio", "tipo_de_estacion", "ubicacion"])
    df_fact = pd.merge(df_fact, df_dim_variable, on=["variable", "unidades"])
    df_fact = pd.merge(df_fact, df_dim_tiempo, on=["fechas_horas_del_maximo"])
    print(df_fact.columns)

    #Tabla hechos mediciones
    df_fact_mediciones = df_fact[["id_estacion", "id_variable", "id_tiempo","representatividad_temporal", "excedencias_limite_actual", "minimo", "promedio", "mediana", "percentil_98", "maximo"]]
    df_fact_mediciones = df_fact_mediciones.reset_index(drop=True)
    df_fact_mediciones['id_medicion'] = df_fact_mediciones.index + 1

    print("Modelado completo. Tablas listas para cargar")

    #Carga de los datos a POSTGRESQL:

    try:
        # El parámetro if_exists='replace' borrará y reemplazará la tabla si ya existe.
        # En un entorno productivo, se usaría 'append' con una lógica para evitar duplicados.
        df_dim_estacion.to_sql('dim_estacion', engine, if_exists='replace', index=False)
        df_dim_variable.to_sql('dim_variable', engine, if_exists='replace', index=False)
        # Solo cargamos las columnas relevantes de la dimensión de tiempo
        df_dim_tiempo[['id_tiempo', 'fecha', 'hora', 'dia_semana', 'mes', 'anio']].to_sql('dim_tiempo', engine, if_exists='replace', index=False)
        df_fact_mediciones.to_sql('fact_mediciones', engine, if_exists='replace', index=False)
        print("¡Carga de datos completada exitosamente!")
    except Exception as e:
        print(f"Error durante la carga de datos: {e}")

if __name__ == "__main__":
    load_data()
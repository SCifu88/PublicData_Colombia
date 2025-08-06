# Monitor de Calidad del Aire en Ciudades Colombianas

![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)
![Pandas](https://img.shields.io/badge/Pandas-2.x-brightgreen.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13-blue.svg)
![Docker](https://img.shields.io/badge/Docker-20.10%2B-blue.svg)
![Apache Airflow](https://img.shields.io/badge/Apache%20Airflow-2.x-brightgreen.svg)

## 📄 Resumen del Proyecto

Este proyecto implementa un pipeline de datos (ETL) completo y automatizado para monitorear la calidad del aire en varias ciudades de Colombia. El pipeline extrae datos públicos del portal de datos abiertos del gobierno, los procesa para asegurar su calidad y consistencia, y los carga en una base de datos PostgreSQL, dejando la información lista para análisis y visualización.

El objetivo principal es demostrar habilidades clave en ingeniería de datos, incluyendo la ingesta de datos desde APIs, su transformación y limpieza, el modelado para almacenamiento y la orquestación de flujos de trabajo automatizados.

## 🏛️ Arquitectura del Pipeline

El flujo de datos sigue una arquitectura ETL clásica, orquestada para ejecutarse de forma periódica y automática.



## 🛠️ Stack Tecnológico

* **Lenguaje de Programación:** Python 3.9
* **Procesamiento de Datos:** Pandas
* **Base de Datos:** PostgreSQL
* **Contenerización:** Docker y Docker Compose (para crear un entorno reproducible)
* **Orquestación de Pipeline:** Apache Airflow (ejecutado vía Docker)
* **Conexión a la BD:** SQLAlchemy

## 📊 Fuente de Datos

Los datos son obtenidos del dataset **"Datos de las estaciones de monitoreo de calidad del aire del IDEAM"**, disponible en el Portal de Datos Abiertos de Colombia.

* **Enlace al Dataset:** [https://www.datos.gov.co/resource/ysq6-ri4e.json](https://www.datos.gov.co/resource/ysq6-ri4e.json)

## 🚀 Cómo Empezar

Sigue estos pasos para levantar el entorno y ejecutar el pipeline.

### Prerrequisitos

* Tener [Docker](https://www.docker.com/products/docker-desktop/) y Docker Compose instalados.
* Tener Python 3.9 o superior instalado en tu máquina local.

### Instalación y Ejecución

1.  **Clona el repositorio:**
    ```bash
    git clone [URL-DE-TU-REPOSITORIO]
    cd proyecto-calidad-aire
    ```

2.  **Levanta la base de datos con Docker:**
    ```bash
    docker-compose up -d
    ```
    Esto iniciará un contenedor de PostgreSQL con la configuración definida en `docker-compose.yml`.

3.  **Crea un entorno virtual e instala las dependencias:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```
    *(Nota: deberás crear un archivo `requirements.txt` con las librerías que uses: `pandas`, `requests`, `sqlalchemy`, `psycopg2-binary`, etc.)*

4.  **Ejecuta el pipeline manualmente (primer paso):**
    ```bash
    python scripts/extract_air_quality.py
    # Próximamente: python scripts/transform_load_air_quality.py
    ```

## 📁 Estructura del Repositorio

```
.
├── data/                  # Almacena los datos generados
│   ├── raw/
│   └── processed/
├── dags/                  # Contiene los DAGs de Apache Airflow
├── scripts/               # Scripts individuales para ETL
│   ├── extract_air_quality.py
│   └── transform_load_air_quality.py
├── .gitignore             # Archivos y carpetas a ignorar por Git
├── docker-compose.yml     # Define los servicios de Docker (Postgres, Airflow)
├── Dockerfile             # (Opcional) Para construir imágenes personalizadas
├── README.md              # Esta descripción
└── requirements.txt       # Dependencias de Python
```

## 🔮 Futuras Mejoras

* [ ] Implementar un sistema de tests de calidad de datos con `Great Expectations`.
* [ ] Migrar la infraestructura a un proveedor Cloud (AWS, GCP, Azure).
* [ ] Crear un dashboard de visualización en tiempo real con Streamlit o Dash.
* [ ] Escalar el procesamiento de datos utilizando Spark en lugar de Pandas.

## 👤 Autor

* **Santiago Cifuentes Diaz**
* **LinkedIn:**
* **Portafolio Web:**

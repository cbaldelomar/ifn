# Indicadores Financieros de Nicaragua

Este proyecto en **Python** descarga, procesa y almacena información de indicadores financieros relevantes de varias instituciones de Nicaragua.

El objetivo del proyecto es consolidar esta información en una base de datos centralizada para facilitar el análisis y la visualización de los datos.

## Requisitos previos

- Python 3.12 o superior.
- SQL Server instalado y configurado.
- Asegúrate de tener acceso a internet para descargar los datos de los orígenes.

## Orígenes procesados
- Banco Central de Nicaragua (BCN)
- Superintendencia de Bancos (SIBOIF)
- Comisión Nacional de Microfinanzas (CONAMI)

## Indicadores procesados

### BCN
- Ver lista en `src/bcn/reportes.py`

### SIBOIF y CONAMI
- Estado de Situación Financiera (ESF): Activo, Pasivo, Patrimonio.

## Instalar dependencias
```bash
pip install -r requirements.txt
```

## Base de datos

El nombre de la base de datos usada es `IndicadoresDW`.

### Crear base de datos

El script para crear la base de datos se encuentra en `/database`.

Puedes ejecutar el script desde **SSMS** o bien desde la terminal:

- **Usando autenticación de Windows**
```powershell
sqlcmd -S [servidor] -d master -E -i ./database/create_database.sql
```

- **Usando usuario y contraseña en Windows/Linux/MacOS**
```bash
sqlcmd -S [servidor] -d master -E -i ./database/create_database.sql
```

> Asegúrate de que tu servidor de SQL Server esté corriendo y de que tienes los permisos necesarios para crear bases de datos. El script configurará las tablas y objetos iniciales necesarios para almacenar y actualizar los datos procesados.

### Conexión a base de datos

Las credenciales que se usan para conectarse a la base de datos desde Python están en `.env`

Estas son configuradas desde el script de creación de la base de datos.

## Ejecución

El proyecto permite procesar los indicadores financieros de varias maneras. Dependiendo de los parámetros que pases, puedes procesar todos los periodos, el último periodo disponible, o un periodo específico.

- **Procesar todos los periodos**

```bash
py src/procesar.py todos
```

- **Último periodo disponible**
```bash
py src/procesar.py
```

- **Periodo especifico (yyyymm)**
```bash
py src/procesar.py 202403
```
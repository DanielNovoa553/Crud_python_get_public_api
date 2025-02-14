import psycopg2
from psycopg2 import OperationalError

def connectdb():
    """
    Function to connect to database webdinarZappa
    Returns: connection object or error message if connection fails
    """
    try:
        connection = psycopg2.connect(
            host='localhost',
            user='postgres',
            password='Inicio01',
            dbname='banpay'
        )
        if connection:
            print("Conexión exitosa")
        return connection

    except OperationalError as e:
        print("Error al conectar con la base de datos, detalle del error: ", e)
        return e


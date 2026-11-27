
import mysql.connector

def get_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="charan",
        database="inventory_management"
    )

    return connection

from database import get_connection

try:
    with get_connection() as connection: # connection connects you to database
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")  #cursor sends SQL commands
            database_version = cursor.fetchone()

            print("Connected successfully!")
            print(database_version[0])

except Exception as error:
    print("Database connection failed:")
    print(error)
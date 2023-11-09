import oracledb

def check_DB_connection():
    try:
        connection = oracledb.connect(user="user", password="password", dsn="dsn", mode=oracledb.SYSDBA)
        print("Connection successful")
        cur = connection.cursor()
        cur.execute("SELECT sum(bytes) FROM dba_data_files")
        storage_size = cur.fetchall()
        print("Storage size of the DBF:", storage_size[0][0])
        cur.close()
        connection.close()

    except oracledb.DatabaseError as e:
        error, = e.args
        print(f"Error code: {error.code}, Error message: {error.message}")

check_DB_connection()
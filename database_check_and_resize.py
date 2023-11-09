import shutil
import smtplib
import os
import psutil


def check_and_resize_databas(user, password, dsn, threshold_percentage=90):
    # Create connection
    connection = cx_Oracle.connect(user, password, dsn)
    cursor = connection.cursor()
    # Query to get total and used space in MB
    query_total = """
        SELECT SUM(BYTES)/1024/1024 AS MB
        FROM DBA_DATA_FILES;
        """
    query_used = """
        SELECT SUM(BYTES)/1024/1024 AS MB
        FROM DBA_SEGMENTS;
        """
    
    cursor.execute(query_total)
    total_size=cursor.fetchone()[0]

    cursor.execute(query_used)
    used_size = cursor.fetchone()[0]

    # Calculate percentage
    percentage_used = (used_size/total_size)*100

    if percentage_used > threshold_percentage:

        # Get tablespaces above with 90% usage

        tablespaces_query = """
            SELECT TABLESPACE_NAME,
                100 * (USED_SPACE / TABLESPACE_SIZE) AS PERCENTAGE_USED
                FROM DBA_TABLESPACE_USAGE_METRICS
                WHERE 100 * (USED_SPACE / TABLESPACE_SIZE) > :threshold
                """
        
        cursor.execute(tablespaces_query, threshold=threshold_percentage)
        tablespaces_to_expand = cursor.fetchall()

        for tablespace, percentage in tablespaces_to_expand:
            print(f"Tablespace {tablespace} is {percentage:.2f}% full.")
            # Resizing the largest datafile

            datafile_query = """
                SELECT FILENAME, BYTES
                FROM DBA_DATA_FILES
                WHERE TABLESPACE_NAME = :tablespace_name
                ORDER BY BYTES DESC
                FETCH FIRST 1 ROW ONLY
                """
            
            cursor.execute(datafile_query, tablespace_name=tablespace)
            file_name, file_size = cursor.fetchone()

            new_size = file_size + 1024 * 1024 * 200
            resize_query = f"ALTER DATABASE  DATAFILE '{file_name}' RESIZE {new_size}"
            cursor.execute(resize_query)
            print(f"Resized datafile {file_name} to {new_size/(1024*1024)} MBs.")
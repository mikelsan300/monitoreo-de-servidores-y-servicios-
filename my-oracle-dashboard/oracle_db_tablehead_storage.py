import oracledb
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import wmi
import logging
import pythoncom

server_credentials = {
    "server1": {"user": "user1", "password": "password1", "dsn": "dsn1"},
    "server2": {"user": "user2", "password": "password2", "dsn": "dsn2", "conn_user": "connuser", "conn_password": "connpassword"},
}
app = Flask(__name__)
CORS(app)
@app.route('/get_tablespace_storage', methods=['GET'])




def get_tablespace_storage():
    
    server = request.args.get('server', 'server')
    credentials =server_credentials.get(server, {})

    connection = oracledb.connect(
        user=credentials.get("user"),
        password=credentials.get("password"),
        dsn=credentials.get("dsn"),
        mode=oracledb.SYSDBA,
    )
    print("Connection successful")
    cur = connection.cursor()

    query = """
    SELECT
        tbs_info.tablespace_name,
        tbs_info."Size MB",
        seg_info."Used MB",
        fs_info."Free MB",
        ROUND((seg_info."Used MB" / tbs_info."Size MB") * 100, 2) "Percentage Used",
        tbs_info."Tablespace Status"
    FROM
        (
            SELECT
                df.tablespace_name,
                ROUND(SUM(df.bytes) / 1024 / 1024) "Size MB",
                ts.STATUS "Tablespace Status"
            FROM
                dba_data_files df
            JOIN
                dba_tablespaces ts ON df.tablespace_name = ts.tablespace_name
            GROUP BY
                df.tablespace_name, ts.STATUS
        ) tbs_info
    LEFT JOIN
        (
            SELECT
                tablespace_name,
                ROUND(SUM(bytes) / 1024 / 1024) "Used MB"
            FROM
                dba_segments
            GROUP BY
                tablespace_name
        ) seg_info ON tbs_info.tablespace_name = seg_info.tablespace_name
    LEFT JOIN
        (
            SELECT
                tablespace_name,
                ROUND(SUM(bytes) / 1024 / 1024) "Free MB"
            FROM
                dba_free_space
            GROUP BY
                tablespace_name
        ) fs_info ON tbs_info.tablespace_name = fs_info.tablespace_name
    ORDER BY
        tbs_info.tablespace_name


        """
    
    cur.execute(query)
    results = cur.fetchall()

    data = []
    for row in results:
        data.append({
            "TablespaceName": row[0],
        "SizeMB": row[1],
        "UsedMB": row[2],
        "FreeMB": row[3],
        "PctUsed": row[4],
        "Status": row[5]
        })

    cur.close() 
    connection.close()
    return jsonify(data)

@app.route('/add_storage/<tablespace_name>', methods=['POST'])

def add_storage(tablespace_name):
    server = request.args.get('server', 'server')
    credentials = server_credentials.get(server, {})
    connection = oracledb.connect(
         user=credentials.get("user"),
         password=credentials.get("password"),
         dsn=credentials.get("dsn"),
         mode=oracledb.SYSDBA,
         )
    try:
    # Get the current size of the datafile(s) associated with the tablespace
        cur = connection.cursor()
        cur.execute(f"""
            SELECT df.AUTOEXTENSIBLE, df.MAXBYTES
            FROM DBA_DATA_FILES df
            WHERE df.TABLESPACE_NAME = '{tablespace_name}'
            ORDER BY df.FILE_ID DESC
            FETCH FIRST 1 ROW ONLY
                    """)
        res = cur.fetchone()
        autoextensible = res[0]
        maxbytes = res[1]

        cur.execute(f"""
                    SELECT COUNT(*)
                    FROM DBA_DATA_FILES
                    WHERE TABLESPACE_NAME = '{tablespace_name}'
                    """)
        count_result = cur.fetchone()
        count = count_result[0]

        cur.execute(f"""
            SELECT df.FILE_NAME, df.BYTES, df.MAXBYTES
            FROM DBA_DATA_FILES df
            WHERE df.TABLESPACE_NAME = '{tablespace_name}'
        """)
        

        
        results = cur.fetchall()
        for row in results:
            file_name = row[0]
            current_size = row[1] //1024//1024
            max_file_size = row[2] //1024//1024
            max_file_size = max_file_size 
            

            # Calculate the new size (110% of current)
            new_size = int(current_size * 1.05)
            if new_size >= max_file_size and count > 1:
                count = count - 1
                print(count)
                print(current_size)
                print(max_file_size)
            elif new_size >= max_file_size:
                #Add a new datafile 

                print("Datafila should have been added")
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                new_datafile_name = file_name.replace(".DBF", f"_new_{timestamp}.DBF")
                if autoextensible == 'YES':
                    cur.execute(f"""
                        ALTER TABLESPACE {tablespace_name} ADD DATAFILE '{new_datafile_name}' SIZE 100M AUTOEXTEND ON MAXSIZE {maxbytes}
                        """)
                else:
                    cur.execute(f"""
                    ALTER TABLESPACE {tablespace_name} ADD DATAFILE '{new_datafile_name}' SIZE 100M
                        """)
                print("did I get here?")
                
            else:
            
            # Resize the datafile
               
                print(current_size)
                cur.execute(f"""
                ALTER DATABASE DATAFILE '{file_name}' RESIZE {new_size}M
                """)
                print(new_size)
        
        cur.close()
        connection.close()
        
        return jsonify({"success": True, "message": f"Storage increased by 10% for {tablespace_name}"})
    except Exception as e:
        connection.close()
        return jsonify({"success": False, "message":str(e)})
    


#@app.route('/get_server_status', methods=['GET'])
#def get_server_status():
    #print("we trying")
    #server = request.args.get('server', 'server')
    #credentials =server_credentials.get(server, {})

    #connection = oracledb.connect(
        #user=credentials.get("user"),
        #password=credentials.get("password"),
        #dsn=credentials.get("dsn"),
        #mode=oracledb.SYSDBA,
    #)

    #print("here")
    
    #cur = connection.cursor()

    # This query is just a placeholder. Replace with the actual query to get instance status.
    #query = """SELECT INSTANCE_NAME, STATUS FROM V$INSTANCE"""

    #cur.execute(query)
    #results = cur.fetchall()
    #server_status = [{"instance_name": row[0], "status": row[1]} for row in results]

    #cur.close()
    #connection.close()

    #return jsonify(server_status)


@app.route('/get_windows_services', methods=['GET'])
def get_windows_services():
    pythoncom.CoInitialize()
    print("starting get services")
    server = request.args.get('server')
    print(server)
    if not server:
        return jsonify({'error': 'Server parameter is missing'})
    print("server acquired")
    credentials = server_credentials.get(server, {})
    if not credentials:
        return jsonify({'error': 'No credentials found for the specified server'})
    print("credentials acquired")

    try:

        if server == 'server1':
            conn=wmi.WMI()
        else:
            # Establish a WMI connection to the remote server
            conn = wmi.WMI(computer=credentials.get("dsn").split(':')[0], user=credentials.get("conn_user"), password=credentials.get("conn_password"))
        print("connection acquired")
        # Specify the service names you want to check
        service_names = ["ModulabWildfly-node1", "OracleOraDB12Home1TNSListener", "OracleServiceMGOLD", "OracleVssWriterMGOLD", "RtkBtManServ"]  # Replace with your service names
        print("service names acquired")
        # Get the statuses of the specified services
        services = []
        for service_name in service_names:
            for service in conn.Win32_Service(Name=service_name):
                print(services)
                services.append({"Nombre": service_name, "estado": service.State})
        print("services acquired")

        print(services)
        return jsonify({'services': services})
    
    except wmi.x_wmi as wmi_error:
        logging.exception("WMI error occurred")
        return jsonify({'error': str(wmi_error)})
    
    except Exception as e:
        logging.exception("An unexpected error occurred")
        return jsonify({'error': str(e)})
    
    
    finally:
        pythoncom.CoUninitialize()

    
if __name__ == "__main__":
    app.run(debug=True)


import psycopg2
import os
import logging
from flask import Flask, render_template

## Global Variables
trg_db_creds = {}
src_db_creds = {}
app = Flask(__name__)

def GetSecrets(secret_id: str,version_id="latest"):
    """ This function gets the DB credentials from secret manager"""
    try:
        from google.cloud import secretmanager
        client = secretmanager.SecretManagerServiceClient()
        name = f"{secret_id}/versions/{version_id}"
        response = client.access_secret_version(name=name)
        logging.info(f"Found secret {secret_id} and returning value")
        return response.payload.data.decode('UTF-8')
    except Exception as e:
        logging.error(f"Unable to find or retrieve the secret {secret_id}")
        logging.error(e)

def ConfigureCloudLogging():
        """ This function imports and configured the google cloud logging sdk """
        import google.cloud.logging
        # Instantiates a client
        client = google.cloud.logging.Client()
        client.setup_logging()
        logging.info("Using Cloud Loggging")

def BuildConnection(DBInfo: dict):
    """ This function builds and returns a PostGres Connection"""
    logging.info(f"Building connection with the infO: {DBInfo}")
    conn = None
    try:
        conn = psycopg2.connect(database=DBInfo["db_name"],
                            host=DBInfo["db_host"],
                            user=DBInfo["db_user"],
                            password=DBInfo["db_password"],
                            port=5432,
                            connect_timeout=3)
        logging.info("Built DB Connection")
    except Exception as e:
        logging.error(f"Unable to connect to the DB")
        logging.error(e)

    return conn

def FetchAllData(conn):
    """ This function lists all the tables in the target DB and returns list """
    database_info = {}
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
        table_list = []
        for row in cursor.fetchall():
            table_list.append(row[0])

        for aTable in table_list:
            # Lookup all the rows
            cursor = conn.cursor()
            postgreSQL_select_Query = f"select * from {aTable}"
            cursor.execute(postgreSQL_select_Query)
            logging.info(f"Gathering table data for {aTable}")          
            database_info[aTable] = cursor.fetchall()
        # Return Results
        return database_info
    except Exception as e:
        logging.error(f"Error while fetching data from PostgreSQL")
        logging.error(e)


@app.route("/")
def hello_world():
    """ Return Results"""
    # Connect to the Source DB
    logging.info("Source Data:")
    srcConn = BuildConnection(DBInfo=src_db_creds)
    srcData = FetchAllData(conn=srcConn)
    logging.info(srcData)
    
    # Connect to the Target DB
    logging.info("Target Data:")
    trgConn = BuildConnection(DBInfo=trg_db_creds)
    trgData = FetchAllData(conn=trgConn)
    logging.info(trgData)

    # Render Page
    return render_template('index.html', src_db="CloudSQL", trg_db="AlloyDB", src_data=srcData, trg_data=trgData, src_len=len(srcData), trg_len=len(trgData))

if __name__ == "__main__":
    # First check if running in google cloud
    if os.getenv('is_gcp') is not None:
        ConfigureCloudLogging()
    else:
        logging.info("Using local logs")


    # Find Source DB Creds
    if os.getenv('src_secret_id') is not None:
        # Check for Secret Hosting
        raw_secret = GetSecrets(secret_id=os.getenv('src_secret_id'))
        src_db_creds = dict(map(lambda x: x.split(':'), raw_secret.split(',')))
        logging.info("Pulled Source DB connection values from Secret Manager")
    elif os.getenv('src_db_user') is not None:
        # Check for values in Env
        src_db_creds["src_db_user"] = os.getenv('src_db_user')
        src_db_creds['src_db_password'] = os.getenv('src_db_password')
        src_db_creds['src_db_name'] = os.getenv('src_db_name')
        src_db_creds['src_db_host'] = os.getenv('src_db_host')
        logging.info("Pulled Source DB Connection values from Environment")
    else:
        # Fail Hard
        logging.error("Unable to find Source DB Connection Values")
        exit(1)

    logging.info(src_db_creds)


    # Find Source DB Creds
    if os.getenv('trg_secret_id') is not None:
        # Check for Secret Hosting
        raw_secret = GetSecrets(secret_id=os.getenv('trg_secret_id'))
        trg_db_creds = dict(map(lambda x: x.split(':'), raw_secret.split(',')))
        logging.info("Pulled Target DB connection values from Secret Manager")
    elif os.getenv('db_user') is not None:
        # Check for values in Env
        trg_db_creds["trg_db_user"] = os.getenv('trg_db_user')
        trg_db_creds['trg_db_password'] = os.getenv('trg_db_password')
        trg_db_creds['trg_db_name'] = os.getenv('trg_db_name')
        trg_db_creds['trg_db_host'] = os.getenv('trg_db_host')
        logging.info("Pulled Target DB Connection values from Environment")
    else:
        # Fail Hard
        logging.error("Unable to find Target DB Connection Values")
        exit(1)
    logging.info(trg_db_creds)

    # Start App
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

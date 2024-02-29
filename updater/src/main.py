import psycopg2
import os
import logging
from random import randint, choice
from time import sleep

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

def ListTables(conn):
    """ This function lists all the tables in the target DB and returns list """
    cursor = conn.cursor()
    cursor.execute("select relname from pg_class where relkind='r' and relname !~ '^(pg_|sql_)';")
    table_list = []
    for row in cursor.fetchall():
        print(row[0])
        table_list.append(row[0])
    return table_list

def UpdateTable(conn, table_name: str):
    """ This function will randomly update a row in a table"""
    print(f"Update: {table_name}")

def InsertIntoTable(conn, table_name: str):
    """ This function will randomly insert a new row in a table"""
    print(f"Insert: {table_name}")

def DeleteFromTable(conn, table_name: str):
    """ This function will randomly delete a row in a table"""
    print(f"Delete: {table_name}")


if __name__ == "__main__":
    # First check if running in google cloud
    if os.getenv('is_gcp') is not None:
        ConfigureCloudLogging()
    else:
        logging.info("Using local logs")

    
    # Next Read the environment variables for TargetDB
    project = os.getenv('project_id')

    # Db Connection values
    db_creds = {}

    # Find DB Creds
    if os.getenv('secret_id') is not None:
        # Check for Secret Hosting
        raw_secret = GetSecrets(secret_id=os.getenv('secret_id'))
        db_creds = dict(map(lambda x: x.split(':'), raw_secret.split(',')))
        logging.info("Pulled DB connection values from Secret Manager")
    elif os.getenv('db_user') is not None:
        # Check for values in Env
        db_creds["db_user"] = os.getenv('db_user')
        db_creds['db_password'] = os.getenv('db_password')
        db_creds['db_name'] = os.getenv('db_name')
        db_creds['db_host'] = os.getenv('db_host')
        logging.info("Pulled DB Connection values from Environment")
    else:
        # Fail Hard
        logging.error("Unable to find DB Connection Values")
        exit(1)

    logging.debug(db_creds)


    # Next Step is to update the source DB
    myConn = None
    while True:
        # First loop should build connectoin
        if myConn is None:
            myConn = BuildConnection(DBInfo=db_creds)
            if myConn is None:
                # Give up here
                exit(1)

        # Select List of Tables
        tableList = ListTables(conn=myConn)
        thisTable = choice(tableList)
        logging.debug(tableList)
        
        # Pick a random task:
        task = randint(1,3)
        if task == 1:
            # Randomly update
            UpdateTable(conn=myConn, table_name=thisTable)
        elif task == 2:
            # Randomly delete
            DeleteFromTable(conn=myConn, table_name=thisTable)
        else:
            # Randomly insert
           InsertIntoTable(conn=myConn, table_name=thisTable)

        # Sleep a random number of seconds (between 1 and 5)
        sleep(randint(1,5))
import psycopg2
import os
import logging

def GetSecrets(secret_id: str, project_id: str, version_id="latest"):
    """ This function gets the DB credentials from secret manager"""
    from google.cloud import secretmanager
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(name=name)
    return response.payload.data.decode('UTF-8')


if __name__ == "__main__":
    # First check if running in google cloud
    if os.getenv('CLOUD_RUN_JOB') is not None:
        # Imports the Cloud Logging client library
        import google.cloud.logging
        # Instantiates a client
        client = google.cloud.logging.Client()
        client.setup_logging()
    
    # Next Read the environment variables for TargetDB
    project = os.getenv('project_id')

    # PUll 
    if os.getenv('secret_id') is not None:
        raw_secret = GetSecrets(secret_id=os.getenv('secret_id'), project_id=project)
        db_values = raw_secret.split(",")



    

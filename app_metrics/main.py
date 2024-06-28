from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google.cloud import bigquery
from google.oauth2 import service_account
import os

app = FastAPI()

# Path to your service account key file
key_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "key.json")

# Create credentials object
credentials = service_account.Credentials.from_service_account_file(key_path)

# Initialize BigQuery client with credentials
client = bigquery.Client(credentials=credentials, project=credentials.project_id)

# Define BigQuery dataset and table
dataset_id = 'your_dataset'
table_id = 'metric_0001'
project_id = 'yalp-tcefrep'

class PlayerMetricsRequest(BaseModel):
    player_id: str

@app.post("/get_metric/")
async def get_metric(request: PlayerMetricsRequest):
    query = f"""
        SELECT metric_0001
        FROM `{project_id}.{dataset_id}.{table_id}`
        WHERE player_id = @player_id
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("player_id", "STRING", request.player_id)
        ]
    )
    
    try:
        query_job = client.query(query, job_config=job_config)
        results = query_job.result()
        
        metrics = [row.metric_0001 for row in results]
        
        if not metrics:
            raise HTTPException(status_code=404, detail="Metric not found")
        
        return {"player_id": request.player_id, "metric_0001": metrics[0]}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run the server with: uvicorn app_metrics.main:app --reload

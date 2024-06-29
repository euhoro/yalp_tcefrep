from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from google.cloud import bigquery
from google.oauth2 import service_account
import os
import time
import uvicorn
import platform
import logging
from fastapi.responses import JSONResponse



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(debug=True)

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    if isinstance(exc, bigquery.exceptions.BadRequest):
        logger.error(f"BigQuery BadRequest: {exc.errors}")
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error", "details": str(exc)}
    )

# Determine if we are in a development environment
IS_DEV_ENV = os.getenv('IS_DEV', 'false').lower() == 'true'
print(IS_DEV_ENV)

IS_DEV = (platform.system() == 'Linux' and platform.release() == '5.15.0-ubuntu') or (os.getenv('USER') == 'eu')
if IS_DEV:
    # Path to your service account key file
    key_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "key.json")

    # Create credentials object
    credentials = service_account.Credentials.from_service_account_file(key_path)

    # Initialize BigQuery client with credentials
    client = bigquery.Client(credentials=credentials, project=credentials.project_id)
else:
    client = bigquery.Client()

# Define BigQuery dataset and table
dataset_id = 'your_dataset'
table_id = 'metric_0001'
project_id = 'yalp-tcefrep'  # Replace with your actual project ID

class PlayerMetricsRequest(BaseModel):
    player_id: str

@app.get("/test_bigquery")
async def test_bigquery():
    try:
        query = "SELECT 1"
        query_job = client.query(query)
        results = query_job.result()
        for row in results:
            return {"result": row[0]}
    except Exception as e:
        logger.error(f"BigQuery test failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    

# @app.post("/get_metric/")
# async def get_metric(request: PlayerMetricsRequest):
    
#     logger.info(f"Received request for player_id: {request.player_id}")

#     start_time = time.time()  # Start timing the whole request
#     query = f"""
#         SELECT metric_0001
#         FROM `{project_id}.{dataset_id}.{table_id}`
#         WHERE player_id = @player_id
#     """
#     job_config = bigquery.QueryJobConfig(
#         query_parameters=[
#             bigquery.ScalarQueryParameter("player_id", "STRING", request.player_id)
#         ]
#     )
    
#     try:
#         logger.info(f"Received request for player_id: {request.player_id}")

#         query_start_time = time.time()  # Start timing the query
#         query_job = client.query(query, job_config=job_config)
#         logger.info("Query executed, fetching results")
#         results = query_job.result()
#         query_time = time.time() - query_start_time  # Calculate query time
#         logger.info(f"Query results: {results}")
#         metrics = [row.metric_0001 for row in results]
        
#         if not metrics:
#             raise HTTPException(status_code=404, detail="Metric not found")
        
#         total_time = time.time() - start_time  # Calculate total request time
        
#         return {
#             "player_id": request.player_id,
#             "metric_0001": metrics[0],
#             "query_time": query_time,
#             "total_time": total_time
#         }
    
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
    

@app.post("/get_metric/")
async def get_metric(request: PlayerMetricsRequest):
    logger.info(f"Received request for player_id: {request.player_id}")
    start_time = time.time()

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
        logger.info(f"Executing BigQuery query: {query}")
        query_start_time = time.time()
        query_job = client.query(query, job_config=job_config)
        logger.info("Query job created, waiting for results...")
        results = query_job.result()
        query_time = time.time() - query_start_time
        logger.info(f"Query completed in {query_time} seconds")

        metrics = [row.metric_0001 for row in results]
        logger.info(f"Query returned {len(metrics)} results")

        if not metrics:
            logger.warning(f"No metrics found for player_id: {request.player_id}")
            raise HTTPException(status_code=404, detail="Metric not found")

        total_time = time.time() - start_time

        response = {
            "player_id": request.player_id,
            "metric_0001": metrics[0],
            "query_time": query_time,
            "total_time": total_time
        }
        logger.info(f"Returning response: {response}")
        return response

    except Exception as e:
        logger.error(f"Error in get_metric: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Middleware to add processing time to response headers
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Run the server with: uvicorn app_metrics.main:app --reload

# if __name__ == "__main__":
#     uvicorn.run(app, host="127.0.0.1", port=8000)
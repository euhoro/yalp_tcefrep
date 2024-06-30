from functools import wraps

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

ALL_METRICS = ['avg_price_10',
               'last_weighted_daily_matches_count_10_played_days',
               'active_days_since_last_purchase',
               'score_perc_50_last_5_days',
               'country']

version = 'v.1.1.0'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(debug=True)

client = None


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    if isinstance(exc, bigquery.exceptions.BadRequest):
        logger.error(f"BigQuery BadRequest: {exc.errors}")
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error", "details": str(exc)}
    )


def initialize_bigquery_client():
    global client
    if client is None:
        IS_DEV = (platform.system() == 'Linux' and platform.release() == '5.15.0-ubuntu') or (os.getenv('USER') == 'eu')
        IS_DEV = True  # or set this based on your actual conditions
        print('is_dev', IS_DEV)
        if IS_DEV:
            # Path to your service account key file
            key_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "key.json")

            # Create credentials object
            credentials = service_account.Credentials.from_service_account_file(key_path)

            # Initialize BigQuery client with credentials
            client = bigquery.Client(credentials=credentials, project=credentials.project_id)
        else:
            client = bigquery.Client()
    return client


# Define BigQuery dataset and table
dataset_id = 'your_dataset'
table_id = 'app_user_panel'
project_id = 'yalp-tcefrep'  # Replace with your actual project ID


# df = df[df['player_id'] == '6671adc2dd588a8bda035feb']
# country
class PlayerMetricsRequest(BaseModel):
    player_id: str
    metric_name: str


@app.get("/version")
async def get_version():
    return version


@app.get("/metrics")
async def get_metrics():
    return ALL_METRICS


@app.get("/test_bigquery")
async def test_bigquery():
    try:
        client = initialize_bigquery_client()
        query = "SELECT 1"
        query_job = client.query(query)
        results = query_job.result()
        for row in results:
            return {"result": row[0]}
    except Exception as e:
        logger.error(f"BigQuery test failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# In-memory cache (dictionary)
cache = {}


def cache_check(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # player_id = kwargs.get('player_id')
        # metric_name = kwargs.get('metric_name')
        player_id = args[0]
        metric_name = args[1]
        cache_key = f"{player_id}_{metric_name}"

        # Check if the result is in the cache
        if cache_key in cache:
            logger.info(f"Cache hit for {cache_key}")
            return cache[cache_key]

        logger.info(f"Cache miss for {cache_key}, fetching from BigQuery")
        result = func(*args, **kwargs)

        # Add result to cache
        cache[cache_key] = result
        logger.info(f"Added {cache_key} to cache")
        return result

    return wrapper


@cache_check
def service_get_metric(player_id, metric_name):
    client = initialize_bigquery_client()

    query = f"""
        SELECT {metric_name}
        FROM `{project_id}.{dataset_id}.{table_id}`
        WHERE player_id = @player_id
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("player_id", "STRING", player_id)
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

        # Convert rows to dictionaries
        results_dicts = [dict(row) for row in results]

        # Access column values by column name
        metrics = [row[metric_name] for row in results_dicts]
        # metrics = [row.avg_price_10 for row in results]
        logger.info(f"Query returned {len(metrics)} results")

        if not metrics:
            logger.warning(f"No metrics found for player_id: {player_id}")
            raise HTTPException(status_code=404, detail="Metric not found")

        return metrics, query_time

    except Exception as e:
        logger.error(f"Error in get_metric: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/get_metric/")
async def get_metric(request: PlayerMetricsRequest):
    logger.info(f"Received request for player_id: {request.player_id}")

    start_time = time.time()
    if request.metric_name not in set(ALL_METRICS):
        logger.warning(f"Metric not valid: {request.metric_name}")
        raise HTTPException(status_code=422, detail="Metric not valid")

    metrics, query_time = service_get_metric(request.player_id, request.metric_name)

    total_time = time.time() - start_time

    response = {
        "player_id": request.player_id,
        f"{request.metric_name}": metrics[0],
        "query_time": query_time,
        "total_time": total_time
    }
    logger.info(f"Returning response: {response}")
    return response


# Middleware to add processing time to response headers
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Run the server with: uvicorn app_metrics.main:app --reload

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

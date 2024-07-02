# Yalp Tcefrep Project

## Overview

This project provides a FastAPI service for accessing player metrics stored in Google BigQuery. It includes an in-memory caching mechanism to optimize performance by reducing the number of direct queries to BigQuery.

## Prerequisites

- [Git](https://git-scm.com/)
- [Terraform](https://www.terraform.io/)
- [Python](https://www.python.org/downloads/)
- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
- [Docker](https://www.docker.com/products/docker-desktop)

## Installation

1. **Clone the Repository:**

    ```bash
    git clone https://github.com/euhoro/yalp-tcefrep.git
    cd yalp-tcefrep
    ```

2. **Add an Admin Service Account:**

    Ensure you have the following service account with the necessary roles in your GCP project:
    
    - Email: `terraform@yalp-tcefrep.iam.gserviceaccount.com`
    - Roles:
      - Artifact Registry Administrator
      - Artifact Registry Writer
      - BigQuery User
      - Container Analysis Occurrences Viewer
      - Editor
      - Owner
      - Storage Admin

    Download the key file and place it in the root folder of the project as `key.json`.

3. **Initialize and Apply Terraform:**

    ```bash
    terraform init
    terraform apply
    ```

    This will create the `yalp_tcefrep` bucket and the necessary structure for the BigQuery table.
    This will create the api available in the gcp cloud for easy access 

4. **Setup Python Environment:**

    Create a virtual environment and activate it:

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

5. **Install Required Python Packages:**

    ```bash
    pip install -r requirements.txt
    ```

6. **Populate BigQuery Table:**

    Run the following command to populate the BigQuery table:

    ```bash
    export GOOGLE_APPLICATION_CREDENTIALS="key.json"
    python notebooks/pandas_file_to_big_query.py
    ```

7. **Build and Run Docker Container locally:**

    ```bash
    docker build -t fastapi-metrics:v1.1.0 .
    docker run -p 8080:8080 fastapi-metrics:v1.1.0
    ```

## Usage

The FastAPI service provides an endpoint to get player metrics. The service looks in the cache first and then queries BigQuery if the data is not cached. The cache is refreshed periodically.

Access the application:
   - [API Documentation](http://localhost:8080/docs)
   - [Home](http://localhost:8080/)

- **Endpoint:** `GET /get_metric/`

   - **Request Body:**
       ```json
       {
         "player_id": "6671adc2dd588a8bda0367bb",
         "metric_name": "country"
       }
       ```

   - **Response:**
       ```json
       {
         "player_id": "6671adc2dd588a8bda0367bb",
         "country": "USA",
         "query_time": 0.34,
         "total_time": 0.35
       }
       ```
     * query_time will be -1 if request reached the cache

### Design 
- [Design Documentation](https://github.com/euhoro/yalp_tcefrep/blob/main/DESIGN.md)

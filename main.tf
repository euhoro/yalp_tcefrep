provider "google" {
  credentials = file("key.json")
  project     = var.project_id
  region      = var.region
}

locals {
  service_account_key = jsondecode(file("key.json"))
  service_account_email = local.service_account_key.client_email
}

resource "google_storage_bucket" "data_bucket" {
  name          = var.project_id
  location      = "US"
  force_destroy = true
}

resource "google_storage_bucket_object" "data_files" {
  for_each = fileset("raw_data", "*.parquet")
  name     = each.value
  bucket   = google_storage_bucket.data_bucket.name
  source   = "raw_data/${each.value}"
}

resource "google_storage_bucket_object" "function_zip" {
  name   = "function-source.zip"
  bucket = google_storage_bucket.data_bucket.name
  source = data.archive_file.function_source.output_path
}

data "archive_file" "function_source" {
  type        = "zip"
  source_dir  = "notebooks"
  output_path = "./labda_source.zip"
}

resource "google_cloudfunctions_function" "pandas_to_bigquery" {
  name        = "pandas-file-to-bigquery"
  description = "A function to process pandas file and upload to BigQuery"
  runtime     = "python39"
  available_memory_mb = 256
  source_archive_bucket = google_storage_bucket.data_bucket.name
  source_archive_object = google_storage_bucket_object.function_zip.name
  trigger_http = true
  entry_point = "main"

  environment_variables = {
    "GCP_PROJECT"  = var.project_id
    "GCP_BUCKET"   = google_storage_bucket.data_bucket.name
    "FORCE_REDEPLOY" = "true"  # Trivial change to force redeployment
  }
}
resource "google_cloud_scheduler_job" "job" {
  name             = "pandas-to-bigquery-job"
  description      = "Schedule pandas to bigquery function"
  schedule         = "0 */4 * * *"
  time_zone        = "Etc/UTC"
  http_target {
    http_method = "POST"
    uri         = google_cloudfunctions_function.pandas_to_bigquery.https_trigger_url
    oidc_token {
      service_account_email = local.service_account_email
      audience = google_cloudfunctions_function.pandas_to_bigquery.https_trigger_url  # Explicitly set the audience
    }
  }
}

resource "google_cloudfunctions_function_iam_member" "invoker" {
  project        = var.project_id
  region         = var.region
  cloud_function = google_cloudfunctions_function.pandas_to_bigquery.name

  role   = "roles/cloudfunctions.invoker"
  member = "allUsers"
}


resource "google_cloud_run_service_iam_member" "allUsers" {
  service  = google_cloud_run_service.default.name
  location = google_cloud_run_service.default.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

resource "google_project_iam_member" "bigquery" {
  project = var.project_id
  role    = "roles/bigquery.user"
  member  = "serviceAccount:${google_cloud_run_service.default.template[0].spec[0].service_account_name}"
}

resource "google_project_service" "bigquery" {
  project                    = var.project_id
  service                    = "bigquery.googleapis.com"
  disable_on_destroy         = true
  disable_dependent_services = true
}

resource "google_bigquery_dataset" "dataset" {
  dataset_id = "your_dataset"
  project    = var.project_id
}

resource "google_bigquery_table" "metric_0001" {
  dataset_id = google_bigquery_dataset.dataset.dataset_id
  table_id   = "metric_0001"
  project    = var.project_id

  deletion_protection = false

  schema = <<EOF
[
  {
    "name": "player_id",
    "type": "STRING",
    "mode": "REQUIRED"
  },
  {
    "name": "metric_0001",
    "type": "FLOAT",
    "mode": "REQUIRED"
  }
]
EOF

  clustering = ["player_id"]
}

resource "google_bigquery_table" "app_user_panel" {
  dataset_id = google_bigquery_dataset.dataset.dataset_id
  table_id   = "app_user_panel"
  project    = var.project_id

  deletion_protection = false

  schema = <<EOF
[
  {
    "name": "player_id",
    "type": "STRING",
    "mode": "REQUIRED"
  },
  {
    "name": "country",
    "type": "STRING",
    "mode": "REQUIRED"
  },
  {
    "name": "avg_price_10",
    "type": "FLOAT",
    "mode": "REQUIRED"
  },
  {
    "name": "last_weighted_daily_matches_count_10_played_days",
    "type": "FLOAT",
    "mode": "REQUIRED"
  },
  {
    "name": "active_days_since_last_purchase",
    "type": "FLOAT",
    "mode": "REQUIRED"
  },
  {
    "name": "score_perc_50_last_5_days",
    "type": "FLOAT",
    "mode": "REQUIRED"
  },
  {
    "name": "update_time",
    "type": "TIMESTAMP",
    "mode": "REQUIRED"
  }
]
EOF

  clustering = ["player_id"]

  time_partitioning {
    type  = "DAY"
    field = "update_time"
  }
}

resource "google_bigquery_reservation" "bi_engine" {
  project    = var.project_id
  location   = "US"  # adjust as needed
  name       = "bi-engine-reservation"
  slot_capacity = 100  # adjust based on your needs and budget
}
#
#resource "google_bigquery_table" "metrics_view" {
#  dataset_id = google_bigquery_dataset.dataset.dataset_id
#  table_id   = "metrics_view"
#  project    = var.project_id
#
#  deletion_protection = false
#
#  view {
#    query = <<EOF
#    SELECT player_id, avg_price_10 , last_weighted_daily_matches_count_10_played_days, active_days_since_last_purchase, score_perc_50_last_5_days, country
#    FROM (
#      SELECT player_id, avg_price_10 , last_weighted_daily_matches_count_10_played_days, active_days_since_last_purchase, score_perc_50_last_5_days, country,
#             ROW_NUMBER() OVER (PARTITION BY player_id ORDER BY update_time DESC) as rn
#      FROM `${var.project_id}.${google_bigquery_dataset.dataset.dataset_id}.app_user_panel`
#    )
#    WHERE rn = 1
#    EOF
#    use_legacy_sql = false
#  }
#}

resource "google_cloud_run_service" "default" {
  name     = var.service_name
  location = var.region

  template {
    spec {
      containers {
        #image = "us-central1-docker.pkg.dev/${var.project_id}/fastapi-metrics-repo/fastapi-metrics"
        #image = "us-central1-docker.pkg.dev/yalp-tcefrep/fastapi-metrics-repo/fastapi-metrics@sha256:92fb1c4122013d50c8f777d96447743026e2d176aa7a3342bcd89f1523933af8"
        image = "us-central1-docker.pkg.dev/yalp-tcefrep/fastapi-metrics-repo/fastapi-metrics:${var.image_tag}"
        ports {
          container_port = 8080
        }

        env {
          name  = "IS_DEV"
          value = "false"
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

variable "image_tag" {
  description = "The tag of the Docker image to deploy"
  #default     = "latest"
  default     = "v1.1.0"
}

variable "project_id" {
  description = "The project ID"
  default     = "yalp-tcefrep"  # Set your default project ID here
}

variable "region" {
  description = "The region"
  default     = "us-central1"
}

variable "service_name" {
  description = "The name of the Cloud Run service"
  default     = "fastapi-metrics"
}

output "service_url" {
  value = google_cloud_run_service.default.status[0].url
}

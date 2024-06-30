provider "google" {
  credentials = file("key.json")
  project     = var.project_id
  region      = var.region
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

resource "google_bigquery_table" "metric" {
  dataset_id = google_bigquery_dataset.dataset.dataset_id
  table_id   = "metric"
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
  },
  {
    "name": "metric_0002",
    "type": "FLOAT",
    "mode": "REQUIRED"
  },
  {
    "name": "metric_0003",
    "type": "FLOAT",
    "mode": "REQUIRED"
  },
  {
    "name": "metric_0004",
    "type": "FLOAT",
    "mode": "REQUIRED"
  },
  {
    "name": "metric_0005",
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

# resource "google_bigquery_table" "metrics_mv" {
#   dataset_id = google_bigquery_dataset.dataset.dataset_id
#   table_id   = "metrics_mv"
#   project    = var.project_id

#   deletion_protection = false

#   materialized_view {
#     query = <<EOF
#     SELECT player_id, metric_0001, metric_0002, metric_0003, metric_0004, metric_0005
#     FROM (
#       SELECT player_id, metric,
#              ROW_NUMBER() OVER (PARTITION BY player_id ORDER BY update_time DESC) as rn
#       FROM `${var.project_id}.${google_bigquery_dataset.dataset.dataset_id}.metric`
#     )
#     WHERE rn = 1
#     EOF
#     enable_refresh = true
#     refresh_interval_ms = 14400000  # 4 hours in milliseconds
#   }
# }

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
  default     = "v1.0.6"
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

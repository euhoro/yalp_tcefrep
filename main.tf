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
    "name": "metric",
    "type": "FLOAT",
    "mode": "REQUIRED"
  }
]
EOF

  clustering = ["player_id"]
}

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
  default     = "v1.0.5"
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

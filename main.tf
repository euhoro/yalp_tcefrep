provider "google" {
  credentials = file("key.json")
  project     = var.project_id
  region      = var.region
}

resource "google_project" "project" {
  name            = var.project_name
  project_id      = var.project_id
  org_id          = var.organization_id
  billing_account = var.billing_account
}

resource "google_project_service" "bigquery" {
  project = google_project.project.project_id
  service = "bigquery.googleapis.com"
}

resource "google_bigquery_dataset" "dataset" {
  dataset_id = "your_dataset"
  project    = google_project.project.project_id
}

resource "google_bigquery_table" "metric_0001" {
  dataset_id = google_bigquery_dataset.dataset.dataset_id
  table_id   = "metric_0001"
  project    = google_project.project.project_id

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
  project    = google_project.project.project_id

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

variable "project_name" {
  description = "The name of the project"
  default     = "my-gcp-project"
}

variable "project_id" {
  description = "The project ID"
  default     = "yalp-tcefrep"
}

variable "organization_id" {
  description = "The organization ID"
}

variable "billing_account" {
  description = "The billing account ID"
}

variable "region" {
  description = "The region"
  default     = "us-central1"
}

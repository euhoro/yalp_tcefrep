# yalp_tcefrep
yalp_tcefrep

#https://cloud.google.com/sdk/docs/install
sudo snap install google-cloud-sdk --classic
gcloud iam service-accounts create terraform --display-name "Terraform admin account"

project same as git - yalp-tcefrep

gcloud projects add-iam-policy-binding <YOUR_PROJECT_ID> --member serviceAccount:terraform@<YOUR_PROJECT_ID>.iam.gserviceaccount.com --role roles/owner
gcloud projects add-iam-policy-binding yalp-tcefrep --member serviceAccount:terraform@yalp-tcefrep.iam.gserviceaccount.com --role roles/owner

gcloud iam service-accounts keys create key.json --iam-account terraform@yalp-tcefrep.iam.gserviceaccount.com

sudo snap install terraform --classic

create in gcp project yalp-tcefrep

enable bigquery in gcp
enable cloud billing api 
add terraform user to billing admins https://console.cloud.google.com/billing/XXXX-XXXX-XXX/manage?project=yalp-tcefrep

https://console.cloud.google.com/apis/library?project=yalp-tcefrep ???? enable api
https://console.cloud.google.com/apis/library/cloudresourcemanager.googleapis.com?project=yalp-tcefrep
https://console.cloud.google.com/apis/library/serviceusage.googleapis.com?project=yalp-tcefrep




#deployment can be done with terraform or cli
https://console.developers.google.com/apis/api/artifactregistry.googleapis.com/overview?project=173982698358

gcloud auth configure-docker

gcloud projects add-iam-policy-binding yalp-tcefrep --member=user:<USER_EMAIL> --role=roles/storage.admin

/home/<USER_NAME_UBUNTU>/.config/gcloud/application_default_credentials.json


###docker 
gcloud iam service-accounts create docker-pusher --display-name "Docker Pusher Service Account"
gcloud projects add-iam-policy-binding yalp-tcefrep --member=serviceAccount:docker-pusher@yalp-tcefrep.iam.gserviceaccount.com --role=roles/storage.admin
gcloud iam service-accounts keys create ~/key.json --iam-account=docker-pusher@yalp-tcefrep.iam.gserviceaccount.com

gcloud auth activate-service-account --key-file ~/key.json
gcloud auth configure-docker

export GOOGLE_APPLICATION_CREDENTIALS="~/key.json"
gcloud artifacts repositories create fastapi-metrics-repo --repository-format=docker --location=us --description="Docker repository for FastAPI metrics"




yalp-tcefrep

docker build -t gcr.io/yalp-tcefrep/fastapi-metrics .
docker push gcr.io/yalp-tcefrep/fastapi-metrics


#gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/fastapi-metrics
#gcloud run deploy --image gcr.io/YOUR_PROJECT_ID/fastapi-metrics --platform managed


#enable some more apis -- https://console.developers.google.com/apis/api/run.googleapis.com/overview?project=yalp-tcefrep


#logs : 
gcloud beta run services logs read fastapi-metrics --region=us-central1


1: put raw_data (parquet files ) in the root folder 
2: setup gcp ( for locally - put key.json in the root folder  - make sure apis are enabled ( big query api )
3. Docker build

gcloud auth activate-service-account --key-file=key.json
gcloud auth configure-docker us-central1-docker.pkg.dev
docker build -t us-central1-docker.pkg.dev/yalp-tcefrep/fastapi-metrics-repo/fastapi-metrics:v1.0.9 .
docker push us-central1-docker.pkg.dev/yalp-tcefrep/fastapi-metrics-repo/fastapi-metrics:v1.0.9

gcloud config set project yalp-tcefrep


# Authenticate Docker to use GCR/Artifact Registry
gcloud auth activate-service-account --key-file=/Users/euhoro/PycharmProjects/yalp_tcefrep/key_docker_pusher.json
gcloud auth configure-docker us-central1-docker.pkg.dev
docker build -t us-central1-docker.pkg.dev/yalp-tcefrep/fastapi-metrics-repo/fastapi-metrics:v1.0.7 .
docker push us-central1-docker.pkg.dev/yalp-tcefrep/fastapi-metrics-repo/fastapi-metrics:v1.0.7


key_docker_pusher.json


4.Setup the terraform env - terraform init , terraform apply .  upload all the parquet to s3 ( gap ) setup lambda to run every 1 hour
— Batch to big query activate every hour , api up , can be queried at the end of the process there will be an api point . 
Api can be queried - 

Locally -
Docker build - pandas to css
Fastapi to in mem dictionary 

mac - build image for x86
docker buildx build --platform linux/amd64 -t fastapi-metrics:v1.1.0 --load .
docker tag fastapi-metrics:v1.1.0 us-central1-docker.pkg.dev/yalp-tcefrep/fastapi-metrics-repo/fastapi-metrics:v1.1.0
docker push us-central1-docker.pkg.dev/yalp-tcefrep/fastapi-metrics-repo/fastapi-metrics:v1.1.0



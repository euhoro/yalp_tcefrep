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
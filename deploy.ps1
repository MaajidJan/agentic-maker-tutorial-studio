# PowerShell deployment script for Botrix on Google Cloud Run & Firestore

$ErrorActionPreference = "Stop"

$PROJECT_ID = if ($env:GOOGLE_CLOUD_PROJECT) { $env:GOOGLE_CLOUD_PROJECT } else { "gen-lang-client-0986160378" }
$REGION = "us-central1"
$SERVICE_NAME = "botrix-agentic-tutorial-assistant"

Write-Host "=== 1. Setting Active GCP Project: $PROJECT_ID ===" -ForegroundColor Cyan
gcloud config set project $PROJECT_ID

Write-Host "=== 2. Enabling Google Cloud APIs ===" -ForegroundColor Cyan
gcloud services enable run.googleapis.com firestore.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com

Write-Host "=== 3. Initializing Firestore Database ===" -ForegroundColor Cyan
try {
    gcloud firestore databases create --location=$REGION --type=firestore-native
} catch {
    Write-Host "Firestore database already initialized or default exists." -ForegroundColor Yellow
}

Write-Host "=== 4. Deploying to Cloud Run ===" -ForegroundColor Cyan
gcloud run deploy $SERVICE_NAME `
    --source . `
    --region $REGION `
    --platform managed `
    --allow-unauthenticated `
    --set-env-vars "GEMINI_API_KEY=$($env:GEMINI_API_KEY),GEMINI_MODEL=gemini-3.5-flash,GOOGLE_CLOUD_PROJECT=$PROJECT_ID,USE_FIRESTORE=true,FIRESTORE_COLLECTION=botrix_tutorial_jobs" `
    --memory 2Gi `
    --cpu 2 `
    --timeout 300

Write-Host "=== Deployment Successful! ===" -ForegroundColor Green
gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.url)"

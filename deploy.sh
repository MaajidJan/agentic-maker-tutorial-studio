#!/usr/bin/env bash
# Deploy Botrix Agentic Tutorial Assistant to Google Cloud Run with Firestore

set -e

PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-gen-lang-client-0986160378}"
REGION="us-central1"
SERVICE_NAME="botrix-agentic-tutorial-assistant"

echo "=== 1. Setting Active GCP Project: $PROJECT_ID ==="
gcloud config set project "$PROJECT_ID"

echo "=== 2. Enabling Required Google Cloud APIs ==="
gcloud services enable \
    run.googleapis.com \
    firestore.googleapis.com \
    cloudbuild.googleapis.com \
    artifactregistry.googleapis.com

echo "=== 3. Initializing Firestore in Native Mode (if not exists) ==="
gcloud firestore databases create --location="$REGION" --type=firestore-native || true

echo "=== 4. Building and Deploying to Cloud Run ==="
gcloud run deploy "$SERVICE_NAME" \
    --source . \
    --region "$REGION" \
    --platform managed \
    --allow-unauthenticated \
    --set-env-vars "GEMINI_API_KEY=$GEMINI_API_KEY,GEMINI_MODEL=gemini-3.5-flash,GOOGLE_CLOUD_PROJECT=$PROJECT_ID,USE_FIRESTORE=true,FIRESTORE_COLLECTION=botrix_tutorial_jobs" \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300

echo "=== 5. Deployment Complete! ==="
gcloud run services describe "$SERVICE_NAME" --region "$REGION" --format='value(status.url)'

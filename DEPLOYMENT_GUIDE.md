# Google Cloud Deployment Guide for AI Trading Platform

This guide provides a comprehensive walkthrough of the steps required to deploy the full-stack AI Trading Platform on Google Cloud Platform (GCP).

## 1. Prerequisites

- A Google Cloud Platform project.
- `gcloud` command-line tool installed and authenticated.
- `docker` installed and configured to push to Google Artifact Registry.
- All necessary source code, including the patched files and Dockerfiles.

## 2. Google Cloud Project Setup

Enable the following APIs in your GCP project. This can be done via the console or `gcloud`:

```bash
gcloud services enable \
  run.googleapis.com \
  sqladmin.googleapis.com \
  compute.googleapis.com \
  servicenetworking.googleapis.com \
  vpcaccess.googleapis.com \
  artifactregistry.googleapis.com
```

## 3. Cloud SQL for PostgreSQL Setup

1.  **Create a PostgreSQL instance**:
    - **Instance ID**: `auto-trade-db`
    - **Region**: `asia-northeast1`
    - **Database version**: PostgreSQL 13 or higher
    - **Password**: Set a strong password for the `postgres` user.

2.  **Create a database**:
    - Inside your `auto-trade-db` instance, create a new database named `trading_db`.

3.  **Create a database user**:
    - Create a new user named `trading_user` and set a password for it.

4.  **Configure networking**:
    - Enable **Private IP** for the instance.
    - The allocated IP range will be used for the VPC peering connection.

## 4. VPC Networking Setup

1.  **Create a VPC Connector**:
    - This allows Cloud Run services to communicate with the Cloud SQL instance over the private network.
    - **Name**: `auto-trade-connector`
    - **Region**: `asia-northeast1`
    - **IP range**: A `/28` range, e.g., `10.8.0.0/28`.

## 5. Backend Deployment (`auto-trade-ai`)

1.  **Build the Docker image**:
    - From the project root, build the backend image using its specific Dockerfile.
    ```bash
docker build -f Dockerfile.cloudrun -t asia-northeast1-docker.pkg.dev/YOUR_PROJECT_ID/auto-trade-repo/auto-trade-ai:full-v7 .
    ```

2.  **Push the image to Artifact Registry**:
    ```bash
docker push asia-northeast1-docker.pkg.dev/YOUR_PROJECT_ID/auto-trade-repo/auto-trade-ai:full-v7
    ```

3.  **Deploy to Cloud Run**:
    - Deploy the image as a new service. This is a single command that includes all necessary environment variables and network settings.
    - Replace placeholders like `YOUR_PROJECT_ID`, `YOUR_FRONTEND_URL`, and all secrets with your actual values.
    ```bash
gcloud run deploy auto-trade-ai \
  --image asia-northeast1-docker.pkg.dev/YOUR_PROJECT_ID/auto-trade-repo/auto-trade-ai:full-v7 \
  --platform managed \
  --region asia-northeast1 \
  --allow-unauthenticated \
  --vpc-connector auto-trade-connector \
  --set-env-vars="APP_URL=YOUR_FRONTEND_URL,ENVIRONMENT=production,DEBUG=false,DATABASE_HOST=YOUR_PRIVATE_DB_IP,DATABASE_PORT=5432,DATABASE_NAME=trading_db,DATABASE_USER=trading_user,DATABASE_PASSWORD=YOUR_DB_PASSWORD,DATABASE_URL=postgresql://trading_user:YOUR_DB_PASSWORD@YOUR_PRIVATE_DB_IP:5432/trading_db,JWT_SECRET=YOUR_JWT_SECRET,GOOGLE_CLIENT_ID=YOUR_GOOGLE_CLIENT_ID,GOOGLE_CLIENT_SECRET=YOUR_GOOGLE_CLIENT_SECRET,OPENAI_API_KEY=YOUR_OPENAI_KEY"
```

## 6. Frontend Deployment (`auto-trade-frontend`)

1.  **Build the Docker image**:
    - From the project root, build the frontend image, passing the backend URL as a build argument.
    ```bash
docker build -f frontend/Dockerfile --build-arg NEXT_PUBLIC_API_URL=https://auto-trade-ai-....run.app -t asia-northeast1-docker.pkg.dev/YOUR_PROJECT_ID/auto-trade-repo/auto-trade-frontend:v4 frontend
    ```

2.  **Push the image to Artifact Registry**:
    ```bash
docker push asia-northeast1-docker.pkg.dev/YOUR_PROJECT_ID/auto-trade-repo/auto-trade-frontend:v4
    ```

3.  **Deploy to Cloud Run**:
    ```bash
gcloud run deploy auto-trade-frontend \
  --image asia-northeast1-docker.pkg.dev/YOUR_PROJECT_ID/auto-trade-repo/auto-trade-frontend:v4 \
  --platform managed \
  --region asia-northeast1 \
  --allow-unauthenticated
    ```

## 7. Database Initialization

After the first deployment of the backend, the database tables need to be created and correctly structured.

1.  **Run the database schema fix script**:
    - The `recreate_all_tables.py` script was created to drop and recreate all tables with the correct schema, including `UUID` types.
    - This requires connecting to the database via the **Cloud SQL Auth Proxy**.
    - First, start the proxy:
      ```bash
      cloud_sql_proxy -instances=YOUR_PROJECT_ID:asia-northeast1:auto-trade-db=tcp:5432 &
      ```
    - Then, run the script with the correct environment variables (pointing to the local proxy):
      ```bash
      export DATABASE_URL="postgresql://trading_user:YOUR_DB_PASSWORD@127.0.0.1:5432/trading_db" && python3 recreate_all_tables.py
      ```
    - Stop the proxy (`kill <PID>`) once the script is complete.

2.  **Redeploy the backend service** one last time to ensure it starts fresh with the correct database schema.

## 8. Google OAuth Setup

1.  **Create OAuth 2.0 Client ID**:
    - In the GCP Console, navigate to "APIs & Services" > "Credentials".
    - Create a new OAuth 2.0 Client ID of type "Web application".

2.  **Configure Authorized URIs**:
    - **Authorized JavaScript origins**: Add your frontend URL (`https://auto-trade-frontend-....run.app`).
    - **Authorized redirect URIs**: Add your frontend callback URL (`https://auto-trade-frontend-....run.app/auth/google/callback`).

3.  **Use the Client ID and Secret**: Provide the generated Client ID and Client Secret as environment variables (`GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`) to your `auto-trade-ai` backend service during deployment.

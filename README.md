# Iris Flower ML Classifier — GitHub, Docker, EC2 and CI/CD

A small Flask application that uses a trained scikit-learn Random Forest model to predict Iris flower species. It includes Docker files and starter files for an AWS CodePipeline deployment to an EC2 instance.

## Project structure

```text
ml-iris-cicd-ec2-docker/
├── app.py
├── train_model.py
├── model.joblib
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── .gitignore
├── buildspec.yml
├── scripts/
│   ├── deploy_on_ec2.sh
│   └── install_docker_ec2_ubuntu.sh
└── README.md
```

## A. Run locally on your computer

Prerequisites: Python 3.11 and Docker Desktop (for the Docker test).

### Option 1 — Python

Open a terminal in this project folder:

```bash
python -m venv .venv
```

Windows PowerShell:
```powershell
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:
```bash
source .venv/bin/activate
```

Then run:

```bash
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000` in your browser. Health check: `http://127.0.0.1:5000/health`.

### Option 2 — Docker

From the project folder, where `Dockerfile` is located:

```bash
docker build -t iris-ml-app .
docker run --rm -p 5000:5000 --name iris-ml-app iris-ml-app
```

Open `http://127.0.0.1:5000`. Stop with `Ctrl+C`.

## B. Push source to GitHub

Create a new empty repository on GitHub, then in a terminal opened in this project folder:

```bash
git init
git add .
git commit -m "Add Iris ML app with Docker"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
git push -u origin main
```

Replace the URL with your own repository URL. If Git says `origin` already exists, run `git remote set-url origin YOUR_REPOSITORY_URL`.

## C. EC2 setup (Ubuntu)

1. Create an Ubuntu EC2 instance.
2. Create/attach an IAM instance role. For Systems Manager, attach `AmazonSSMManagedInstanceCore`. Also give it least-privilege `s3:GetObject` access to the pipeline artifact object/bucket.
3. Confirm SSM shows the instance as online/managed.
4. Allow inbound TCP port 80 from your own IP for testing (or use a load balancer for a production setup). SSH is not required if using Session Manager.
5. In the EC2 terminal/session, run the commands from `scripts/install_docker_ec2_ubuntu.sh` or paste them:
   ```bash
   sudo apt-get update
   sudo apt-get install -y docker.io unzip curl awscli
   sudo systemctl enable --now docker
   sudo docker --version
   ```
   Note: AWS CLI availability depends on the Ubuntu image/repository; if `awscli` cannot be installed with apt, install AWS CLI v2 using the official AWS instructions.

## D. CI/CD architecture and AWS configuration notes

This repository includes `buildspec.yml` for CodeBuild source validation and `scripts/deploy_on_ec2.sh` as the deployment script. **These files alone do not create an AWS pipeline.** Configure AWS resources and IAM permissions in the AWS Console.

A common beginner-friendly AWS pipeline is:

1. **S3 artifact bucket** — in the same AWS Region as the pipeline; keep it private.
2. **CodeBuild project** — source comes from CodePipeline; use `buildspec.yml`. For a stronger pipeline, have CodeBuild build the Docker image and push it to Amazon ECR.
3. **CodePipeline** — Source stage uses GitHub via the CodeConnections connection; Build stage uses CodeBuild; Deploy stage runs the deployment script on EC2 using Systems Manager Run Command.
4. **EC2 instance role** — `AmazonSSMManagedInstanceCore` plus narrowly scoped access to the pipeline artifact in S3. Avoid broad `AdministratorAccess`.
5. **CodeBuild service role** — permissions only for logs, artifact bucket, and ECR if used.
6. **CodePipeline service role** — permissions for CodeConnections, artifact S3, CodeBuild, and SSM deployment action as appropriate.

### Deployment script variables

The deployment script expects:
- `ARTIFACT_BUCKET`: private S3 bucket name holding the source ZIP.
- `ARTIFACT_KEY`: object key for the source ZIP (default `iris-ml-app/source.zip`).
- `AWS_REGION`: region, default `ap-south-1`.
- EC2 must have Docker, AWS CLI, unzip, and curl installed.

The script must run on the EC2 instance, not your Windows computer. It downloads the source ZIP from S3, builds the image on EC2, and restarts the container. Configure your pipeline to publish the deployable source ZIP to that exact S3 bucket/key and to invoke the script through SSM. If your CodePipeline action supplies artifacts differently, adjust the artifact download step to match that action.

## E. Test the deployed app

After deployment, open `http://EC2_PUBLIC_IP/`. Health endpoint: `http://EC2_PUBLIC_IP/health`.

The EC2 security group must allow inbound TCP 80 from your testing IP. Do not expose development ports or secrets publicly.

## Troubleshooting

- `docker: command not found`: install and start Docker on EC2.
- `AccessDenied` from S3: check the EC2 instance role and bucket/object policy.
- SSM target unavailable: check instance role, SSM Agent, network access, and managed-instance status.
- Page not reachable: check the EC2 public IP, security-group port 80 rule, and `docker ps`.
- Pipeline does not deploy by itself just because GitHub contains `buildspec.yml`; the CodePipeline, CodeBuild and SSM actions must be configured in AWS.

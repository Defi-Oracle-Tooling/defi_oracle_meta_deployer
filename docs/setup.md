# Setup
This section will guide you through the setup process for the DeFi Oracle Meta Deployer project.

## Prerequisites
- Python 3.8 or higher
- Azure CLI
- Git
- Docker (optional)

## Installation

### Clone the Repository
1. Clone the repository:
```bash
git clone https://github.com/your-repo/defi_oracle_meta_deployer.git
```
2. Navigate to the project directory:
```bash
cd defi_oracle_meta_deployer
```

### Python Setup
3. Install the required Python packages:
```bash
pip install -r requirements.txt
```

### Environment Variables
4. Set up environment variables:

#### Using Export (Linux/MacOS)
```bash
export AZURE_SUBSCRIPTION_ID=<your_subscription_id>
export AZURE_ACCESS_TOKEN=<your_access_token>
export AZURE_ADMIN_PASSWORD=<your_admin_password>
export SECRET_KEY=<your_secret_key>
```

#### Using .env File
Create a `.env` file in the project root and add the following:
```
AZURE_SUBSCRIPTION_ID=your_subscription_id
AZURE_ACCESS_TOKEN=your_access_token
AZURE_ADMIN_PASSWORD=your_admin_password
SECRET_KEY=your_secret_key
```

### Additional Setup for New Features

#### Azure Active Directory (OAuth2) Integration

1. Register your application in Azure Active Directory to obtain the necessary credentials.
2. Update the `.env` file with the following additional environment variables:
```
AZURE_CLIENT_ID=your_client_id
AZURE_CLIENT_SECRET=your_client_secret
AZURE_TENANT_ID=your_tenant_id
```

#### Machine Learning Model

1. Ensure the `ml_model.pkl` file is present in the project root. This file contains the pre-trained machine learning model used for predictions.

#### Monitoring and Alerts

1. Ensure you have the necessary permissions to create Log Analytics workspaces and set up monitoring and alerts in your Azure subscription.

### Running the Application
5. Run the application:
```bash
python app.py
```
6. Access the web interface:
Open your browser and navigate to `http://localhost:5000`.

### Running the Application with New Features

1. Run the application:
```bash
python app.py
```
2. Access the web interface:
Open your browser and navigate to `http://localhost:5000`.

### Docker Setup (Optional)

#### Build and Run with Docker
1. Build the Docker image:
```bash
docker build -t defi_oracle_meta_deployer .
```
2. Run the Docker container:
```bash
docker run -d -p 5000:5000 --env-file .env defi_oracle_meta_deployer
```

### Testing

#### Running Unit Tests
1. Run the unit tests:
```bash
pytest tests/
```
2. Generate a coverage report:
```bash
pytest --cov=app tests/
```
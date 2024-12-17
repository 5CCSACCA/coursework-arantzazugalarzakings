[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/pa_hoUiU)
# FastAPI Emotion Detection App

## Overview
This project implements a FastAPI application for emotion detection in text. The app is built with Python, containerized using Docker.
⚠️ **Note**: The CI/CD pipeline is not reliable yet. Manual setup and deployment are recommended.

---

## Prerequisites

Before running the application, ensure you have the following software installed:

### 1. **Docker**
- Install Docker: [Official Guide](https://docs.docker.com/get-docker/)
- Verify installation on the terminal: 
   docker --version

### 2. **Docker Compose**
- Comes preinstalled with modern Docker versions.
- Verify installation on the terminal: 
   docker compose version

### 3. **MongoDB**
 Install MongoDB locally: [Install MongoDB](https://www.mongodb.com/docs/manual/installation/)

Ensure MongoDB runs on `localhost:27017` or provide your connection string in the `.env` file.
---

## Installation and Setup

### 1. Clone the Repository
Clone the repository to your local machine:

git clon https://github.com/5CCSACCA/coursework-arantzazugalarzakings.git
cd <coursework-arantzazugalarzakings>

### 2. Create the Environment File
Create a `.env` file in the root of the project directory to configure MongoDB connection settings:
MONGO_URI=mongodb://localhost:27017/emotion_db

### 3. Run the Application with Docker Compose
Use Docker Compose to build and start the application and MongoDB service.
docker compose up --build

- The FastAPI application (API Gateway, the API unified) will be available at: [http://localhost:8002](http://localhost:8002)
- To see authentication only: [http://localhost:800](http://localhost:8001)
- To see the model only: [http://localhost:8000](http://localhost:8000)
---

### 4. Verify the Running Containers
To check if the containers are running successfully:
docker ps

You should see:
- A container running for the services: authentication, model and API Gateway. 
- A container running MongoDB.

---

### 5. Stop the Application
To stop and remove all containers:

docker compose down


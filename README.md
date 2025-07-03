Here's your guide for setting up and deploying your YOLO API, formatted for a GitHub repository's `README.md` file:

-----

# LineBOT : YOLO Object Detection API Setup and Deployment Guide

This guide will walk you through setting up your YOLO Object Detection API, running it locally, and deploying it to Heroku.

-----

## 1\. Local Setup

### 1.1. Create and Activate Virtual Environment

It's highly recommended to use a virtual environment to manage dependencies and avoid conflicts.

```bash
pip install virtualenv
virtualenv yolo-api-venv
```

To activate your virtual environment:

```bash
cd yolo-api-venv\Scripts\activate.bat
```

> **Note:** Always activate your virtual environment before running any commands related to this project.

### 1.2. Install Dependencies

Install all necessary libraries from the `requirements.txt` file. This file should be located in your `MainCode-Heroku` directory.

```bash
pip install -r requirements.txt
```

> **Important:**
>
>   * To **save** your currently installed libraries to `requirements.txt`:
>     ```bash
>     pip freeze > requirements.txt
>     ```
>     Do not delete this file without backing it up\!
>   * To **uninstall** all libraries listed in `requirements.txt` (useful before cloud deployment):
>     ```bash
>     pip uninstall -r requirements.txt -y
>     ```

### 1.3. Configure Environment Variables

You need to rename the `Ex_env.txt` files to `.env` in the following locations to configure your environment variables (e.g., Firebase credentials, API keys).

  * `.\FireBase\functions`
  * `.\MainCode-Heroku`

-----

## 2\. Running Locally

### 2.1. Run Object Detection API

Navigate to your `MainCode-Heroku` directory (if not already there) and run the API:

```bash
cd MainCode-Heroku # If you're not in this directory
py line-yolo-api.py
```

### 2.2. Run Firebase Functions (for testing)

To test your Firebase functions locally using the Firebase emulators:

```bash
firebase emulators:start --only functions
```

-----

## 3\. Deployment

### 3.1. Deploy Firebase Functions

Once you are ready to deploy your Firebase functions to the cloud:

```bash
firebase deploy --only functions
```

-----

### 3.2. Deploy to Heroku

This section covers deploying your YOLO API to Heroku using Docker containers.

#### 3.2.1. Login to Heroku Container Registry

First, log in to the Heroku Container Registry:

```bash
heroku login
heroku container:login
```

#### 3.2.2. Build and Push Docker Image

Navigate to your project's main directory (where your `Dockerfile` is located), then build and push your Docker image to Heroku. Replace `your-heroku-app-name` with the actual name of your Heroku application.

```bash
# Ensure you are in the directory containing your Dockerfile (e.g., MainCode-Heroku)
heroku container:push web -a your-heroku-app-name
```

#### 3.2.3. Release Docker Image

Finally, release the pushed Docker image to your Heroku application:

```bash
heroku container:release web -a your-heroku-app-name
```
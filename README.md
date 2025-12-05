# Banao Hospital Management System (HMS)

A full-stack Hospital Management System built with Django and Serverless Framework.

## Features

-   **User Roles**: Distinct Patient and Doctor roles with mutual exclusivity.
-   **Authentication**: Secure Signup/Login with role-based dashboards.
-   **Appointments**:
    -   Doctors can create availability slots.
    -   Patients can book available slots.
    -   Real-time concurrency handling to prevent double booking.
-   **Notifications**:
    -   **Serverless Email Service**: AWS Lambda function (Python) to send emails via Gmail SMTP.
    -   Welcome emails on signup.
    -   Confirmation emails to both Patient and Doctor on booking.
-   **Database**: PostgreSQL for robust data management.

## Tech Stack

-   **Backend**: Django 6.0, Python 3.9+
-   **Database**: PostgreSQL
-   **Serverless**: Serverless Framework V3, AWS Lambda (emulated locally via `serverless-offline`)
-   **Frontend**: Django Templates, Bootstrap 5

## Setup Instructions

### 1. Prerequisites
-   Python 3.8+
-   Node.js & npm
-   PostgreSQL

### 2. Backend Setup
1.  Clone the repository.
2.  Install Python dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Create a `.env` file in the root directory:
    ```env
    DB_NAME=banao_hms
    DB_USER=your_postgres_user
    DB_PASSWORD=your_postgres_password
    DB_HOST=localhost
    DB_PORT=5432
    ```
4.  Run migrations:
    ```bash
    python manage.py migrate
    ```
5.  Create a superuser:
    ```bash
    python manage.py createsuperuser
    ```
6.  Run the server:
    ```bash
    python manage.py runserver
    ```

### 3. Email Service Setup
1.  Navigate to the serverless directory:
    ```bash
    cd serverless-email
    ```
2.  Install Node dependencies:
    ```bash
    npm install
    ```
3.  Create a `.env` file in `serverless-email/`:
    ```env
    EMAIL_USER=your_email@gmail.com
    EMAIL_PASS=your_app_password
    ```
4.  Run the local offline server:
    ```bash
    npx serverless offline
    ```

## Usage
1.  Start both the Django server and the Serverless Offline server.
2.  Visit `http://127.0.0.1:8000` to access the application.

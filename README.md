# Task Management and Report Subscription System

## Project Overview

The **Task Management and Report Subscription System** allows users to effectively manage tasks and subscribe to automated reports. Users can receive scheduled email summaries based on their selected frequency (daily, weekly, or monthly). The system includes robust user authentication and authorization to ensure that only authenticated users can access specific endpoints.

## Setup Instructions

### Prerequisites

- Docker
- Docker Compose
- Python 3.12 or later (for local development)

## Setup Instructions

Follow these steps to set up and run the project locally.

1. Clone the repository:
   - Start by cloning the repository to your local machine:
   ```bash
   git clone https://github.com/YasminaMohamed99/Task-Management-and-Report-Subscription-System.git
   cd task-management-system
   ```
2. Open Docker Desktop.
   - Ensure that Docker is running on your machine. If not, open Docker Desktop.

3. Build and start the Docker containers
   - To build and start the Docker containers, execute the following command:
   ```bash
     docker-compose up --build
   ```
4. Run Migrations and Create SuperUser
   - Once the containers are up, access the web container and run the migrations, then create a superuser for the Django admin:
   ```bash
      docker-compose exec web bash
      python manage.py migrate
      python manage.py createsuperuser
   ```
5. Start the Application
   - To start the application, use the following command:
   ```bash
      docker-compose up
   ```
6. Run Celery Workers and Scheduler for Email Notifications
   - To start the Celery worker and scheduler to send emails and generate reports, run the following commands:
   ```bash
    docker-compose exec web celery -A task_management worker --loglevel=info
    docker-compose exec web celery -A task_management beat --loglevel=info
      ```
7. Access the Swagger API Documentation
   - Once the containers are up and running, you can view the Swagger API documentation by navigating to the following URL in your browser
      ```bash
         http://localhost:8000/swagger/
      ```
8. Stopping the Containers
   - To stop the running containers, use the following command
 ```bash
    docker-compose down
 ```


## API Requests and Responses

1. ### User Authentication
   ***Sign Up***: 
   - This API allows users to sign up by providing a username, email, and password, with validation to prevent duplicate sign-ups using the same email address. The password must meet specific security criteria to ensure the safety of user accounts.
     - **Endpoint:**
        ```
        POST /api/users/signup
        ```
     - **Request Body:**
         To create a new user, send a POST request with the following JSON payload:
          ```
             {
              "username": "username",
              "email": "user@example.com",
              "password": "Password@123"
             }
        ```
     - **Validation Rules:**
         - email and password required fields
         - Email must be email address validation
         - Minimum Length: The password must be at least 8 characters long.
         - Contains a Digit: The password must contain at least one digit.
         - Contains a Lowercase Letter: The password must contain at least one lowercase letter.
         - Contains an Uppercase Letter: The password must contain at least one uppercase letter.
         - Contains a Special Character: The password must contain at least one special character (e.g., !, @, #, etc.)..
     
     - **Returns:**
        - On success, returns `User created successfully` with status 201.
        - On failure, returns `Bad Request - Validation errors` with status 400.
        - Internal Server Error returns status 500.
        - 
     ***Sign In***:
       - Authenticates a user using email and password. If the credentials are valid, it generates a JWT access token and a refresh token. The access token expires 60 minutes after generated. If the credentials are invalid or the user does not exist, an error message is returned.
       - **Endpoint:**
         ```
         POST /api/users/signin
         ```
       - **Request Body:**
          To create a new user, send a POST request with the following JSON payload:
           ```
              {
               "username": "username",
               "email": "user@example.com",
               "password": "Password@123"
              }
         ```
       - **Validation Rules:**
          - email and password required fields
       - **Returns:**
         - On success, returns `Login Successfully` with status 200.
         - On failure, returns `Bad Request` with status 400 and error messages.
         - Unauthorized User - returns status 401.
         - Internal Server Error returns status 500.
     
2. ### Task Management API
     ***Create Task***
      - Creates a new task with the provided details.
      - **Endpoint:**
           ```
           POST /api/tasks/create
           ```
      - **Request Body:**
         To create a new task, send a POST request with the following JSON payload:
          ```
             {
                "title": "Complete user authentication system",
                "description": "Implement and test user login, registration, and password reset functionality.",
                "start_date": "2025-01-10",
                "due_date": "2025-01-11",
                "status": "Completed"
             }
        ```
      - **Validation Rules:**
         - title, description, start_date, due_date all fields required
         - title must be unique across all tasks for each user.
         - start_date must be earlier than or equal to due_date and completion_date if exists.
      - **Returns:**
         - On success, returns the created task with status 201.
         - On failure, returns validation errors with status 400.
         - Unauthorized User - returns status 401.
         - Internal Server Error returns status 500.

   ***Retrieves Task***
      - Retrieves a list of tasks filtered by the provided parameters or all tasks owned by the authenticated user.

      - **Endpoint:**
           ```
           GET /api/tasks/retrieve_tasks/
           ```
      - **Parameters:**
          - `status`: (Optional) Filter tasks by their status (`Pending`, `Completed`, `Overdue`).
          - `start_date`: (Optional) Filter tasks that start on or after this date (format: YYYY-MM-DD).
          - `end_date`: (Optional) Filter tasks that end on or before this date (format: YYYY-MM-DD). This filter works as follows:
               - If a task has a completion_date, it will be included if the completion_date is less than or equal to the provided end_date.
               - If a task does not have a completion_date but has a due_date, it will be included if the due_date is less than or equal to the provided end_date.
      - **Returns:**
         - A filtered list of tasks based on the provided parameters, or all tasks if no parameters are provided.
         - Returns a 400 Bad Request response if invalid parameters are provided with error messages.
         - Unauthorized User - returns status 401.
         - Internal Server Error returns status 500.

   ***Update Task***
      - The task can only be updated by its owner. If the status field is changed to a completed or overdue status, the completion_time field will be automatically updated to the current date.

      - **Endpoint:**
           ```
           PUT /api/tasks/update/{id}/
           PATCH /api/tasks/update/{id}/
           ```
      - **Request Body:**
         To update task, send a PUT request with the following JSON payload or PATCH request with partial update:
          ```
             {
                "title": "Complete user authentication system",
                "description": "Implement and test user login, registration, and password reset functionality.",
                "start_date": "2025-01-10",
                "due_date": "2025-01-11",
                "status": "Completed"
             }
        ```
      - **Validation Rules:**
         - title must be unique across all tasks for each user.
         - start_date must be earlier than or equal to due_date and completion_date if exists.
         - Updated task by its owner.

      - **Returns:**
         - On success, returns `Task updated successfully.` with status 200.
         - On failure, returns `Bad Request - Invalid data provided or update failed.` with status 400 and error messages.
         - Unauthorized User - returns status 401.
         - Permission Denied - `You do not have permission to access this task` with status 403.
         - `Task doesn't exist.` with status 404
         - Internal Server Error returns status 500.
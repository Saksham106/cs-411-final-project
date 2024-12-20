# **Weather Application API**

## **Overview**

This Weather Application API is built using Flask. It allows users to:

-   Fetch weather data from the Visual Crossing API.
-   Retrieve current weather conditions, weekly averages, and other weather details.
-   Create user accounts, log in, and update passwords.

The API is containerized using Docker and stores user and location data in SQLite.



## **Setup Instructions**

### **Using Docker**

1. **Build the Docker Image:**
    ```bash
    docker build -t weather-app .
    ```
2. **Run the Docker Container:**
    ```bash
    docker run -d -p 5002:5002 --env-file .env weather-app
    ```

## Routes Documentation

### /api/health

-   **Request Type:** `GET`
-   **Purpose:** Verifies that the application is running.
-   **Response Format:** JSON
    -   **Success Response Example:**
        -   **Code:** `200`
        -   **Content:**
            ```json
            {
                "status": "healthy"
            }
            ```


### **/api/`<city>`**

-   **Request Type:** `GET`
-   **Purpose:** Fetches weather data for the specified city from the Visual Crossing API.
-   **Response Format:** JSON
    -   **Success Response Example:**
        -   **Code:** `200`
        -   **Content:**
            ```json
            {
              "days": [...],
              "currentConditions": {...}
            }
            ```
    -   **Error Response Example:**
        -   **Code:** `500`
        -   **Content:**
            ```json
            {
                "error": "HTTP error occurred: ..."
            }
            ```


### /api/`<city>`/current-conditions

-   **Request Type:** `GET`
-   **Purpose:** Retrieves current weather conditions for the city.
-   **Response Format:** JSON
    -   **Success Response Example:**
        -   **Code:** `200`
        -   **Content:**
            ```json
            {
                "temp": 70,
                "humidity": 50,
                "precip": 0.1
            }
            ```
            

### /api/`<city>`/week-average-temp

-   **Request Type:** `GET`
-   **Purpose:** Calculates the weekly average temperature for the city.
-   **Response Format:** JSON
    -   **Success Response Example:**
        -   **Code:** `200`
        -   **Content:**
            ```json
            {
                "week_average_temp": 72.5
            }
            ```


### /api/`<city>`/max-temp-day

-   **Request Type:** `GET`
-   **Purpose:** Fetches the day with the highest maximum temperature.
-   **Response Format:** JSON
    -   **Success Response Example:**
        -   **Code:** `200`
        -   **Content:**
            ```json
            {
                "tempmax": 85,
                "date": "2024-12-10"
            }
            ```


### /api/`<city>`/min-temp-day

-   **Request Type:** `GET`
-   **Purpose:** Fetches the day with the lowest minimum temperature.
-   **Response Format:** JSON
    -   **Success Response Example:**
        -   **Code:** `200`
        -   **Content:**
            ```json
            {
                "tempmin": 60,
                "date": "2024-12-09"
            }
            ```


### /api/`<city>`/highest-precip-day

-   **Request Type:** `GET`
-   **Purpose:** Fetches the day with the highest precipitation probability.
-   **Response Format:** JSON
    -   **Success Response Example:**
        -   **Code:** `200`
        -   **Content:**
            ```json
            {
                "precipprob": 90,
                "date": "2024-12-11"
            }
            ```


### **/api/create-account**

-   **Request Type:** `POST`
-   **Purpose:** Creates a new user account with a username and password.
-   **Request Body:**

    ```json
    {
        "username": "newuser123",
        "password": "securepassword"
    }
    ```

-   **Response Format:** JSON
    -   **Success Response Example:**
        -   **Code:** `201`
        -   **Content:**
            ```json
            {
                "message": "Account created successfully"
            }
            ```


### **/api/login**

-   **Request Type:** `POST`
-   **Purpose:** Logs in a user with their username and password.
-   **Request Body:**
    ```json
    {
        "username": "newuser123",
        "password": "securepassword"
    }
    ```
-   **Response Format:** JSON

    -   **Success Response Example:**

        -   **Code:** `200`
        -   **Content:**
            ```json
            {
                "message": "Login successful"
            }
            ```


### **/api/update-password**

-   **Request Type:** `POST`
-   **Purpose:** Updates a user's password.
-   **Request Body:**
    ```json
    {
        "username": "newuser123",
        "old_password": "securepassword",
        "new_password": "newsecurepassword"
    }
    ```
-   **Response Format:** JSON
    -   **Success Response Example:**
        -   **Code:** `200`
        -   **Content:**
            ```json
            {
                "message": "Password updated successfully"
            }
            ```


## **Testing**

### **Unit Tests**

Run unit tests to ensure individual features work as expected:

```bash
pytest tests/
```

### **Smoke Tests**

Run smoke tests to verify that critical features are operational:

```bash
sh smoketest.sh
```



## **Dependencies**

-   **Python Libraries:**
    -   Flask
    -   requests
    -   python-dotenv
    -   pytest
    -   SQLite3
-   **External API:**
    -   [Visual Crossing Weather API](https://www.visualcrossing.com/)

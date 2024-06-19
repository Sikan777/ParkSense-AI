# ParkSense-AI 


---

ParkSense-AI is a web application designed to automate the detection of vehicle license plates in images, track parking duration for each unique vehicle, and calculate accumulated parking fees.

---

## Table of Contents

- [Technologies](#technologies)
- [Basic functionality](#basic-functionality)
- [Usage](#usage)
  - [Installation](#installation)
  - [Additional information](#additional-information)
- [License](#license)
- [Authors](#authors)

---

## Technologies

| **Module**                                           | **Description**    |
| ---------------------------------------------------- | ------------------ |
| [FastAPI](https://fastapi.tiangolo.com/)             | Framework          |
| [Pydantic](https://pydantic-docs.helpmanual.io/)     | Validation library |
| [SQLAlchemy](https://docs.sqlalchemy.org/)           | ORM                |
| [Alembic](https://alembic.sqlalchemy.org/en/latest/) | Migration tool     |
| [PostgreSQL](https://www.postgresql.org/)            | Database           |
| [Cloudinary](https://cloudinary.com/)                | Image hosting      |
| [Passlib](https://passlib.readthedocs.io/en/stable/) | Password hashing   |
| [Pillow](https://pypi.org/project/Pillow/)           | Image processing   |
| [Tensorflow](https://www.tensorflow.org/guide/tensor)| Machine learning   |
| [OpenCV](https://docs.opencv.org/4.x/)               | Computer vision    |
| [Easyocr](https://github.com/JaidedAI/EasyOCR)       | Optical character recognition   |


---

## Basic functionality

## Authentication

### Signup
**Endpoint:** `POST /api/auth/signup`

Registers a new user.

### Login
**Endpoint:** `POST /api/auth/login`

Authenticates a user and returns a token.

### Refresh Token
**Endpoint:** `GET /api/auth/refresh_token`

Refreshes the authentication token.

### Logout
**Endpoint:** `POST /api/auth/logout`

Logs out the authenticated user.

## Users

### Get Current User
**Endpoint:** `GET /api/users/me`

Retrieves the profile of the currently authenticated user.

### Update Profile
**Endpoint:** `PATCH /api/users/me`

Updates the profile of the currently authenticated user.

### Get User Profile
**Endpoint:** `GET /api/users/{username}`

Retrieves the profile of a user by their username.

### Ban User
**Endpoint:** `PATCH /api/users/admin/{username}/ban`

Bans a user by their username (Admin only).

### Get Cars By User
**Endpoint:** `GET /api/users/cars/{user_id}`

Retrieves all cars associated with a specific user.

### Get Car By Plate
**Endpoint:** `GET /api/users/cars/{plate}`

Retrieves a car by its plate number.

## Admin

### Read Cars
**Endpoint:** `GET /api/admin/cars`

Retrieves a list of all cars (Admin only).

### Create Car
**Endpoint:** `POST /api/admin/cars`

Creates a new car entry (Admin only).

### Get Default Parking Rate
**Endpoint:** `GET /api/admin/default-parking-rate`

Retrieves the default parking rate.

### Create Or Update Parking Rate
**Endpoint:** `POST /api/admin/parking-rates`

Creates or updates a parking rate (Admin only).

### Read Parked Cars
**Endpoint:** `GET /api/admin/cars/parked`

Retrieves a list of all currently parked cars (Admin only).

### Read Car
**Endpoint:** `GET /api/admin/cars/{plate}`

Retrieves a car by its plate number (Admin only).

### Update Car
**Endpoint:** `PATCH /api/admin/cars/{plate}`

Updates a car entry by its plate number (Admin only).

### Delete Car
**Endpoint:** `DELETE /api/admin/cars/{plate}`

Deletes a car entry by its plate number (Admin only).

### Read Users By Car
**Endpoint:** `GET /api/admin/users-by-car/{plate}`

Retrieves a list of users associated with a specific car (Admin only).

### Ban Car
**Endpoint:** `PATCH /api/admin/cars/{plate}/ban`

Bans a car by its plate number (Admin only).

## Images

### Park Entry
**Endpoint:** `POST /api/parking/entry`

Records an entry event for a car using image processing.

### Park Exit
**Endpoint:** `POST /api/parking/exit`

Records an exit event for a car using image processing.

## Parking

### Park Entry
**Endpoint:** `POST /api/parking/entry`

Records an entry event for a car.

### Park Exit
**Endpoint:** `POST /api/parking/exit`

Records an exit event for a car.

## Parking-Rate

### Get Latest Parking Rate With Free Spaces
**Endpoint:** `GET /api/parking-rate/free-spaces`

Retrieves the latest parking rate and the number of free parking spaces.

### Create Rate
**Endpoint:** `POST /api/parking-rate/new-parking-rate`

Creates a new parking rate entry.

---

## Usage

### Installation

- Clone the repository.

```Shell
  git clone https://github.com/Sikan777/ParkSense-AI.git
```

- Run docker file.

```Shell
  docker run --name ParkSense-AI -p 5432:5432 -e POSTGRES_PASSWORD=pass -d postgres
```

- Install dependencies.

_using poetry_

```Shell
  poetry install
```

- Setup the ".env" file.

```Shell
  cp .env.example .env
```
- We create a database in DBeaver with the appropriate name and password located in the .env file

- Update migrations

```Shell
  alembic upgrade head
```

- Run the application.

```Shell
  uvicorn main:app --reload
```

- Access the API documentation at `http://127.0.0.1:8000/docs#/ after starting the development server.

- Use the provided endpoints to manage users, cars, and parking rates.

---

### Additional information


- [Swagger documentation](http://127.0.0.1:8000/docs#)
- [GitHub](https://github.com/Sikan777/ParkSense-AI.git)
- [Prezentation](https://www.canva.com/design/DAGIZD7T0Qc/OmFtbHDnEqkxa7iMxOARPw/view?utm_content=DAGIZD7T0Qc&utm_campaign=designshare&utm_medium=link&utm_source=editor#1)


---

## License

This project is distributed under the **MIT** license.

---

## Authors

The **PyCrafters** Team:

- [Yuliia Didenko](https://github.com/yulyan407)
- [Maksim Nesterovskyi](https://github.com/legendarym4x)
- [Olga Tsuban](https://github.com/OlgaTsuban)
- [Yaroslav Vdovenko](https://github.com/hedgyv)
- [Bohdan Sikan](https://github.com/Sikan777)

---

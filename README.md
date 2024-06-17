# ParkSense-AI 

<p align="center">
  <img src="http://res.cloudinary.com/dyhtnkitj/image/upload/v1709056165/ImageHubProjectDB/user_1/original_images/ttu63ajzijfgp7ydjinm.jpg"
  alt="ImageHub" width="256" height="256">
</p>

---

ParkSense-AI is a web application designed to automate the detection of vehicle license plates in images, track parking duration for each unique vehicle, and calculate accumulated parking fees.

---

## Table of Contents

- [Technologies](#technologies)
- [Basic functionality](#basic-functionality)
  - [Authentication](#authentication)
  - [Working with photos](#working-with-photos)
  - [Comments](#comments)
  - [Profile](#profile)
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

### POST /api/auth/signup
Signup a new user.

### POST /api/auth/login
Login an existing user.

### GET /api/auth/refresh_token
Refresh the authentication token.

### POST /api/auth/logout
Logout the current user.

## Users

### GET /api/users/me
Get the current user's profile.

### PATCH /api/users/me
Update the current user's profile.

### GET /api/users/{username}
Get a user's profile by username.

### PATCH /api/users/admin/{username}/ban
Ban a user by username (Admin only).

### GET /api/users/cars/{user_id}
Get cars associated with a user by user ID.

### GET /api/users/cars/{plate}
Get a car by its license plate.

## Admin

### GET /api/admin/cars
Retrieve a list of all cars.

### POST /api/admin/cars
Add a new car.

### GET /api/admin/default-parking-rate
Get the default parking rate.

### POST /api/admin/parking-rates
Create or update a parking rate.

### GET /api/admin/cars/parked
Retrieve a list of currently parked cars.

### GET /api/admin/cars/{plate}
Retrieve information about a car by its license plate.

### PATCH /api/admin/cars/{plate}
Update a car's information by its license plate.

### DELETE /api/admin/cars/{plate}
Delete a car by its license plate.

### GET /api/admin/users-by-car/{plate}
Retrieve users associated with a car by its license plate.

### PATCH /api/admin/cars/{plate}/ban
Ban a car by its license plate.

## Images

### POST /api/parking/entry
Register a parking entry event.

### POST /api/parking/exit
Register a parking exit event.

## Parking

### POST /api/parking/entry
Register a parking entry event.

### POST /api/parking/exit
Register a parking exit event.

## Parking-Rate

### GET /api/parking-rate/free-spaces
Get the latest parking rate with available free spaces.

### POST /api/parking-rate/new-parking-rate
Create a new parking rate.

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

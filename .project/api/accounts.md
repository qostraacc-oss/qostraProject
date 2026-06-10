# Accounts API Reference

Provides user identity and profile-related endpoints.

---

## Get User Profile

Retrieve the currently authenticated user's profile information.

- **URL**: `/api/accounts/profile/`
- **Method**: `GET`
- **Headers**:
  - `Authorization: Bearer <JWT_TOKEN>`
- **Response (200 OK)**:
  ```json
  {
    "id": "e441c49b-b0b3-4ad5-ae92-c9b64efc60bf",
    "username": "jane_doe",
    "email": "jane.doe@example.com",
    "first_name": "Jane",
    "last_name": "Doe"
  }
  ```
- **Response (401 Unauthorized)**:
  ```json
  {
    "detail": "Authentication credentials were not provided."
  }
  ```

---

## Update User Profile

Partially update the currently authenticated user's profile information.

- **URL**: `/api/v1/accounts/profile/`
- **Method**: `PATCH`
- **Headers**:
  - `Authorization: Bearer <JWT_TOKEN>`
- **Request Body**:
  ```json
  {
    "first_name": "Janet",
    "last_name": "Smith"
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "id": "e441c49b-b0b3-4ad5-ae92-c9b64efc60bf",
    "username": "jane_doe",
    "email": "jane.doe@example.com",
    "first_name": "Janet",
    "last_name": "Smith"
  }
  ```

# Task Tracker API

Project URL: [To-do List API](https://roadmap.sh/projects/todo-list-api)

## Endpoints

### User Registration

Register as a new user by making the following request:

```
# POST /register

{
  “name”: “John Doe”,
  “email”: “john@doe.com”,
  “password”: “password”
}
```

The server will validate the provided details, ensure the email is unique, and store the user information in the database.

If the registration is successful, a token will be returned for authentication purposes:

```
{
  “token”: “eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9”
}
```

### User Login

Log in as an existing user by making the following request:

```
# POST /login

{
  “email”: “john@doe.com”,
  “password”: “password”
}
```

The server will validate the email and password. Upon successful authentication, it will respond with a token:

```
{
  “token”: “eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9”
}
```

All other endpoints require an authentication token. If the token is missing or invalid, the server will respond with a 401 status code and an error message:

```
{
  “message”: “Unauthorized”
}
```

To authenticate a request, include the token received from the login endpoint in the `Authorization` header.

### Create a To-Do Item

Create a new to-do item by making the following request:

```
# POST /todos

{
  “title”: “Buy groceries”,
  “description”: “Buy milk, eggs, and bread”
}
```

Upon successful creation, the server will respond with the details of the created to-do item:

```
{
  “id”: 1,
  “title”: “Buy groceries”,
  “description”: “Buy milk, eggs, and bread”
}
```

### Update a To-Do Item

Update an existing to-do item by making the following request:

```
# PUT /todos/1

{
  “title”: “Buy groceries”,
  “description”: “Buy milk, eggs, bread, and cheese”
}
```

Only the creator of a to-do item is authorized to update it. If the requesting user is not authorized, the server will respond with a 403 status code and an error message:

```
{
  “message”: “Forbidden”
}
```

Upon successful update, the server will respond with the updated details of the to-do item:

```
{
  “id”: 1,
  “title”: “Buy groceries”,
  “description”: “Buy milk, eggs, bread, and cheese”
}
```

### Delete a To-Do Item

Delete an existing to-do item by making the following request:

```
# DELETE /todos/1
```

The requesting user must be authenticated and authorized to delete the to-do item.

Upon successful deletion, the server will respond with a 204 status code.

### Get To-Do Items

Retrieve a list of to-do items by making the following request:

```
# GET /todos?page=1&limit=10
```

The response will include the list of to-do items along with pagination details. For example:

```
{
  “data”: [
    {
      “id”: 1,
      “title”: “Buy groceries”,
      “description”: “Buy milk, eggs, bread”
    },
    {
      “id”: 2,
      “title”: “Pay bills”,
      “description”: “Pay electricity and water bills”
    }
  ],
  “page”: 1,
  “limit”: 10,
  “total”: 2
}
```

Authentication is required to access this endpoint. The response is paginated, with `page` and `limit` parameters to control the results.

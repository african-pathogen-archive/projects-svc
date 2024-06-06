# SANBI Projects Service

The Projects Service limits creation of projects to certain groups through Ego authorization.
Project creation allows the project administrator to provide the details and, crucially, **the group** for a project. 

## Get Started

```
docker-compose up --build
```

```
docker exec -it app bash
```

```
flask db init
flask db migrate -m "Run migrations"
flask db upgrade
```
Should be accessible on `http://localhost:5000`
Swagger is available at: `http://localhost:5000/swagger/`

## UI Sandbox

A basic React App to interact with the API

```
cd ui
yarn


yarn dev
```
Shoud be accessible on `http://localhost:1234`


## JWT Token

Projects Service's currently uses its own cookie - this will be replaced with the one from Ego later, but can currently be generated through the UI.

A valid JWT from Ego is still needed (to call groups endpoint) and needs to be manually added as EGOJWT cookie
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

## Permissions

Currently the ability to edit and manage projects and pathogens is defined in `config.py` with the values:

```
PROJECT_GROUP = 'ego_group_id'
PATHOGEN_GROUP = 'ego_group_id'
```

## UI Sandbox

A basic React App to interact with the API

```
cd ui
yarn

yarn dev
```
Shoud be accessible on `http://localhost:1234`


## JWT Token

The Projects Service requires a valid EGO generated JWT token. When using the UI Sandbox, add it as a cookie `JWT`.

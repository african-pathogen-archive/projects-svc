# SANBI Projects Service

The projects service adds pathogens, projects and user management to the studies workflow.


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

## JWT Token

The Projects Service requires a valid EGO generated JWT token. When using the UI Sandbox, add it as a cookie `JWT`.

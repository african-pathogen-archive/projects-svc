# SANBI Projects Service

The projects service adds pathogens, projects and user management to the studies workflow.


## Get Started

```bash
docker-compose up --build
```

```bash
docker exec -it app bash
```

```bash
flask db init
flask db migrate -m "Run migrations"
flask db upgrade
```
Should be accessible on `http://localhost:5000`
Swagger is available at: `http://localhost:5000/swagger`

## Permissions

Currently the ability to edit and manage projects and pathogens is defined in `config.py` with the values:

```python
PROJECT_GROUP = 'ego_group_id'
PATHOGEN_GROUP = 'ego_group_id'
```

## Workflow and endpoints

### Projects

A project is a pathogen related grouping of studies:

```json
{
    "title": "Project name",
    "pid": "Project identifier",
    "pathogen_id": "Required Pathogen ID",
    "description": "Project description"
}
```

A project requires a valid, existing `pathogen_id`.

This endpoint will also create a EGO admin group and policy and add it to the project.

### Pathogens

A pathogen and related schema. Projects require a pathogen

### Studies

When studies are created through the projects-service, they are recorded in the studies table as part of a project. EGO admin groups and member groups and policies are automatically created.


## JWT Token

The Projects Service requires a valid EGO generated JWT token.
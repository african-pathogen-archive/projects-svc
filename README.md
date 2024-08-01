# SANBI Projects Service

The projects service adds pathogens, projects and user management to the Overture studies workflow.


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

## Permissions

Currently the ability to edit and manage projects and pathogens is defined in `config.py` with the values:

```python
PROJECT_GROUP = 'ego_group_id'
PATHOGEN_GROUP = 'ego_group_id'
```

Use a `.env` file to control config variables.

## JWT Token

The Projects Service requires a valid EGO generated JWT token.

## Workflow and endpoints

### Pathogens

#### Add, edit and delete pathogens.

```
GET /api/pathogens
```
Returns all pathogens

```
GET /api/pathogens/<string:id>
```
Returns a single pathogen

```
POST /api/pathogens
```
Creates a new pathogens

```
PUT /api/pathogens/<string:id>
```

Edits a pathogen

```
DELETE /api/pathogens/<string:id>
```
Soft deletes a pathogen

---

Pathogens are only used in this **projects service** and does not currently use any external Overture endpoints apart from *optionally* referencing a **Song** schema.

A newly created pathogen in the **projects service** db will have:

```javascript
id: A uuid string
common_name: The common name
scientific_name: The scientific name
schema: An associated Song metadata schema name
schema_version: The schema version
created_at: Date created
updated_at: Date updated
delete_at: Date soft deleted
```

### Projects

#### Projects are a pathogen-specific collection of studies.

```
GET /api/projects
```
Gets all the projects

```
GET /api/projects/<string:id>
```
Gets a project by uuid

```
POST /api/projects
```
Add a new project

```
POST /api/projects/<string:id>/users/<string:user_id>
```
Add a user to the project admin group

```
PUT /api/projects/<string:id>
```
Edits a project

```
DELETE /api/projects/<string:id>
```
soft deletes a project

```
DELETE /api/projects/<string:id>/users/<string:user_id>
```
Removes a user from project admin group

---
When creating a project, the **projects service** will:

- Create a new project in the **projects service** db
- Create an **Ego** group for project administrators
- Create and **Ego** policy for project administration
- Add the current user to the group

Newly created projects in the **projects service** db will have:

```
id: A uuid string
common_namtitlee: A project title
pid: A short, unique identifier
pathogen_id: The related pathogen uuid
admin_group: The Ego admin group uuid
description: A project description
owner: The Ego uuid of the user who created the project
created_at: Date created
updated_at: Date updated
delete_at: Date soft deleted
```

### Studies

#### Studies are related to their projects

```
GET /api/studies
```
Returns all studies

```
GET /api/studies/<string:study_id>
```
Returns a single study

```
POST /api/studies/<string:study_id>/users/<string:user_id>/admin
POST /api/studies/<string:study_id>/users/<string:user_id>/member
```
Adds a user to a study. Role can be either admin or member

```
DELETE /api/studies/<string:study_id>/users/<string:user_id>/
```
Removes a user from a study group

```
DELETE /api/studies/<string:study_id>
```
soft deletes a study in the projects service db

---
Studies are added to a project by project administrators. When adding a new project **projects service** will:

- Create a new study in Song
- Create a new project in the **projects service** db
- Create a new **Ego** group for study administrators
- Create a new **Ego** grou for study members
- Create new **Ego** policies
- Add the current user to the administrators group

A new study in the **projects service** db will have:

```
id: A uuid string
study: The Song study name
project_id: The related project uuid
admin_group: The Ego admin group uuid
member_group: The Ego member group uuid
created_at: Date created
updated_at: Date updated
delete_at: Date soft deleted
```

## API Documentation

Please read the Swagger docs here: `http://localhost:5000/swagger`.

API documentation may be incomplete.

## Testing

Test are in `/app/tests/` and can be run with `pytest app/tests/`
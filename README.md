# SANBI Projects Service

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
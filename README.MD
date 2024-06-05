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

Currently the generated token needs to be manually saved as a cookie...todo.
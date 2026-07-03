# Munch visual annotations
This is a project about creating a visual annotation system for images, specifically orthophotos or topographical visualizations for a Edvard Munch painiting object is university of Oslo. The system will allow users to create polygonal annotations on the images, categorize them, and filter them based on various criteria such as year, category, and tags. The backend will consist of several models to manage images, meshes, visual annotations, categories, tags, and painting objects.

# Set up

## Create local database
Optional if you use the container version.

TBD

Switch on postgis extension for your database with:
```bash
CREATE EXTENSION postgis;
```

## Create environment

In order to control which database is used locally, in a container or productive system, create and adjust a hidden environment file .env:

```bash
SECRET_KEY=<your-secret-key>
DB_NAME=<prod-db-name>
DB_USER=<prod-db-user>
DB_PASS=<prod-db-pass>
HOST=<prod-db-host>
PORT=<prod-db-port>
DB_LOCAL_NAME=<local-db-name>
DB_LOCAL_USER=<local-db-user>
DB_LOCAL_PASS=<local-db-pass>
DB_HOST=<local-db-host>
DB_PORT=<local-db-port>
POSTGRES_DB=<local-db-name>
POSTGRES_USER=<local-db-user>
POSTGRES_PASSWORD=<local-db-pass>
```

Of course you only need to provide the values you actually use, like only the local, container or productive version.

## Local installation 

Create e.g. a conda environment with

```bash
conda env create -f environment.yml
```
## Use Podman containers

To start the containers run 
```bash
podman-compose build
```
(use `--no-cache` after an update)
and
```bash
podman-compose up
```

### Use latest database version
Make a dump of the production database. Copy it into the container with
```bash
podman cp <path-to-your-dump>.sql <db-container-name>:/tmp/dump.sql
```
Then enter the db container with
```bash
podman exec -it <db-container-name> bash
```
and load the dump file into the database.


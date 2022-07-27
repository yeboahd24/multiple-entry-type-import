# Import health data from multiple entries
### Stack
- Python 3.8
- Django 3.2
- PostgreSQL

### Description
This application allows users to import health data from multiple entries such as Garmin, Strava, etc. Data can be imported in various formats like CSV, FIT, GPX, TCX.

### Running
- Copy sample config
```bash
cp docs/docker/settings.ini .
```
- Build
```bash
docker compose up -d --build
# or in older version: docker-compose up -d
```
Possible issues:
- if database does not exist error occurs, try to create `entry` database in `entry_postgres` container
- if you can not log in to admin panel, try to create superuser in `entry_django` container
### Usage
You can upload exported file in django admin panel `localhost:8000/secure/` (it can be implemented in API endpoints and other parts of project easily). Sample files are stored in `docs/dataset/` folder.

### Benchmarking
#### Tested on Lenovo laptop:
#### intel core i3, 8GB RAM running Ubuntu 20.04 LTS
- manipulated 10431 points from `.fit` file
```text
2.10 s in get_dataframe_from_file
933.79 ms in dataframe_to_model_objs
434.16 mks in dataframe_to_model_objs
1.39 s in submit_model_objs_to_db
1.32 ms in submit_model_objs_to_db
```
- manipulated 9719 points from `.gpx` file
```text
959.71 ms in get_dataframe_from_file
748.51 ms in dataframe_to_model_objs
1.60 s in submit_model_objs_to_db
```
- manipulated 9719 points from `.tcx` file
```text
1.71 s in get_dataframe_from_file
965.18 ms in dataframe_to_model_objs
505.21 mks in dataframe_to_model_objs
1.40 s in submit_model_objs_to_db
1.08 ms in submit_model_objs_to_db
```

### Development
It can be optimizer if we run process in async tasks or leave it in queue to be processed.# multiple-entry-type-import

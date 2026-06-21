# docker postgres commands
docker exec -it postgres psql -U admin -d buildings_db
\dt
SELECT guid_oks FROM buildings LIMIT 1;

# request example
Какие объекты находятся в Челябинской области?
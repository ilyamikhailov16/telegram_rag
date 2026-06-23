# Telegram RAG (retrieval-augmented generation)

Бот использует RAG-подход (text-to-sql) для ответа на запросы по базе строящихся объектов.

## Быстрый старт

- Убедитесь, что у вас установлены Docker и Docker Compose.
- Запустите сервисы (Postgres и бот) через `docker-compose up` или  `docker-compose up --build`.

## Команды для доступа к Postgres

Подключиться к контейнеру Postgres и открыть psql:

```
docker exec -it postgres psql -U admin -d buildings_db
```

Просмотреть таблицы:

```
\dt
```

Выполнить пример SQL-запроса:

```
SELECT guid_oks FROM buildings LIMIT 1;
```

## Пример запроса к боту

```
Какие объекты находятся в Челябинской области?
```

# ToolTown Makerspace API

BDF Group Assignment, card **JP-GAI2B-G06** (Theme 6 of 30: Tool library), twist **Three at a time**.

A REST API that records makers, tools and loans so the makerspace can see who has which tool.

**Stack:** Node.js, Express, SQLite (`sqlite3` package), tested with Postman.

## How to run

```bash
cd complete-project
npm install
npm start          # http://localhost:3000
```

The database file `tooltown.db` and sample data (3 makers, 5 tools) are created on first start.
Delete `tooltown.db` to reset the data before re-running the Postman tests.

## Database (3 related tables)

| Table  | Columns |
|--------|---------|
| makers | id, name |
| tools  | id, name, kind |
| loans  | id, maker_id → makers.id, tool_id → tools.id, loaned_at, returned_at (empty while the loan is active) |

## Endpoints

| Method | Path | Success | Errors |
|--------|------|---------|--------|
| GET | `/tools` | 200 all tools | |
| GET | `/tools?kind=power` | 200 tools of that kind | |
| GET | `/tools/:id` | 200 | 404 |
| POST | `/tools` `{name, kind}` | 201 | 400 |
| PUT | `/tools/:id` `{name, kind}` | 200 | 400, 404 |
| DELETE | `/tools/:id` | 200 | 404 |
| GET | `/makers`, `/makers/:id` | 200 | 404 |
| POST | `/makers` `{name}` | 201 | 400 |
| GET | `/loans` | 200 join: loans with `maker_name` and `tool_name` | |
| POST | `/loans` `{maker_id, tool_id}` | 201 | 400, 404, 409 |
| POST | `/loans/:id/return` | 200 | 404, 409 |

Valid tool kinds: `power`, `hand`, `electronic`, `measuring`, `garden`.

## The twist: Three at a time

A maker can hold at most 3 active loans. The 4th attempt returns **409** with `"Limit of 3 reached"`.
Returning a loan frees a place. The check and the insert happen in one SQL statement:

```sql
INSERT INTO loans (maker_id, tool_id)
SELECT ?, ? WHERE (SELECT COUNT(*) FROM loans WHERE maker_id = ? AND returned_at IS NULL) < 3
```

| Test | Action | Expected |
|------|--------|----------|
| 1 | 3 loans for Asha | 201, 201, 201 |
| 2 | 4th loan for Asha | 409 |
| 3 | Return one, create a new one | 201 |

## Postman

1. Start the server on a fresh database.
2. Import `postman/ToolTown.postman_collection.json`.
3. The collection variable `baseUrl` is `http://localhost:3000`.
4. Run the folders in order (each request has a status-code test). Folder 2 holds the twist tests.

## Repository layout

| Folder | Part |
|--------|------|
| `task1-server-and-routes` | Express setup, routes, status codes |
| `task2-database` | SQLite tables and queries |
| `task3-rest-endpoints` | CRUD and join endpoint |
| `task4-validation-and-search` | Input checks, messages, search |
| `task5-twist-rule` | Three-at-a-time rule |
| `task6-postman-and-readme` | Postman collection and this README |
| `complete-project` | Everything merged, ready to run |

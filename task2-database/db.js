// Task 2: SQLite database with 3 related tables: makers, tools, loans
const sqlite3 = require('sqlite3').verbose();
const path = require('path');

const db = new sqlite3.Database(path.join(__dirname, 'tooltown.db'));

// Promise helpers so routes can use async/await
const run = (sql, params = []) =>
  new Promise((resolve, reject) =>
    db.run(sql, params, function (err) {
      if (err) reject(err);
      else resolve({ lastID: this.lastID, changes: this.changes });
    })
  );
const get = (sql, params = []) =>
  new Promise((resolve, reject) => db.get(sql, params, (e, row) => (e ? reject(e) : resolve(row))));
const all = (sql, params = []) =>
  new Promise((resolve, reject) => db.all(sql, params, (e, rows) => (e ? reject(e) : resolve(rows))));

async function init() {
  await run('PRAGMA foreign_keys = ON');
  await run(`CREATE TABLE IF NOT EXISTS makers (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
  )`);
  await run(`CREATE TABLE IF NOT EXISTS tools (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    kind TEXT NOT NULL
  )`);
  await run(`CREATE TABLE IF NOT EXISTS loans (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    maker_id    INTEGER NOT NULL REFERENCES makers(id),
    tool_id     INTEGER NOT NULL REFERENCES tools(id),
    loaned_at   TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    returned_at TEXT
  )`);

  // Sample data (only when the tables are empty)
  const m = await get('SELECT COUNT(*) AS n FROM makers');
  if (m.n === 0) {
    for (const n of ['Asha', 'Ravi', 'Meena']) await run('INSERT INTO makers (name) VALUES (?)', [n]);
  }
  const t = await get('SELECT COUNT(*) AS n FROM tools');
  if (t.n === 0) {
    const tools = [['Cordless Drill', 'power'], ['Hand Saw', 'hand'], ['Orbital Sander', 'power'],
                   ['Claw Hammer', 'hand'], ['Soldering Iron', 'electronic']];
    for (const [n, k] of tools) await run('INSERT INTO tools (name, kind) VALUES (?, ?)', [n, k]);
  }
}

module.exports = { db, run, get, all, init };

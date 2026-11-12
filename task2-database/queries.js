// Task 2: the SQL used by the routes, kept in one place
module.exports = {
  allTools:      'SELECT id, name, kind FROM tools ORDER BY id',
  toolsByKind:   'SELECT id, name, kind FROM tools WHERE LOWER(kind) = LOWER(?) ORDER BY id',
  toolById:      'SELECT id, name, kind FROM tools WHERE id = ?',
  insertTool:    'INSERT INTO tools (name, kind) VALUES (?, ?)',
  updateTool:    'UPDATE tools SET name = ?, kind = ? WHERE id = ?',
  deleteTool:    'DELETE FROM tools WHERE id = ?',
  allMakers:     'SELECT id, name FROM makers ORDER BY id',
  makerById:     'SELECT id, name FROM makers WHERE id = ?',
  insertMaker:   'INSERT INTO makers (name) VALUES (?)',
  // JOIN: loans with the maker name and the tool name
  loansJoined: `SELECT loans.id, loans.maker_id, makers.name AS maker_name,
                       loans.tool_id,  tools.name  AS tool_name,
                       loans.loaned_at, loans.returned_at
                FROM loans
                JOIN makers ON makers.id = loans.maker_id
                JOIN tools  ON tools.id  = loans.tool_id
                ORDER BY loans.id`,
  loanById:      'SELECT * FROM loans WHERE id = ?',
  toolInActiveLoan: 'SELECT id FROM loans WHERE tool_id = ? AND returned_at IS NULL',
  // Task 5 twist: insert only when the maker has fewer than 3 active loans
  insertLoanLimited: `INSERT INTO loans (maker_id, tool_id)
                      SELECT ?, ? WHERE (SELECT COUNT(*) FROM loans
                                         WHERE maker_id = ? AND returned_at IS NULL) < 3`,
  returnLoan: "UPDATE loans SET returned_at = datetime('now') WHERE id = ? AND returned_at IS NULL"
};

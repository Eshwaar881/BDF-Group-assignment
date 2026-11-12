// Task 3: the join endpoint (loans with maker name and tool name)
const express = require('express');
const { all } = require('../db');
const q = require('../queries');
const router = express.Router();

// GET /loans -> 200, each row has maker_name and tool_name
router.get('/', async (req, res, next) => {
  try { res.status(200).json(await all(q.loansJoined)); } catch (e) { next(e); }
});

module.exports = router;

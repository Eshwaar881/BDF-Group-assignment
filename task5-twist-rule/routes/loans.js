// Task 5: twist "Three at a time" - a maker can hold at most 3 active loans
const express = require('express');
const { run, get, all } = require('../db');
const q = require('../queries');
const router = express.Router();

// GET /loans -> join endpoint (maker name + tool name)
router.get('/', async (req, res, next) => {
  try { res.status(200).json(await all(q.loansJoined)); } catch (e) { next(e); }
});

// POST /loans -> 201, 400, 404, 409
router.post('/', async (req, res, next) => {
  try {
    const { maker_id, tool_id } = req.body || {};
    if (!Number.isInteger(maker_id) || !Number.isInteger(tool_id)) {
      return res.status(400).json({ error: 'maker_id and tool_id must be whole numbers' });
    }
    if (!(await get(q.makerById, [maker_id]))) return res.status(404).json({ error: 'Maker not found' });
    if (!(await get(q.toolById, [tool_id])))   return res.status(404).json({ error: 'Tool not found' });
    if (await get(q.toolInActiveLoan, [tool_id])) {
      return res.status(409).json({ error: 'Tool is already on loan' });
    }

    // Count and insert in ONE statement, so two simultaneous requests cannot both pass the check
    const r = await run(q.insertLoanLimited, [maker_id, tool_id, maker_id]);
    if (r.changes === 0) return res.status(409).json({ error: 'Limit of 3 reached' });

    res.status(201).json(await get(q.loanById, [r.lastID]));
  } catch (e) { next(e); }
});

// POST /loans/:id/return -> 200, 404, 409 (returning frees a place)
router.post('/:id/return', async (req, res, next) => {
  try {
    const r = await run(q.returnLoan, [req.params.id]);
    if (r.changes === 0) {
      const loan = await get(q.loanById, [req.params.id]);
      if (!loan) return res.status(404).json({ error: 'Loan not found' });
      return res.status(409).json({ error: 'Already returned' });
    }
    res.status(200).json(await get(q.loanById, [req.params.id]));
  } catch (e) { next(e); }
});

module.exports = router;

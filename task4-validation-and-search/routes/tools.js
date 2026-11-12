// Task 4: tools routes with validation (POST, PUT) and search (GET /tools?kind=power)
const express = require('express');
const { run, get, all } = require('../db');
const q = require('../queries');
const { validateTool } = require('../middleware/validate');
const router = express.Router();

// GET /tools          -> all tools
// GET /tools?kind=x   -> search by kind (case-insensitive)
router.get('/', async (req, res, next) => {
  try {
    const { kind } = req.query;
    const rows = kind ? await all(q.toolsByKind, [kind]) : await all(q.allTools);
    res.status(200).json(rows);
  } catch (e) { next(e); }
});

router.get('/:id', async (req, res, next) => {
  try {
    const tool = await get(q.toolById, [req.params.id]);
    if (!tool) return res.status(404).json({ error: 'Tool not found' });
    res.status(200).json(tool);
  } catch (e) { next(e); }
});

router.post('/', validateTool, async (req, res, next) => {
  try {
    const r = await run(q.insertTool, [req.body.name, req.body.kind]);
    res.status(201).json(await get(q.toolById, [r.lastID]));
  } catch (e) { next(e); }
});

router.put('/:id', validateTool, async (req, res, next) => {
  try {
    const r = await run(q.updateTool, [req.body.name, req.body.kind, req.params.id]);
    if (r.changes === 0) return res.status(404).json({ error: 'Tool not found' });
    res.status(200).json(await get(q.toolById, [req.params.id]));
  } catch (e) { next(e); }
});

router.delete('/:id', async (req, res, next) => {
  try {
    const r = await run(q.deleteTool, [req.params.id]);
    if (r.changes === 0) return res.status(404).json({ error: 'Tool not found' });
    res.status(200).json({ message: 'Tool deleted' });
  } catch (e) { next(e); }
});

module.exports = router;

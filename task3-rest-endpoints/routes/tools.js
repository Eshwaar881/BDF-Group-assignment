// Task 3: CRUD for tools, each with the right status code
const express = require('express');
const { run, get, all } = require('../db');
const q = require('../queries');
const router = express.Router();

// GET /tools -> 200
router.get('/', async (req, res, next) => {
  try { res.status(200).json(await all(q.allTools)); } catch (e) { next(e); }
});

// GET /tools/:id -> 200 or 404
router.get('/:id', async (req, res, next) => {
  try {
    const tool = await get(q.toolById, [req.params.id]);
    if (!tool) return res.status(404).json({ error: 'Tool not found' });
    res.status(200).json(tool);
  } catch (e) { next(e); }
});

// POST /tools -> 201
router.post('/', async (req, res, next) => {
  try {
    const { name, kind } = req.body;
    const r = await run(q.insertTool, [name, kind]);
    res.status(201).json(await get(q.toolById, [r.lastID]));
  } catch (e) { next(e); }
});

// PUT /tools/:id -> 200 or 404
router.put('/:id', async (req, res, next) => {
  try {
    const { name, kind } = req.body;
    const r = await run(q.updateTool, [name, kind, req.params.id]);
    if (r.changes === 0) return res.status(404).json({ error: 'Tool not found' });
    res.status(200).json(await get(q.toolById, [req.params.id]));
  } catch (e) { next(e); }
});

// DELETE /tools/:id -> 200 or 404
router.delete('/:id', async (req, res, next) => {
  try {
    const r = await run(q.deleteTool, [req.params.id]);
    if (r.changes === 0) return res.status(404).json({ error: 'Tool not found' });
    res.status(200).json({ message: 'Tool deleted' });
  } catch (e) { next(e); }
});

module.exports = router;

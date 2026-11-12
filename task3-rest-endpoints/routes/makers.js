// Task 3: makers routes
const express = require('express');
const { run, get, all } = require('../db');
const q = require('../queries');
const router = express.Router();

router.get('/', async (req, res, next) => {
  try { res.status(200).json(await all(q.allMakers)); } catch (e) { next(e); }
});

router.get('/:id', async (req, res, next) => {
  try {
    const maker = await get(q.makerById, [req.params.id]);
    if (!maker) return res.status(404).json({ error: 'Maker not found' });
    res.status(200).json(maker);
  } catch (e) { next(e); }
});

router.post('/', async (req, res, next) => {
  try {
    const name = (req.body.name || '').trim();
    if (!name) return res.status(400).json({ error: 'name is required' });
    const r = await run(q.insertMaker, [name]);
    res.status(201).json(await get(q.makerById, [r.lastID]));
  } catch (e) { next(e); }
});

module.exports = router;

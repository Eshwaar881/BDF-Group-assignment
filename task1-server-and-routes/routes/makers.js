// Task 1: route skeleton for /makers (handlers are filled in by later tasks)
const express = require('express');
const router = express.Router();

router.get('/', (req, res) => res.status(501).json({ error: 'Not implemented yet' }));

module.exports = router;

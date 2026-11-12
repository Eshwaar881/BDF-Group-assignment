// Task 4: input checks with clear error messages (400)
const KINDS = ['power', 'hand', 'electronic', 'measuring', 'garden'];

function validateTool(req, res, next) {
  const { name, kind } = req.body || {};
  if (typeof name !== 'string' || name.trim() === '') {
    return res.status(400).json({ error: 'name is required and must be a non-empty text' });
  }
  if (name.trim().length > 60) {
    return res.status(400).json({ error: 'name must be 60 characters or fewer' });
  }
  if (typeof kind !== 'string' || kind.trim() === '') {
    return res.status(400).json({ error: 'kind is required' });
  }
  if (!KINDS.includes(kind.trim().toLowerCase())) {
    return res.status(400).json({ error: `kind must be one of: ${KINDS.join(', ')}` });
  }
  req.body.name = name.trim();
  req.body.kind = kind.trim().toLowerCase();
  next();
}

module.exports = { validateTool, KINDS };

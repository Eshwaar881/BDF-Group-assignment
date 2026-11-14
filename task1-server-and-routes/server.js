// Task 1: Express setup, routes and status codes
const express = require('express');
const makersRouter = require('./routes/makers');
const toolsRouter = require('./routes/tools');
const loansRouter = require('./routes/loans');

const app = express();
app.use(express.json());

app.get('/', (req, res) => res.json({ service: 'ToolTown Makerspace API', status: 'running' }));

app.use('/makers', makersRouter);
app.use('/tools', toolsRouter);
app.use('/loans', loansRouter);

// Unknown route -> 404
app.use((req, res) => res.status(404).json({ error: 'Route not found' }));

// Bad JSON body and any other error
app.use((err, req, res, next) => {
  if (err.type === 'entity.parse.failed') return res.status(400).json({ error: 'Invalid JSON body' });
  console.error(err);
  res.status(500).json({ error: 'Server error' });
});

const PORT = process.env.PORT || 3000;
if (require.main === module) {
  app.listen(PORT, () => console.log(`ToolTown API listening on http://localhost:${PORT}`));
}
module.exports = app;

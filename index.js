const express = require('express');
const app = express();
const port = 8080;

app.get('/tshirt', (req, res) => {
  res.json({ tshirt: 'wow', size: 'large' });
});

app.listen(port, () => {
  console.log(`Server listening on port ${port}`);
});
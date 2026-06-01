const express = require('express');
const cors = require('cors');
const app = express();
app.use(express.json());
app.use(cors());

// Banco de dados em memória
const clientes = [
  { id: 1, nome: "João Silva", telefone: "41-99999-9999" },
  { id: 2, nome: "Maria Souza", telefone: "41-88888-8888" }
];

app.post('/clientes', (req, res) => {
  const { nome, telefone } = req.body;
  const novoCliente = { id: clientes.length + 1, nome, telefone };
  clientes.push(novoCliente);
  res.status(201).json(novoCliente);
});

app.get('/clientes', (req, res) => {
  res.json(clientes);
});

app.get('/clientes/:id', (req, res) => {
  const cliente = clientes.find(c => c.id === parseInt(req.params.id));
  if (!cliente) return res.status(404).json({ erro: "Cliente não encontrado" });
  res.json(cliente);
});

app.listen(5001, () => console.log("Serviço de Clientes rodando na porta 5001"));
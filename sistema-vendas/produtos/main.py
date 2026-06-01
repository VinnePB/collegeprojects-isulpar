from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Banco de dados em memória
produtos = [
    {"id": 1, "nome": "Notebook", "descricao": "i7 16GB RAM", "preco": 4500.0},
    {"id": 2, "nome": "Mouse Gamer", "descricao": "RGB 4000 DPI", "preco": 150.0}
]

class Produto(BaseModel):
    nome: str
    descricao: str
    preco: float

@app.post("/produtos")
def criar_produto(produto: Produto):
    novo_produto = {
        "id": len(produtos) + 1,
        "nome": produto.nome,
        "descricao": produto.descricao,
        "preco": produto.preco
    }
    produtos.append(novo_produto)
    return novo_produto

@app.get("/produtos")
def listar_produtos():
    return produtos

@app.get("/produtos/{produto_id}")
def obter_produto(produto_id: int):
    produto = next((p for p in produtos if p["id"] == produto_id), None)
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return produto
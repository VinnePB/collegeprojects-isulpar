from flask import Flask, request, jsonify
from flask_cors import CORS
import queue
import threading
import requests
import time

app = Flask(__name__)
CORS(app)

# Fila FIFO paralela para processamento assíncrono de vendas
fila_vendas = queue.Queue()
historico_vendas = []

# Worker em background que processa as vendas da fila de forma paralela
def worker_processamento():
    while True:
        # Pega a venda da fila (bloqueia a thread se estiver vazia)
        dados_venda = fila_vendas.get()
        if dados_venda is None:
            break
        
        try:
            cliente_id = dados_venda['cliente_id']
            produto_id = dados_venda['produto_id']
            
            # Comunicação síncrona Inter-processos (Buscando dados nos outros containers via HTTP)
            res_cliente = requests.get(f"http://clientes:5001/clientes/{cliente_id}", timeout=2)
            res_produto = requests.get(f"http://produtos:5002/produtos/{produto_id}", timeout=2)
            
            if res_cliente.status_code == 200 and res_produto.status_code == 200:
                cliente = res_cliente.json()
                produto = res_produto.json()
                
                venda_finalizada = {
                    "id_transacao": len(historico_vendas) + 1,
                    "cliente": cliente['nome'],
                    "produto": produto['nome'],
                    "valor_total": produto['preco'],
                    "status": "PROCESSADO COM SUCESSO"
                }
                historico_vendas.append(venda_finalizada)
            else:
                historico_vendas.append({"status": "FALHA - Cliente ou Produto inexistente"})
                
        except Exception as e:
            historico_vendas.append({"status": f"FALHA NO PROCESSAMENTO DISTRIBUÍDO: {str(e)}"})
        
        # Indica que a tarefa da fila foi concluída
        fila_vendas.task_done()

# Inicia a thread trabalhadora em background assim que o microsserviço sobe
threading.Thread(target=worker_processamento, daemon=True).start()

@app.post('/vendas')
def registrar_venda():
    dados = request.json
    if not dados or 'cliente_id' not in dados or 'produto_id' not in dados:
        return jsonify({"erro": "Dados inválidos"}), 400
    
    # Enfileira a requisição na fila FIFO para processamento assíncrono paralelo
    fila_vendas.put(dados)
    return jsonify({"mensagem": "Venda enviada para a fila de processamento distribuído!"}), 202

@app.get('/vendas')
def listar_vendas():
    return jsonify(historico_vendas)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
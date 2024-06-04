import mercadopago

# Adicione as credenciais
public_key = "APP_USR-19d81ac1-b3ca-4a73-a367-f9a15f56c2a8"

token = "APP_USR-6109729073100708-060213-dc2594ff68269e94faa7d59f1c3ba110-1835340744"

sdk = mercadopago.SDK(token)

# preciso informar os ítens que o cliente está comprando, no formato de dicionário;
# a quantidade;
# o valor;


def criar_pagamento(itens_pedido, link):

    itens = []
    for item in itens_pedido:
        nome = item.item_estoque.produto.nome
        quantidade = int(item.quantidade)
        preco_unitario = float(item.item_estoque.produto.preco)
        itens.append(
            {"title": nome,
             "quantity": quantidade,
             "unit_price": preco_unitario
             }
        )

    preference_data = {
        "items": itens,
        "auto_return": "all",
        "back_urls": {
            "success": link,
            "pending": link,
            "failure": link,
        }
    }

    resposta = sdk.preference().create(preference_data)

    link_pagamento = resposta["response"]["init_point"]
    id_pagamento = resposta["response"]["id"]
    # print(link_pagamento)
    return link_pagamento, id_pagamento

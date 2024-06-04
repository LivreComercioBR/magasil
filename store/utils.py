from django.core.mail import send_mail
from django.db.models import Min, Max
from django.http import HttpResponse
import csv


def filtrar_produtos(produtos, filtro):
    if filtro:
        if "-" in filtro:
            categoria, tipo = filtro.split("-")
            produtos = produtos.filter(
                categoria__slug=categoria, tipo__slug=tipo)
        else:
            produtos = produtos.filter(categoria__slug=filtro)
    return produtos


def precos_minimo_maximo(produtos):
    minimo = 0
    maximo = 0

    if len(produtos) > 0:
        minimo = list(produtos.aggregate(Min("preco")).values())[0]
        # minimo = round(minimo, 2) se os valores aparecerem com muitas casas decimais
        maximo = list(produtos.aggregate(Max("preco")).values())[0]
        # maximo = round(maximo, 2) se os valores aparecerem com muitas casas decimais
        # tem que transformar os valores em lista python porque a função aggregate devolve o valor em forma de dicionário
    return minimo, maximo


def ordenar_produtos(produtos, ordem):
    if ordem == "menor-preco":
        produtos = produtos.order_by("preco")
    elif ordem == "maior-preco":
        produtos = produtos.order_by("-preco")
        # -preco para ordenar em ordem decrescente
    elif ordem == "mais-vendidos":
        lista_mais_vendidos = []
        for produto in produtos:
            lista_mais_vendidos.append((produto.total_vendas(), produto))
        lista_mais_vendidos = sorted(
            lista_mais_vendidos, reverse=True, key=lambda tupla: tupla[0])
        produtos = [item[1] for item in lista_mais_vendidos]

    return produtos


def enviar_email_compra(pedido):
    email = pedido.cliente.email
    assunto = "Pagamento Aprovado"
    corpo = f"""Ola {pedido.cliente.nome}, seu pedido foi aprovado!.
    Nº do pedido: {pedido.id}
    Valor do pedido: {pedido.total}
    Produtos: {pedido.itens}"""
    remetente = "ronaldocorreiadesouza@gmail.com"

    send_mail(assunto, corpo, remetente, [email, ], fail_silently=False)


def exportar_csv(informacoes):
    colunas = informacoes.model._meta.fields
    nomes_colunas = [coluna.name for coluna in colunas]

    resposta = HttpResponse(content_type="text/csv")
    resposta["Content-Disposition"] = "attachment; filename=export.csv"
    # criador do csv
    criador_csv = csv.writer(resposta, delimiter=";")
    # para criar as linhas

    criador_csv.writerow(nomes_colunas)

    for linha in informacoes.values_list():
        criador_csv.writerow(linha)

    return resposta

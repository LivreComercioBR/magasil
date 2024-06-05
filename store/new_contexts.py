from django.shortcuts import redirect, render
from store.models import Produto, Pedido, Carrinho, Cliente, Categoria, Tipo

"""sempre que o cliente criar uma conta no site,
 eu vou adicionar um usuário para ele. Tabela OneToOneField"""


def shopping_cart(request):
    qtd_prod_carrinho = 0
    # if request.user.is_authenticated:
    #     cliente = request.user.cliente
    #     # user.cliente da tabela OnetoOneField Client
    # else:
    #     if request.COOKIES.get("id_sessao"):
    #         id_sessao = request.COOKIES.get("id_sessao")
    #         cliente, criado = Cliente.objects.get_or_create(
    #             id_sessao=id_sessao)
    #     else:
    #         return {"qtd_prod_carrinho": qtd_prod_carrinho}
    # pedido, criado = Pedido.objects.get_or_create(
    #     cliente=cliente, finalizado=False)
    # # Se tiver o pedido ele vai pegar o pedido, se não tiver, ele vai criar o pedido.
    # """Agora preciso saber quais são os itens do pedido"""
    # itens_carrinho = Carrinho.objects.filter(pedido=pedido)
    # """Posso ter um pedido com apenas 1 produto, porém, sendo 5 produtos do mesmo produto"""
    # for item in itens_carrinho:
    #     qtd_prod_carrinho += item.quantidade

    return {"qtd_prod_carrinho": qtd_prod_carrinho}


def categorias_tipos(request):
    categorias_navegacao = Categoria.objects.all()
    tipos_navegacao = Tipo.objects.all()

    return {"categorias_navegacao": categorias_navegacao, "tipos_navegacao": tipos_navegacao}


def equipe_vendas(request):
    vendas = False
    if request.user.is_authenticated:
        if request.user.groups.filter(name="vendas").exists():
            vendas = True
    return {"vendas": vendas}

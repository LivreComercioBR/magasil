from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from store.utils import filtrar_produtos, precos_minimo_maximo, ordenar_produtos, enviar_email_compra, exportar_csv
from .models import *
from django.contrib import messages
from django.contrib.messages import constants
import uuid
from django.db.models import Min, Max
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from datetime import datetime
from .api_mercadopago import criar_pagamento
from django.urls import reverse
from django.contrib.auth.decorators import login_required


def home(request):
    banners = Banner.objects.filter(ativo=True)

    context = {"banners": banners}
    return render(request, 'home.html', context)


# TODO VOLTAR na aula 45 para corrigir a barra de navegação que está com um bug dos menus
def produtos(request, filtro=None):
    produtos = Produto.objects.filter(ativo=True)
    produtos = filtrar_produtos(produtos, filtro)

    if request.method == "POST":
        dados = request.POST.dict()
        produtos = produtos.filter(preco__gte=dados.get(
            "preco_minimo"), preco__lte=dados.get("preco_maximo"))
        print(dados)
        if "tamanho" in dados:
            itens = Estoque.objects.filter(
                produto__in=produtos, tamanho=dados.get("tamanho"))
            ids_produtos = itens.values_list("produto", flat=True).distinct()
            produtos = produtos.filter(id__in=ids_produtos)

        if "categoria" in dados:
            produtos = produtos.filter(categoria__slug=dados.get("categoria"))
        if "tipo" in dados:
            produtos = produtos.filter(tipo__slug=dados.get("tipo"))
    tamanhos_itens = Estoque.objects.filter(
        estoque_disponivel__gt=0, produto__in=produtos)
    tamanhos_itens = tamanhos_itens.values_list(
        "tamanho", flat=True).distinct()
    # função flat para formatar os valores e função distinct() para pegar um único valor por tamanho

    ids_categorias = produtos.values_list("categoria", flat=True).distinct()
    categorias = Categoria.objects.filter(id__in=ids_categorias)

    minimo, maximo = precos_minimo_maximo(produtos)
    tamanhos = tamanhos_itens

    ordem = request.GET.get("ordem", "menor-preco")
    produtos = ordenar_produtos(produtos, ordem)

    context = {"produtos": produtos, "minimo": minimo,
               "maximo": maximo, "tamanhos": tamanhos, "categorias": categorias}
    return render(request, 'produtos.html', context)


def ver_produto(request, id_produto, id_cor=None):
    tem_estoque = False
    cores = {}
    tamanhos = {}
    cor_selecionada = None
    if id_cor:
        cor = Cor.objects.get(id=id_cor)
        cor_selecionada = cor

    produto = get_object_or_404(Produto, id=id_produto)

    estoque = Estoque.objects.filter(
        produto=produto).filter(estoque_disponivel__gt=0)

    if len(estoque) > 0:
        tem_estoque = True
        # Variável tem estoque para não mostrar produtos sem estoque, ou seja, produto com estoque == 0.
        cores = {item.cor for item in estoque}
        # Definido um {} set para não repetir as cores
        if id_cor:
            estoque = Estoque.objects.filter(
                produto=produto, estoque_disponivel__gt=0, cor__id=id_cor)
            tamanhos = {item.tamanho for item in estoque}

    similares = Produto.objects.filter(
        categoria__id=produto.categoria.id, tipo__id=produto.tipo.id).exclude(id=produto.id)[:4]

    # for similar in similares:
    #     preco_parcelado = similar.preco / 5

    context = {"produto": produto, "estoque": estoque,
               "tem_estoque": tem_estoque, "cores": cores, "tamanhos": tamanhos, "cor_selecionada": cor_selecionada, "similares": similares}
    return render(request, 'ver_produto.html', context)


def add_carrinho(request, id_produto):
    if request.method == "POST" and id_produto:
        dados = request.POST.dict()
        tamanho = dados.get("tamanho")
        id_cor = dados.get("cor")
        if not tamanho:
            return redirect("produtos")

        resposta = redirect("carrinho")

        if request.user.is_authenticated:
            cliente = request.user.cliente
        else:
            if request.COOKIES.get("id_sessao"):
                # request.COOKIES pega todos os cookies que estão armazenados em meu navegador
                id_sessao = request.COOKIES.get("id_sessao")
            else:
                """Aqui começa o cliente anônimo"""
                id_sessao = str(uuid.uuid4())
                resposta.set_cookie(
                    key="id_sessao", value=id_sessao, max_age=60*60*24*60)
            cliente, criado = Cliente.objects.get_or_create(
                id_sessao=id_sessao)

        pedido, criado = Pedido.objects.get_or_create(
            cliente=cliente, finalizado=False)
        produto = Estoque.objects.get(
            produto__id=id_produto, tamanho=tamanho, cor__id=id_cor)
        item_carrinho, criado = Carrinho.objects.get_or_create(
            item_estoque=produto, pedido=pedido)
        item_carrinho.quantidade += 1
        item_carrinho.save()

        return resposta
    else:
        return redirect("produtos")


def remover_carrinho(request, id_produto):
    if request.method == "POST" and id_produto:
        dados = request.POST.dict()
        tamanho = dados.get("tamanho")
        id_cor = dados.get("cor")
        if not tamanho:
            return redirect("produtos")
        if request.user.is_authenticated:
            cliente = request.user.cliente
        else:
            if request.COOKIES.get("id_sessao"):
                id_sessao = request.COOKIES.get("id_sessao")
                cliente, criado = Cliente.objects.get_or_create(
                    id_sessao=id_sessao)
            else:
                return redirect("produtos")
        pedido, criado = Pedido.objects.get_or_create(
            cliente=cliente, finalizado=False)
        produto = Estoque.objects.get(
            produto__id=id_produto, tamanho=tamanho, cor__id=id_cor)
        item_carrinho, criado = Carrinho.objects.get_or_create(
            item_estoque=produto, pedido=pedido)
        item_carrinho.quantidade -= 1
        item_carrinho.save()
        if item_carrinho.quantidade <= 0:
            item_carrinho.delete()
        return redirect("carrinho")
    else:
        return redirect("produtos")


def carrinho(request):
    if request.user.is_authenticated:
        cliente = request.user.cliente
    else:
        if request.COOKIES.get("id_sessao"):
            id_sessao = request.COOKIES.get("id_sessao")
            cliente, criado = Cliente.objects.get_or_create(
                id_sessao=id_sessao)
        else:
            context = {"cliente_existente": False,
                       "itens_carrinho": None, "pedido": None}
            return render(request, 'carrinho.html', context)

    pedido, criado = Pedido.objects.get_or_create(
        cliente=cliente, finalizado=False)
    itens_carrinho = Carrinho.objects.filter(pedido=pedido)
    """Estou passando a variáveel pedido aqui para poder pegar a quantidade de itens e o valor total do pedido"""

    context = {"itens_carrinho": itens_carrinho,
               "pedido": pedido, "cliente_existente": True}

    return render(request, 'carrinho.html', context)


def checkout(request):
    if request.user.is_authenticated:
        cliente = request.user.cliente
    else:
        if request.COOKIES.get("id_sessao"):
            id_sessao = request.COOKIES.get("id_sessao")
            cliente, criado = Cliente.objects.get_or_create(
                id_sessao=id_sessao)
        else:
            return redirect("produtos")

    pedido, criado = Pedido.objects.get_or_create(
        cliente=cliente, finalizado=False)
    enderecos = Endereco.objects.filter(cliente=cliente)
    context = {"pedido": pedido, "enderecos": enderecos,
               "cliente_existente": True}
    return render(request, 'checkout.html', context)


def cadastrar_endereco(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            cliente = request.user.cliente
        else:
            if request.COOKIES.get("id_sessao"):
                id_sessao = request.COOKIES.get("id_sessao")
                cliente, criado = Cliente.objects.get_or_create(
                    id_sessao=id_sessao)
            else:
                return redirect("produtos")
        try:
            dados = request.POST.dict()
            endereco = Endereco.objects.create(cliente=cliente, nome_endereco=dados.get("nome_endereco"), recebedor=dados.get("recebedor"), estado=dados.get("estado"), rua=dados.get(
                "rua"), ponto_referencia=dados.get("ponto_referencia"), cidade=dados.get("cidade"), cep=dados.get("cep"), numero=int(dados.get("numero")), bairro=dados.get("bairro"))
            endereco.save()
            messages.add_message(request, constants.SUCCESS,
                                 "Endereço de entrega cadastrado com sucesso!")
            return redirect("cadastrar_endereco")
        except:
            messages.add_message(request, constants.ERROR,
                                 "Houve um erro ao cadastrar o endereço")
            return redirect("cadastrar_endereco")
    else:
        return render(request, 'endereco.html')


def finalizar_pedido(request, id_pedido):
    if request.method == "POST":
        dados = request.POST.dict()
        total = dados.get("total")
        total = float(total.replace(",", "."))

        pedido = Pedido.objects.get(id=id_pedido)

        if total != float(pedido.total):
            messages.add_message(request, constants.ERROR,
                                 "Ops! O valor total não confere!")
            return redirect("realizar_pedido")
        if request.user.is_authenticated:
            if not "endereco" in dados:
                messages.add_message(request, constants.WARNING,
                                     "Por favor, selecione um endereço de entrega!")
            else:
                id_endereco = dados.get("endereco")
                endereco = Endereco.objects.get(id=id_endereco)
                pedido.endereco = endereco

        if not request.user.is_authenticated:
            email = dados.get("email")
            try:
                validate_email(email)

            except ValidationError:
                messages.add_message(request, constants.WARNING,
                                     "Por favor, informe um endereço de email!")
                return redirect("finalizar_pedido")
            else:
                clientes = Cliente.objects.filter(email=email)
                if clientes:
                    pedido.cliente = clientes[0]
                    pedido.save()
                else:
                    pedido.cliente.email = email
                    pedido.cliente.save()
        codigo_transacao = f"{pedido.id}-{datetime.now().timestamp()}"
        pedido.codigo_transacao = codigo_transacao
        pedido.save()
        itens_pedido = Carrinho.objects.filter(pedido=pedido)
        link = request.build_absolute_uri(reverse('finalizar_pagamento'))
        # função reverse para pegar o endereço da url
        link_pagamento, id_pagamento = criar_pagamento(itens_pedido, link)
        pagamento = Pagamento.objects.create(
            id_pagamento=id_pagamento, pedido=pedido)
        pagamento.save()

        return redirect(link_pagamento)
    else:
        return redirect("home")


def finalizar_pagamento(request):
    dados = request.GET.dict()
    status = dados.get("status")
    id_pagamento = dados.get("preference_id")

    if status == "approved":
        pagamento = Pagamento.objects.get(id_pagamento=id_pagamento)
        pagamento.aprovado = True
        pedido = pagamento.pedido
        pedido.finalizado = True
        pedido.data_finalizacao = datetime.now()
        pedido.save()
        pagamento.save()

        enviar_email_compra(pedido)
        if request.user.is_authenticated:
            return redirect("meus_pedidos")
        else:
            return redirect("pedido_aprovado", pedido.id)
    else:
        return redirect("checkout")


def pedido_aprovado(request, id_pedido):
    pedido = Pedido.objects.get(id=id_pedido)

    context = {"pedido": pedido}

    return render(request, 'pedido_aprovado.html', context)


@login_required
def gerenciar_loja(request):
    if request.user.groups.filter(name="vendas").exists():
        pedidos_finalizados = Pedido.objects.filter(finalizado=True)
        quantidade_pedidos = len(pedidos_finalizados)

        faturamento = sum([pedido.total for pedido in pedidos_finalizados])

        qtd_prod_vendidos = sum(
            [pedido.quantidade_itens for pedido in pedidos_finalizados])

        context = {"quantidade_pedidos": quantidade_pedidos,
                   "qtd_prod_vendidos": qtd_prod_vendidos, "faturamento": faturamento}
        return render(request, "gerenciar_loja.html", context)


@login_required
def exportar_relatorio(request, relatorio):
    if request.user.groups.filter(name="vendas").exists():
        if relatorio == "pedido":
            informacoes = Pedido.objects.filter(finalizado=True)
        elif relatorio == "cliente":
            informacoes = Cliente.objects.all()
        elif relatorio == "endereco":
            informacoes = Endereco.objects.all()

        return exportar_csv(informacoes)
    else:
        return redirect("produtos")

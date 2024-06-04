from django.contrib import admin
from django.urls import path
from store.views import *


urlpatterns = [
    # path loja/
    path('home/', home, name='home'),
    path('produtos/', produtos, name='produtos'),
    path('produtos/<str:filtro>/', produtos, name='produtos'),
    path('ver_produto/<int:id_produto>/', ver_produto, name='ver_produto'),
    path('ver_produto/<int:id_produto>/<int:id_cor>/',
         ver_produto, name='ver_produto'),
    path('add_carrinho/<int:id_produto>/', add_carrinho, name='add_carrinho'),
    path('remover_carrinho/<int:id_produto>/',
         remover_carrinho, name='remover_carrinho'),
    path('carrinho/', carrinho, name='carrinho'),
    path('checkout/', checkout, name='checkout'),
    path('cadastrar_endereco/', cadastrar_endereco, name="cadastrar_endereco"),
    path('finalizar_pedido/<int:id_pedido>/',
         finalizar_pedido, name='finalizar_pedido'),
    path('finalizar_pagamento/',
         finalizar_pagamento, name='finalizar_pagamento'),
    path('pedido_aprovado/<int:id_pedido>/',
         pedido_aprovado, name='pedido_aprovado'),
    path('gerenciar_loja/', gerenciar_loja, name='gerenciar_loja'),
    path('exportar_relatorio/<str:relatorio>/',
         exportar_relatorio, name='exportar_relatorio')

]

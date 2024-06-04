
from django.db import models
from loja_app.models import User


class Cliente(models.Model):
    nome = models.CharField(max_length=150, blank=True,
                            null=True, default='visitante')
    sobrenome = models.CharField(max_length=100, blank=True, null=True)
    cpf = models.CharField(max_length=16, blank=True, null=True)
    email = models.EmailField(max_length=264, blank=True, null=True)
    telefone = models.CharField(max_length=16, blank=True, null=True)
    usuario = models.OneToOneField(
        User, on_delete=models.CASCADE, blank=True, null=True)
    id_sessao = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self) -> str:
        return str(self.nome)


class Categoria(models.Model):  # (masculino, femenino, infantil)
    nome = models.CharField(max_length=100, blank=True, null=True)
    slug = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return str(self.slug)


class Tipo(models.Model):  # (calça, camiseta, shorts)
    nome = models.CharField(max_length=100, blank=True, null=True)
    slug = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return str(self.slug)


class Imagem(models.Model):
    img = models.ImageField(upload_to='fotos_produtos', blank=True, null=True)

    def __str__(self) -> str:
        return self.img.url


class Produto(models.Model):
    nome = models.CharField(max_length=150)
    imagem = models.ManyToManyField(Imagem,
                                    related_name='imagens_produto', blank=True)
    preco = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True)
    descricao = models.TextField(blank=True, null=True)
    ativo = models.BooleanField(default=True)
    categoria = models.ForeignKey(
        Categoria, on_delete=models.SET_NULL, blank=True, null=True)
    tipo = models.ForeignKey(
        Tipo, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return f"{self.nome} - Preco: {self.preco} - Ativo: {self.ativo} - Categoria: {self.categoria}"

    def total_vendas(self):
        itens = Carrinho.objects.filter(
            pedido__finalizado=True, item_estoque__produto=self.id)
        total = sum([item.quantidade for item in itens])

        return total

    # @property
    # def total_estoque(self):
    #     quantidades = Estoque.objects.filter(produto_id=self.id)

    #     total = sum([item.estoque_disponivel for item in quantidades])

    #     return total

    @property
    def parcelar(self):
        parcela = self.preco / 5
        return parcela


class Endereco(models.Model):
    nome_endereco = models.CharField(max_length=150, blank=True, null=True)
    recebedor = models.CharField(max_length=150, blank=True, null=True)
    rua = models.CharField(max_length=150, blank=True, null=True)
    cep = models.CharField(max_length=32, blank=True, null=True)
    numero = models.IntegerField(blank=True, null=True, default=0)
    ponto_referencia = models.CharField(max_length=200, blank=True, null=True)
    bairro = models.CharField(max_length=50, blank=True, null=True)
    cidade = models.CharField(max_length=32, blank=True, null=True)
    estado = models.CharField(max_length=32, blank=True, null=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL,
                                related_name='endereco_cliente', blank=True, null=True)

    def __str__(self):
        return f"Cliente: {self.cliente} - {self.nome_endereco} - {self.cep} - {self.cidade} - {self.estado}"


class Cor(models.Model):
    nome = models.CharField(max_length=150, blank=True, null=True)
    codigo = models.CharField(max_length=150, blank=True, null=True)

    def __str__(self):
        return str(self.nome)


class Estoque(models.Model):
    produto = models.ForeignKey(
        Produto, on_delete=models.SET_NULL, blank=True, null=True)
    cor = models.ForeignKey(Cor, on_delete=models.SET_NULL, blank=True,
                            null=True)  # (amarelo, azul, preto)
    # (P, M, G)
    tamanho = models.CharField(max_length=5, blank=True, null=True)
    estoque_disponivel = models.IntegerField(blank=True, null=True, default=0)

    def __str__(self):
        return f'{self.produto.nome} - Cor: {self.cor.nome} - Tamanho: {self.tamanho} - Disponivel: {self.estoque_disponivel}'


class Pedido(models.Model):
    cliente = models.ForeignKey(
        Cliente, on_delete=models.SET_NULL, blank=True, null=True)
    codigo_transacao = models.CharField(max_length=150, blank=True, null=True)
    finalizado = models.BooleanField(default=False)
    endereco = models.ForeignKey(
        Endereco, on_delete=models.SET_NULL, blank=True, null=True)
    data_finalizacao = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Cliente: {self.cliente} - Nº Pedido: {self.id} - Finalizado: {self.finalizado}"

    @property
    def quantidade_itens(self):
        itens_carrinho = Carrinho.objects.filter(pedido__id=self.id)
        qtd_itens = sum([item.quantidade for item in itens_carrinho])
        return qtd_itens

    @property
    def total(self):
        itens_carrinho = Carrinho.objects.filter(pedido__id=self.id)

        total_carrinho = sum(
            [item.subtotal for item in itens_carrinho])
        return total_carrinho

    @property
    def itens(self):
        itens_pedido = Carrinho.objects.filter(pedido__id=self.id)

        return itens_pedido


class Carrinho(models.Model):
    item_estoque = models.ForeignKey(
        Estoque, on_delete=models.SET_NULL, related_name="item_produto", blank=True, null=True)
    quantidade = models.IntegerField(blank=True, null=True, default=0)
    pedido = models.ForeignKey(
        Pedido, on_delete=models.CASCADE, related_name="itens_do_pedido", blank=True, null=True)

    def __str__(self):
        if self.pedido:
            pedido_id = str(self.pedido.id)
        else:
            pedido_id = "None"

        return f"Nº Pedido: {pedido_id} -  Cliente: {self.pedido.cliente} - Produto: {self.item_estoque.produto.nome} - Cor: {self.item_estoque.cor} - Tamanho: {self.item_estoque.tamanho}"

    @property
    def subtotal(self):
        return self.quantidade * float(self.item_estoque.produto.preco)

    @property
    def total_carrinho(self):
        total = [float(valor.tot) for valor in self.subtotal]
        return total


class Pagamento(models.Model):
    id_pagamento = models.CharField(max_length=400, blank=True, null=True)
    aprovado = models.BooleanField(default=False)
    pedido = models.ForeignKey(
        Pedido, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return f"{self.id_pagamento}"


class Banner(models.Model):
    imagem = models.ImageField(blank=True, null=True)
    ativo = models.BooleanField(default=False)
    link_destino = models.CharField(max_length=400, null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.link_destino} - Ativo: {self.ativo}"

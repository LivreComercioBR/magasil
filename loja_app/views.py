from django.shortcuts import redirect, render
from django.contrib import auth
from django.contrib import messages
from django.contrib.messages import constants
from django.contrib.auth.decorators import login_required
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from loja_app.models import User
from .utils import password_is_valid
from store.models import Cliente, Pedido


def cadastro(request):
    if request.user.is_authenticated:
        return redirect("logar")
    if request.method == "POST":
        dados = request.POST.dict()
        username = dados.get("email")
        nome = dados.get("nome")
        email = dados.get("email")
        password = dados.get("password")
        confirmar_senha = dados.get("confirmar_senha")

        if "username" in dados and "nome" in dados and "email" in dados and "password" in dados and "confirmar_senha" in dados:
            if len(username.strip()) == 0 or len(email.strip()) == 0 or len(password.strip()) == 0:
                messages.add_message(request, constants.ERROR,
                                     "Preencha todos os dados corretamente!")
                return redirect("cadastro")
        try:
            validate_email(email)
        except ValidationError:
            messages.add_message(
                request, constants. ERROR, "Hum, parece que o seu email não possui um formato válido de email!")
            return redirect("cadastro")

        checar_senha = password_is_valid(request,
                                         password=password, confirm_password=confirmar_senha)
        usuario = auth.authenticate(username=username, password=password)
        if usuario:
            messages.add_message(
                request, constants.ERROR, "Já existe um usuário com este nome e email no sistema")
            return redirect("cadastro")

        if checar_senha:
            usuario, criado = User.objects.get_or_create(
                username=username, nome=nome, email=email, password=password)
        if not criado:
            messages.add_message(
                request, constants.ERROR, "Ops, já existe um usuário com este email ou username no sistema!")
            return redirect("cadastro")
        else:
            usuario.set_password(password)
            usuario.save()

            # Não posso criar um usuário sem um cliente associado a ele
            if request.COOKIES.get("id_sessao"):
                id_sessao = request.COOKIES.get("id_sessao")
                clientes = Cliente.objects.filter(id_sessao=id_sessao)
                if len(clientes) > 0:
                    cliente, criado = Cliente.objects.get_or_create(
                        email=email,
                        nome=nome,
                    )
            else:
                cliente, criado = Cliente.objects.get_or_create(
                    email=email)
            cliente.usuario = usuario
            cliente.email = email
            cliente.nome = nome
            cliente.save()
        auth.authenticate(username=username, password=password)

        auth.login(request, usuario)
        return redirect("produtos")

    return render(request, 'cadastro.html')


def logar(request):
    if request.user.is_authenticated:
        return redirect("produtos")
    if request.method == "POST":
        dados = request.POST.dict()
        if "email" in dados and "password" in dados:
            username = dados.get("email")
            password = dados.get("password")
            # vou autenticar o usuário e redirecioná-lo
            usuario = auth.authenticate(username=username, password=password)
            if usuario:
                auth.login(request, usuario)
                return redirect("produtos")
            else:
                messages.add_message(
                    request, constants.ERROR, "Usuário ou senha inválidos!")
                return redirect("logar")
        else:
            messages.add_message(request, constants.ERROR,
                                 "Preencha os dados corretamente")
            return redirect("logar")

    else:
        return render(request, 'logar.html')


@login_required
def sair(request):
    auth.logout(request)
    return redirect("logar")


@login_required
def minha_conta(request):
    if not request.user.is_authenticated:
        messages.add_message(request, constants.WARNING,
                             "Faça login para acessar a sua conta")
        return redirect("produtos")
    cliente = request.user.cliente
    if request.method == "POST":
        dados = request.POST.dict()
        nome = dados.get("nome")
        sobrenome = dados.get("lastname")
        email = dados.get("email")
        cpf = dados.get("cpf")
        telefone = dados.get("phone")

        if nome in dados:
            if nome != cliente.nome:
                cliente.nome = nome
            else:
                pass
        if "lastname" in dados:
            cliente.sobrenome = sobrenome
        else:
            pass

        if "email" in dados:
            if email != cliente.email:
                clientes = Cliente.objects.filter(email=email)
                usuarios = User.objects.filter(email=email)
                if len(clientes) > 0 or len(usuarios) > 0:
                    messages.add_message(
                        request, constants.ERROR, "Já existe um usuário com este email no sistema")
                    return redirect("minha_conta")
                else:
                    if "email" in dados:
                        cliente.email = email
                        cliente.usuario.email = email
                    else:
                        pass
        if "cpf" in dados:
            cliente.cpf = cpf
        else:
            pass

        if "phone" in dados:
            cliente.telefone = telefone
        else:
            pass

        cliente.save()
        request.user.save()
        messages.add_message(request, constants.SUCCESS,
                             "Dados alterados com sucesso!")
        return redirect("minha_conta")

    return render(request, 'minha_conta.html')
# TODO corrigir para o usuário e o cliente terem o mesmo email


@login_required
def meus_pedidos(request):
    if not request.user.is_authenticated:
        messages.add_message(request, constants.WARNING,
                             "Faça login para acessar os seus pedidos")
        return redirect("produtos")
    pedidos = Pedido.objects.filter(
        finalizado=True, cliente_id=request.user.cliente).order_by("-data_finalizacao")

    if pedidos:
        for pedido in pedidos:
            produtos = pedido.itens
            print(produtos)
    else:
        produtos = None
        messages.add_message(request, constants.WARNING,
                             "Você não possui nenhum pedido")

    context = {"pedidos": pedidos, "produtos": produtos}
    return render(request, 'meus_pedidos.html', context)


@login_required
def alterar_senha(request):
    usuario = request.user.email
    if request.method == "POST":
        dados = request.POST.dict()

        senha_atual = dados.get("senha_atual")
        new_passord = dados.get("new_password")
        confirmar_password = dados.get("confirmar_password")

        usuario = auth.authenticate(
            request, username=usuario, password=senha_atual)
        if usuario:
            usuario.set_password(new_passord)
            usuario.save()
            messages.add_message(request, constants.SUCCESS,
                                 "Senha alterada com sucesso!")
            return redirect("logar")
        else:
            messages.add_message(
                request, constants.ERROR, "Sua senha não confere! Se não se lembrar tente com a opção esqueci minha senha na área de login")
            return redirect("alterar_senha")

    return render(request, 'alterar_senha.html')


def politica_privacidade(request):
    return render(request, 'politica_privacidade.html')


def termos_de_uso(request):
    return render(request, 'termos_de_uso.html')


def quem_somos(request):
    return render(request, 'quem_somos.html')

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.messages import constants
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib import auth
from django.contrib.auth.decorators import user_passes_test
from rolepermissions.roles import assign_role
from rolepermissions.checkers import has_permission

def cadastro(request):
    if request.method == 'GET':
        return render(request, 'cadastro.html')
    elif request.method == 'POST':
        username = request.POST.get('username')
        senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirmar_senha')

        if not senha == confirmar_senha:
            messages.add_message(request, constants.ERROR, 'Senha e confirmar senha devem ser iguais.')
            return redirect('/usuarios/cadastro/')
        
        if len(senha) < 6:
            messages.add_message(request, constants.ERROR, 'A senha deve ter 6 ou mais caracteres.')
            return redirect('/usuarios/cadastro/')

        users = User.objects.filter(username=username)
        if users.exists():
            messages.add_message(request, constants.ERROR, 'Já existe um usuário com esse username.')
            return redirect('/usuarios/cadastro/')

        user = User.objects.create_user(
            username=username,
            password=senha
        )

        return redirect('/usuarios/login')

def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    elif request.method == 'POST':
        username = request.POST.get('username')
        senha = request.POST.get('senha')

        user = authenticate(request, username=username, password=senha)

        if user:
            auth.login(request, user)
            return redirect('treinar_ia')
        
        messages.add_message(request, constants.ERROR, 'Username ou senha inválidos.')
        return redirect('login')

@user_passes_test(lambda u: u.is_superuser)
def permissoes(request):
    """
    Permite ao superusuário gerenciar as permissões dos outros usuários.
    Somente superusuários podem acessar esta view.
    """
    if request.method == 'GET':
        users = User.objects.filter(is_superuser=False)
        return render(request, 'permissoes.html', {'users': users})
    
    elif request.method == 'POST':
        user_id = request.POST.get('user_id')
        papel = request.POST.get('papel')
        
        user = User.objects.get(id=user_id)
        
        # Atribui o papel selecionado ao usuário
        if papel == 'gerente':
            assign_role(user, 'gerente')
        
        messages.add_message(request, constants.SUCCESS, 'Permissão atribuída com sucesso')
        return redirect('permissoes')

@user_passes_test(lambda u: u.is_superuser)
def tornar_gerente(request, id):
    """
    Atribui o papel de gerente para um usuário específico.
    Somente superusuários podem executar esta função.
    
    Args:
        request: Objeto de requisição HTTP
        id: ID do usuário que será promovido a gerente
    """
    user = User.objects.get(id=id)
    assign_role(user, 'gerente')
    messages.add_message(request, constants.SUCCESS, 'Usuário promovido a gerente com sucesso!')
    return redirect('permissoes')
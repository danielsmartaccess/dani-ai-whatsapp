from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Perfil(models.Model):
    """
    Modelo para armazenar informações adicionais do usuário.
    
    Campos:
    - usuario: Relacionamento um para um com o modelo User do Django
    - cargo: Cargo do usuário na empresa
    - departamento: Departamento ao qual o usuário pertence
    """
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    cargo = models.CharField(max_length=100)
    departamento = models.CharField(max_length=100)
    
    def __str__(self):
        return self.usuario.username

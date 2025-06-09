"""
Aplicativo para integração com WhatsApp através da Evolution API.
Este aplicativo substitui o antigo app corrompido com bytes nulos.
"""

from django.apps import AppConfig


class OraculoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'oraculo'
    
    def ready(self):
        """
        Método executado quando o aplicativo é inicializado.
        Importa os signals para que sejam registrados.
        """
        import oraculo.signals

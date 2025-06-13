from django.contrib import admin
from .models import Treinamentos, WhatsAppConfig, DataTreinamento, Pergunta

@admin.register(Treinamentos)
class TreinamentosAdmin(admin.ModelAdmin):
    list_display = ('site',)
    search_fields = ('site',)

@admin.register(WhatsAppConfig)
class WhatsAppConfigAdmin(admin.ModelAdmin):
    list_display = ('instance_name', 'api_url', 'is_active')
    search_fields = ('instance_name', 'api_url')
    list_filter = ('is_active',)
    
    def has_delete_permission(self, request, obj=None):
        # Previne a exclusão da configuração principal
        if obj and obj.pk == 1:
            return False
        return super().has_delete_permission(request, obj)

@admin.register(DataTreinamento)
class DataTreinamentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'texto')
    search_fields = ('texto',)

@admin.register(Pergunta)
class PerguntaAdmin(admin.ModelAdmin):
    list_display = ('id', 'pergunta')
    search_fields = ('pergunta',)
    filter_horizontal = ('data_treinamento',)

from django import forms
from django.core.exceptions import ValidationError
from .models import SequenciaMensagem
from datetime import timedelta

class SequenciaMensagemForm(forms.ModelForm):
    # Campo para exibição mais amigável do atraso em horas e minutos
    atraso_horas = forms.IntegerField(min_value=0, required=False, label="Atraso (horas)")
    atraso_minutos = forms.IntegerField(min_value=0, max_value=59, required=False, label="Atraso (minutos)")
    
    class Meta:
        model = SequenciaMensagem
        fields = ['ordem', 'conteudo', 'atraso_horas', 'atraso_minutos', 'condicao_envio']
        labels = {
            'ordem': 'Ordem',
            'conteudo': 'Mensagem (Template)',
            'condicao_envio': 'Condições de Envio (opcional)',
        }
        widgets = {
            'conteudo': forms.Textarea(attrs={'rows': 5}),
        }
    
    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        initial = kwargs.get('initial', {})
        
        # Se estiver editando uma instância existente, preencher os campos de atraso
        if instance and instance.atraso:
            seconds = int(instance.atraso.total_seconds())
            initial['atraso_horas'] = seconds // 3600
            initial['atraso_minutos'] = (seconds % 3600) // 60
            
        kwargs['initial'] = initial
        super().__init__(*args, **kwargs)
    
    def clean(self):
        cleaned_data = super().clean()
        horas = cleaned_data.get('atraso_horas', 0) or 0
        minutos = cleaned_data.get('atraso_minutos', 0) or 0
        
        if horas == 0 and minutos == 0:
            raise ValidationError("O atraso deve ser pelo menos 1 minuto.")
        
        # Converte horas e minutos em timedelta
        cleaned_data['atraso'] = timedelta(hours=horas, minutes=minutos)
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        horas = self.cleaned_data.get('atraso_horas', 0) or 0
        minutos = self.cleaned_data.get('atraso_minutos', 0) or 0
        instance.atraso = timedelta(hours=horas, minutes=minutos)
        
        if commit:
            instance.save()
        return instance

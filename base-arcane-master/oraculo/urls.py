from django.urls import path
from . import views

urlpatterns = [
    path('treinar_ia', views.treinar_ia, name="treinar_ia"),
    path('chat', views.chat, name="chat"),
    path('stream_response', views.stream_response, name="stream_response"),
    path('ver_fontes/<int:id>', views.ver_fontes, name='ver_fontes'),
    path('webhook_whatsapp', views.webhook_whatsapp, name='webhook_whatsapp'),
    path('whatsapp_config', views.whatsapp_config, name='whatsapp_config'),
    path('whatsapp_status', views.whatsapp_status, name='whatsapp_status'),
    path('whatsapp_qrcode', views.whatsapp_qrcode, name='whatsapp_qrcode'),
    path('whatsapp_disconnect', views.whatsapp_disconnect, name='whatsapp_disconnect'),
]
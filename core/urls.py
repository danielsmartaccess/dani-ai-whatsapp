from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

urlpatterns = [
    path('', lambda request: redirect('/oraculo/treinar_ia/'), name='home'),
    path('oraculo/', include('oraculo.urls'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from django.shortcuts import redirect

urlpatterns = [
    path('', lambda request: redirect('login') if not request.user.is_authenticated else redirect('oraculo/treinar_ia'), name='home'),
    path('admin/', admin.site.urls),
    path('usuarios/', include('usuarios.urls')),
    path('oraculo/', include('oraculo.urls'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

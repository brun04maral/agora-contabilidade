"""
URL configuration for Agora Contabilidade project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.views.static import serve
from core.views import export_fiscal_excel

urlpatterns = [
    path('', RedirectView.as_view(url='/admin/', permanent=False), name='index'),

    # Favicon redirect to ensure correct one is served
    path('favicon.ico', RedirectView.as_view(url='/media/logos/favicon.svg', permanent=True)),

    # Fiscal export (mantém rota para Excel export)
    path('fiscal/export/', export_fiscal_excel, name='export_fiscal_excel'),

    # Admin (inclui Documentação e Fiscal integrados)
    path('admin/', admin.site.urls),
]

# Serve media files (works with Gunicorn)
urlpatterns += [
    path('media/<path:path>', serve, {'document_root': settings.MEDIA_ROOT}),
]

# Also add static files in DEBUG mode
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

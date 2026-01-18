"""
URL configuration for Agora Contabilidade project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.views.static import serve
from core.views import changelog_view, export_fiscal_excel, fiscal_iva_view, fiscal_irs_view, fiscal_irc_view
from core.views_docs import docs_index, docs_view

urlpatterns = [
    path('', RedirectView.as_view(url='/admin/', permanent=False), name='index'),

    # Favicon redirect to ensure correct one is served
    path('favicon.ico', RedirectView.as_view(url='/media/logos/favicon.svg', permanent=True)),

    # Documentation
    path('docs/', docs_index, name='docs_index'),
    path('docs/<str:doc_key>/', docs_view, name='docs_view'),
    path('changelog/', changelog_view, name='changelog'),  # Mantém compatibilidade

    # Fiscal Pages
    path('fiscal/iva/', fiscal_iva_view, name='fiscal_iva'),
    path('fiscal/irs/', fiscal_irs_view, name='fiscal_irs'),
    path('fiscal/irc/', fiscal_irc_view, name='fiscal_irc'),
    path('fiscal/export/', export_fiscal_excel, name='export_fiscal_excel'),

    # Admin
    path('admin/', admin.site.urls),
]

# Serve media files (works with Gunicorn)
urlpatterns += [
    path('media/<path:path>', serve, {'document_root': settings.MEDIA_ROOT}),
]

# Also add static files in DEBUG mode
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

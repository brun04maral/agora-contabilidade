"""
URL configuration for Agora Contabilidade project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from core.views import changelog_view
from core.views_docs import docs_index, docs_view

urlpatterns = [
    path('', RedirectView.as_view(url='/admin/', permanent=False), name='index'),

    # Documentation
    path('docs/', docs_index, name='docs_index'),
    path('docs/<str:doc_key>/', docs_view, name='docs_view'),
    path('changelog/', changelog_view, name='changelog'),  # Mantém compatibilidade

    # Admin
    path('admin/', admin.site.urls),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # In production, serve media via Django as well (simpler than Traefik config)
    from django.views.static import serve
    urlpatterns += [
        path('media/<path:path>', serve, {'document_root': settings.MEDIA_ROOT}),
    ]

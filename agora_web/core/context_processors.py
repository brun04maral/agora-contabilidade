"""
Context processors for Agora Contabilidade
Add global variables to all templates
"""
from config.settings import get_current_version, get_version_date


def version_info(request):
    """Add version and date to template context"""
    return {
        'version': get_current_version(),
        'version_date': get_version_date(),
    }

"""
Documentation views for Agora Contabilidade.
Provides a browsable documentation center for all project documentation.
"""
from pathlib import Path
from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from django.http import Http404
import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.toc import TocExtension
import re


# Documentation structure
DOCS_STRUCTURE = {
    'overview': {
        'title': 'Visão Geral',
        'icon': 'info',
        'file': 'README.md',
        'description': 'Visão geral do projeto Agora Contabilidade'
    },
    'changelog': {
        'title': 'Changelog',
        'icon': 'history',
        'file': 'CHANGELOG.md',
        'description': 'Histórico completo de versões e alterações'
    },
    'database-manual': {
        'title': 'Alterações Manuais BD',
        'icon': 'build',
        'file': 'docs/DATABASE_MANUAL_CHANGES.md',
        'description': 'Histórico de alterações manuais na base de dados'
    },
    'docs-index': {
        'title': 'Índice da Documentação',
        'icon': 'list',
        'file': 'docs/README.md',
        'description': 'Índice completo da documentação do projeto'
    },
    'excel-import': {
        'title': 'Importação Excel',
        'icon': 'upload_file',
        'file': 'docs/EXCEL_IMPORT_ANALYSIS.md',
        'description': 'Análise do sistema de importação de dados via Excel'
    },
    'import-system': {
        'title': 'Sistema de Importação',
        'icon': 'cloud_upload',
        'file': 'docs/IMPORT_SYSTEM.md',
        'description': 'Documentação do sistema de importação'
    },
    'pwa': {
        'title': 'PWA & Branding',
        'icon': 'install_mobile',
        'file': 'docs/PWA_BRANDING.md',
        'description': 'Progressive Web App e configuração de branding'
    },
    'saldos-dashboard': {
        'title': 'Dashboard de Saldos',
        'icon': 'dashboard',
        'file': 'docs/SALDOS_DASHBOARD.md',
        'description': 'Documentação do dashboard de saldos pessoais'
    },
    'saldos-revision': {
        'title': 'Revisão de Saldos',
        'icon': 'fact_check',
        'file': 'docs/SALDOS_REVISION_SPEC.md',
        'description': 'Especificação para revisão da lógica de saldos'
    },
    'socios': {
        'title': 'Migração de Sócios',
        'icon': 'people',
        'file': 'docs/SOCIOS_MIGRATION.md',
        'description': 'Documentação da migração do modelo Socio'
    },
    'audit-trail': {
        'title': 'Audit Trail',
        'icon': 'history_edu',
        'file': 'docs/audit-trail-implementation.md',
        'description': 'Implementação do sistema de auditoria'
    },
    'claude': {
        'title': 'Contexto IA (Claude)',
        'icon': 'smart_toy',
        'file': '.claude/claude.md',
        'description': 'Contexto e instruções para assistente IA'
    },
}


def get_doc_path(doc_key):
    """Get absolute path for a documentation file."""
    if doc_key not in DOCS_STRUCTURE:
        return None

    file_path = DOCS_STRUCTURE[doc_key]['file']

    # Build absolute path based on file location
    if file_path == 'README.md':
        return settings.DOCS_CONFIG['MAIN_README']
    elif file_path == 'CHANGELOG.md':
        return settings.DOCS_CONFIG['CHANGELOG']
    elif file_path == '.claude/claude.md':
        return settings.DOCS_CONFIG['CLAUDE_MD']
    else:
        # docs/ folder
        return settings.DOCS_CONFIG['ROOT_PATH'] / file_path.replace('docs/', '')


def render_markdown(content):
    """Render markdown to HTML with syntax highlighting and TOC."""
    md = markdown.Markdown(extensions=[
        'fenced_code',
        'tables',
        'nl2br',
        CodeHiliteExtension(
            linenums=False,
            guess_lang=True,
            css_class='highlight'
        ),
        TocExtension(
            title='Índice',
            toc_depth='2-4'
        ),
    ])

    html = md.convert(content)
    toc = md.toc if hasattr(md, 'toc') else ''

    return html, toc


def extract_title(content):
    """Extract first H1 from markdown content."""
    match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    return match.group(1) if match else 'Documentação'


@staff_member_required
def docs_index(request):
    """Documentation center index page."""
    # Group docs by category
    categories = {
        'Geral': ['overview', 'changelog', 'docs-index'],
        'Técnico': ['database-manual', 'saldos-dashboard', 'saldos-revision', 'socios', 'audit-trail'],
        'Features': ['excel-import', 'import-system', 'pwa'],
        'Suporte': ['claude'],
    }

    docs_by_category = {}
    for category, doc_keys in categories.items():
        docs_by_category[category] = [
            {**DOCS_STRUCTURE[key], 'key': key}
            for key in doc_keys
            if key in DOCS_STRUCTURE
        ]

    context = {
        'title': 'Centro de Documentação',
        'docs_by_category': docs_by_category,
        'github_repo': settings.DOCS_CONFIG['GITHUB_REPO'],
    }

    return render(request, 'docs/index.html', context)


@staff_member_required
def docs_view(request, doc_key):
    """View a specific documentation page."""
    if doc_key not in DOCS_STRUCTURE:
        raise Http404("Documentação não encontrada")

    doc_info = DOCS_STRUCTURE[doc_key]
    doc_path = get_doc_path(doc_key)

    if not doc_path or not doc_path.exists():
        context = {
            'title': doc_info['title'],
            'doc_key': doc_key,
            'error': f"Ficheiro não encontrado: {doc_path}",
        }
        return render(request, 'docs/document.html', context)

    try:
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read()

        html, toc = render_markdown(content)
        title = extract_title(content) or doc_info['title']

        # Generate GitHub edit URL
        github_edit_url = (
            f"https://github.com/{settings.DOCS_CONFIG['GITHUB_REPO']}/edit/"
            f"{settings.DOCS_CONFIG['GITHUB_BRANCH']}/{doc_info['file']}"
        )

        context = {
            'title': title,
            'doc_key': doc_key,
            'doc_info': doc_info,
            'content_html': html,
            'toc_html': toc,
            'github_edit_url': github_edit_url,
            'all_docs': DOCS_STRUCTURE,
        }

        return render(request, 'docs/document.html', context)

    except Exception as e:
        context = {
            'title': doc_info['title'],
            'doc_key': doc_key,
            'error': f"Erro ao ler ficheiro: {str(e)}",
        }
        return render(request, 'docs/document.html', context)

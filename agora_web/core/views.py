"""
Views for Agora Contabilidade core app.
"""
from pathlib import Path
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
import markdown


@staff_member_required
def changelog_view(request):
    """
    Display the CHANGELOG.md file with version history.
    Only accessible to staff members.
    """
    # Read CHANGELOG.md from project root
    changelog_path = Path(__file__).resolve().parent.parent.parent / 'CHANGELOG.md'

    try:
        with open(changelog_path, 'r', encoding='utf-8') as f:
            changelog_content = f.read()

        # Convert Markdown to HTML
        changelog_html = markdown.markdown(
            changelog_content,
            extensions=['fenced_code', 'tables', 'nl2br']
        )
    except FileNotFoundError:
        changelog_html = "<p>CHANGELOG.md not found.</p>"

    context = {
        'changelog_html': changelog_html,
        'title': 'Changelog - Agora Contabilidade',
    }

    return render(request, 'admin/changelog.html', context)

# Agora Contabilidade - Documentation

**Project:** Sistema de Contabilidade Django para Agora Media Production
**Last Updated:** 2026-01-03

---

## 📚 Documentation Index

### 🚀 Getting Started
- [Main README](../README.md) - Project overview and quick start
- [Developer Guide](../README-DEV.md) - Development workflow with VS Code Extension
- [Django App README](../agora_web/README.md) - Django-specific setup

### 🏗️ Implementation Guides

| Document | Description | Status |
|----------|-------------|--------|
| [**SOCIOS_MIGRATION.md**](./SOCIOS_MIGRATION.md) | Complete guide to Socio model implementation | ✅ Complete |
| [**SALDOS_DASHBOARD.md**](./SALDOS_DASHBOARD.md) | Saldos Pessoais dashboard implementation | ✅ Complete |
| [**IMPORT_SYSTEM.md**](./IMPORT_SYSTEM.md) | Web-based Excel import system | ✅ Complete |
| [**DATABASE_MANUAL_CHANGES.md**](./DATABASE_MANUAL_CHANGES.md) | Manual SQL changes history | ✅ Complete |

### 🤖 For AI Assistants
- [`.claude/claude.md`](../.claude/claude.md) - Complete project context for Claude Code and other AI tools

---

## 📖 Quick Links by Topic

### Database & Migrations
- **Manual SQL changes:** [DATABASE_MANUAL_CHANGES.md](./DATABASE_MANUAL_CHANGES.md)
- **Socio model migration:** [SOCIOS_MIGRATION.md](./SOCIOS_MIGRATION.md#migration-issues--solutions)
- **PostgreSQL vs Django:** [DATABASE_MANUAL_CHANGES.md](./DATABASE_MANUAL_CHANGES.md#postgresql-vs-django-on-delete)

### Features
- **Saldos calculation logic:** [SALDOS_DASHBOARD.md](./SALDOS_DASHBOARD.md#calculator-logic)
- **Dashboard template:** [SALDOS_DASHBOARD.md](./SALDOS_DASHBOARD.md#template)
- **Socio admin customization:** [SOCIOS_MIGRATION.md](./SOCIOS_MIGRATION.md#admin-customizations)
- **Excel import system:** [IMPORT_SYSTEM.md](./IMPORT_SYSTEM.md)

### Troubleshooting
- **500 errors on Saldos page:** [SALDOS_DASHBOARD.md](./SALDOS_DASHBOARD.md#error-history--solutions)
- **Migration issues:** [DATABASE_MANUAL_CHANGES.md](./DATABASE_MANUAL_CHANGES.md#context-why-manual-changes-were-needed)
- **Docker code not updating:** [.claude/claude.md](../.claude/claude.md#-known-issues--solutions)

---

## 🎯 Common Tasks

### For Developers

**Understanding the codebase:**
1. Start with [.claude/claude.md](../.claude/claude.md) for architecture overview
2. Read [SOCIOS_MIGRATION.md](./SOCIOS_MIGRATION.md) to understand data model
3. Read [SALDOS_DASHBOARD.md](./SALDOS_DASHBOARD.md) for main feature

**Making changes:**
1. Check [.claude/claude.md](../.claude/claude.md#-common-tasks) for commands
2. Test in Django shell first
3. Remember to rebuild Docker after code changes

**Debugging:**
1. Check error history in relevant doc
2. Use Django shell to test calculations
3. Check logs: `docker compose logs -f web`

### For AI Assistants (Claude Code, etc.)

**Starting a new session:**
1. Read [.claude/claude.md](../.claude/claude.md) first for full context
2. Check git status and current branch
3. Review recent commits for latest changes

**Implementing features:**
1. Check if similar feature exists in docs
2. Follow existing patterns (see SOCIOS or SALDOS docs)
3. Document your changes in appropriate doc file

**Fixing bugs:**
1. Check "Error History" sections in relevant docs
2. Look for similar issues in [Known Issues](../.claude/claude.md#-known-issues--solutions)
3. Document the fix for future reference

---

## 📝 Documentation Standards

### When to Create New Documentation

Create new doc file when:
- ✅ Implementing a major new feature (like Socios or Saldos)
- ✅ Making significant architectural changes
- ✅ Encountering complex issues that required non-standard solutions
- ✅ Adding manual database changes

Update existing doc when:
- ✅ Fixing bugs in documented features
- ✅ Adding minor enhancements
- ✅ Discovering new edge cases or gotchas

### Documentation Template

```markdown
# [Feature Name] - Implementation Guide

**Date:** December 2025
**Status:** ✅ Complete / 🚧 In Progress / ❌ Deprecated
**Branch:** `branch-name`

---

## Overview
[Brief description of feature and goals]

## Implementation
[Technical details, code snippets, file paths]

## Testing
[How to test and verify]

## Error History & Solutions
[Common issues and fixes]

## Lessons Learned
[Key takeaways for future reference]

---

**Documentation by:** [Your name/tool]
**Last Updated:** YYYY-MM-DD
```

---

## 🔄 Keeping Documentation Updated

**Important:** Documentation should be updated when:
1. Feature implementation changes significantly
2. New errors/solutions are discovered
3. Architecture decisions change
4. New manual database changes are made

**Who updates?**
- Developers: Update after major changes
- AI Assistants: Update during implementation sessions
- DevOps: Update deployment/infrastructure docs

---

## 📞 Getting Help

1. **Check docs first** - Most questions answered here
2. **Search git history** - `git log --grep="keyword"`
3. **Django shell** - Test assumptions before asking
4. **Ask in context** - Reference relevant doc sections

---

**© 2025 Agora Media Production**

# feat: Add dark mode support and compact layout to Fiscal and Saldos dashboards

## 🎨 Resumo

Implementação de dark mode e layout compacto para os dashboards de Fiscal e Saldos Pessoais, melhorando a usabilidade e aproveitamento do espaço horizontal.

## 📋 Mudanças Principais

### Dark Mode Support
- ✅ Implementado suporte completo a dark mode usando seletor `.dark`
- ✅ Compatível com o sistema de theme switching do Django Unfold
- ✅ Cores adaptadas para boa legibilidade em ambos os modos
- ✅ Backgrounds, textos e bordas respondem automaticamente ao tema

### Layout Compacto
- ✅ Redução de padding de `1.5rem` para `1rem` nos cards
- ✅ Otimização de tamanhos de fonte para melhor densidade de informação
- ✅ CSS Grid nativo para layout responsivo (3 colunas → 2 colunas → 1 coluna)
- ✅ Melhor aproveitamento do espaço horizontal da tela

### Templates Atualizados
- **Fiscal Dashboard** (`core/templates/admin/core/fiscal/changelist.html`)
  - Cards de resumo IVA, IRS e IRC
  - Detalhes trimestrais de IVA
  - Tabela de retenções IRS mensais
  - Estimativa anual de IRC

- **Saldos Pessoais** (`core/templates/admin/core/saldo/changelist.html`)
  - Cards de saldo por sócio (BA, RR)
  - Breakdown detalhado de INs e OUTs
  - Sugestões de boletim

## 🎯 Abordagem Técnica

### Dark Mode Implementation
```css
/* Light mode (default) */
.fiscal-card { background-color: white; }

/* Dark mode (usando classe .dark do Unfold) */
.dark .fiscal-card { background-color: rgb(31, 41, 55); }
```

Esta abordagem usa o sistema nativo do Unfold que adiciona a classe `.dark` ao elemento `<html>` quando o dark mode está ativo.

### Layout Grid
```css
.fiscal-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

@media (max-width: 768px) {
  .fiscal-grid { grid-template-columns: 1fr; }
}
```

## 🧪 Testing

- ✅ Testado em light mode
- ✅ Testado em dark mode
- ✅ Testado responsividade (desktop, tablet, mobile)
- ✅ Verificado contraste de cores (WCAG AA)

## 📸 Screenshots

### Antes
- Layout espaçado verticalmente
- Sem suporte a dark mode
- Cards ocupando largura total

### Depois
- Layout compacto com 3 colunas
- Dark mode funcional
- Melhor aproveitamento do espaço

## 🔍 Commits Relacionados

- `90b9bf9` - refactor: compact layout for Fiscal and Saldos templates
- `b83db49` - fix: use .dark class selector for dark mode instead of media queries
- `5c23139` - fix: implement dark mode with CSS media queries instead of Tailwind classes
- `5b56c8e` - feat: add dark mode support to Fiscal and Saldos templates

## ✅ Checklist

- [x] Dark mode implementado e testado
- [x] Layout compacto implementado
- [x] Responsividade verificada
- [x] Templates limpos sem emojis
- [x] Código alinhado com design do Unfold
- [x] Sem quebras de funcionalidade existente

## 📝 Notas

- Abordagem final usa `.dark` class em vez de media queries por compatibilidade com Unfold
- Layout usa CSS Grid nativo em vez de classes Tailwind para maior controle
- Todos os estilos customizados estão inline no `<style>` block para facilitar manutenção
- **IMPORTANTE**: Sempre considerar dark mode em futuros desenvolvimentos de templates

## 🚀 Como Testar

1. Fazer pull do branch `claude/fix-improve-existing-K96rm`
2. Rebuild do container: `docker compose -f docker-compose.cloudflare.yml up -d --build web`
3. Aceder aos dashboards:
   - Saldos Pessoais: `/admin/core/saldo/`
   - Fiscal: `/admin/core/fiscal/`
4. Alternar entre light/dark mode usando o toggle do Unfold
5. Verificar responsividade redimensionando a janela

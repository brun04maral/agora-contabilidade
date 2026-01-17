/* Agora Contabilidade - Custom Admin JavaScript */

(function() {
    'use strict';

    function parseMoneyValue(text) {
        if (!text) return 0;
        const cleanText = text.replace(/[€\s]/g, '').replace(/\./g, '').replace(',', '.');
        const value = parseFloat(cleanText);
        return isNaN(value) ? 0 : value;
    }

    function updateSelectionTotal() {
        const selectedCheckboxes = document.querySelectorAll('input[name="_selected_action"]:checked');
        let totalContainer = document.querySelector('.selection-total-footer');

        if (selectedCheckboxes.length === 0) {
            if (totalContainer) totalContainer.remove();
            return;
        }

        // Descobrir o tipo de entidade (Projetos, Despesas, Boletins)
        let entityType = 'registos';
        const heading = document.querySelector('h1, .font-semibold');
        if (heading) {
            const headingText = heading.textContent;
            if (headingText.includes('Projeto')) entityType = 'Projetos';
            else if (headingText.includes('Despesa')) entityType = 'Despesas';
            else if (headingText.includes('Boletim')) entityType = 'Boletins';
        }

        let total = 0;
        let hasValues = false;

        selectedCheckboxes.forEach(function(checkbox) {
            const row = checkbox.closest('tr');
            if (!row) return;

            const valorCell = row.querySelector('.field-valor_sem_iva') ||
                            row.querySelector('.field-valor') ||
                            row.querySelector('td[class*="valor"]');

            if (valorCell) {
                const value = parseMoneyValue(valorCell.textContent);
                if (value > 0) {
                    total += value;
                    hasValues = true;
                }
            }
        });

        if (!hasValues) {
            if (totalContainer) totalContainer.remove();
            return;
        }

        const totalFormatted = new Intl.NumberFormat('pt-PT', {
            style: 'currency',
            currency: 'EUR'
        }).format(total);

        if (!totalContainer) {
            totalContainer = document.createElement('div');
            totalContainer.className = 'selection-total-footer';
            // Estilo integrado com Unfold theme (similar à barra de ações)
            totalContainer.style.cssText = 'position: fixed; bottom: 20px; right: 20px; z-index: 9999; padding: 12px 20px; background: rgb(255, 255, 255); border: 1px solid rgb(229, 231, 235); border-radius: 6px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06); font-size: 13px; font-family: system-ui, -apple-system, sans-serif;';
            document.body.appendChild(totalContainer);
        }

        // Formato: "X Projetos selecionados | TOTAL sem IVA: €XXX,XX"
        totalContainer.innerHTML = '<span style="color: rgb(107, 114, 128); font-weight: 500;">' + selectedCheckboxes.length + ' ' + entityType + ' selecionados</span> <span style="color: rgb(209, 213, 219); margin: 0 8px;">|</span> <span style="color: rgb(17, 24, 39); font-weight: 600;">TOTAL sem IVA: <span style="color: rgb(212, 175, 55);">' + totalFormatted + '</span></span>';
    }

    function makeRowsClickable() {
        const selectors = [
            '#result_list tbody tr',
            '.change-list table tbody tr',
            'table tbody tr',
        ];

        let tableRows = [];

        for (const selector of selectors) {
            tableRows = document.querySelectorAll(selector);
            if (tableRows.length > 0) break;
        }

        if (tableRows.length === 0) return;

        tableRows.forEach(function(row) {
            if (row.classList.contains('clickable-row')) return;

            row.addEventListener('click', function(event) {
                const target = event.target;
                const isInteractive = target.matches('input, select, button, a, label') ||
                                     target.closest('input, select, button, a, label');

                if (!isInteractive) {
                    const editLink = row.querySelector(
                        'a[href*="/change/"], th a, td:first-child a, td.field-__str__ a, th.field-__str__ a'
                    );

                    if (editLink && editLink.href) {
                        event.preventDefault();
                        if (event.ctrlKey || event.metaKey) {
                            window.open(editLink.href, '_blank');
                        } else {
                            window.location.href = editLink.href;
                        }
                    }
                }
            });

            row.classList.add('clickable-row');
        });
    }

    function initClickableRows() {
        makeRowsClickable();

        if (window.MutationObserver && document.body) {
            const observer = new MutationObserver(function(mutations) {
                let shouldRerun = false;
                mutations.forEach(function(mutation) {
                    if (mutation.addedNodes.length > 0) {
                        shouldRerun = true;
                    }
                });
                if (shouldRerun) {
                    setTimeout(makeRowsClickable, 100);
                }
            });

            observer.observe(document.body, {
                childList: true,
                subtree: true
            });
        }
    }

    function initSelectionTotalListeners() {
        document.addEventListener('change', function(event) {
            if (event.target.name === '_selected_action') {
                updateSelectionTotal();
            }
        });

        const selectAllCheckbox = document.querySelector('input[name="action-toggle"]');
        if (selectAllCheckbox) {
            selectAllCheckbox.addEventListener('change', function() {
                setTimeout(updateSelectionTotal, 50);
            });
        }

        setTimeout(updateSelectionTotal, 500);
    }

    function makeEnvironmentBadgeClickable() {
        // Tentar múltiplos seletores para o badge de environment
        const badgeSelectors = [
            '.badge',  // Unfold badge class
            '[class*="badge"]',  // Any class containing "badge"
            'span[class*="Development"]',
            'span[class*="Production"]',
            'div[class*="environment"]'
        ];

        let environmentBadge = null;

        for (const selector of badgeSelectors) {
            const elements = document.querySelectorAll(selector);
            for (const el of elements) {
                const text = el.textContent.trim();
                if (text === 'Development' || text === 'Production') {
                    environmentBadge = el;
                    break;
                }
            }
            if (environmentBadge) break;
        }

        if (environmentBadge && !environmentBadge.classList.contains('clickable-badge')) {
            environmentBadge.style.cursor = 'pointer';
            environmentBadge.title = 'Ver histórico de versões (CHANGELOG)';

            environmentBadge.addEventListener('click', function(e) {
                e.preventDefault();
                window.location.href = '/admin/changelog/';
            });

            environmentBadge.classList.add('clickable-badge');
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            initClickableRows();
            initSelectionTotalListeners();
            setTimeout(makeEnvironmentBadgeClickable, 1000);  // Delay for Unfold to load
        });
    } else {
        initClickableRows();
        initSelectionTotalListeners();
        setTimeout(makeEnvironmentBadgeClickable, 1000);  // Delay for Unfold to load
    }
})();

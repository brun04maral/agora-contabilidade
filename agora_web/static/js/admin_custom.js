/* Agora Contabilidade - Custom Admin JavaScript */

(function() {
    'use strict';

    function makeRowsClickable() {
        // Seletores para diferentes versões do Django Admin e Unfold
        const selectors = [
            '#result_list tbody tr',           // Django Admin padrão
            '.change-list table tbody tr',     // Unfold
            'table tbody tr',                  // Fallback genérico
        ];

        let tableRows = [];

        // Tentar encontrar as linhas com diferentes seletores
        for (const selector of selectors) {
            tableRows = document.querySelectorAll(selector);
            if (tableRows.length > 0) {
                console.log('Linhas encontradas com seletor:', selector);
                break;
            }
        }

        if (tableRows.length === 0) {
            console.log('Nenhuma linha de tabela encontrada');
            return;
        }

        console.log('Total de linhas encontradas:', tableRows.length);

        tableRows.forEach(function(row) {
            // Evitar processar a mesma linha duas vezes
            if (row.classList.contains('clickable-row')) {
                return;
            }

            // Adicionar handler de clique para toda a linha
            row.addEventListener('click', function(event) {
                // Verificar se o clique foi em um elemento interativo
                const target = event.target;
                const isInteractive = target.matches('input, select, button, a, label') ||
                                     target.closest('input, select, button, a, label');

                console.log('Clique detectado. Elemento:', target.tagName, 'Interativo:', isInteractive);

                // Se não foi em elemento interativo, navegar para o link da linha
                if (!isInteractive) {
                    // Procurar pelo link de edição em várias possibilidades
                    const editLink = row.querySelector(
                        'a[href*="/change/"], ' +      // Link de change
                        'th a, ' +                     // Link no th
                        'td:first-child a, ' +         // Primeiro td
                        'td.field-__str__ a, ' +       // Campo __str__
                        'th.field-__str__ a'           // Campo __str__ em th
                    );

                    console.log('Link de edição encontrado:', editLink);

                    if (editLink && editLink.href) {
                        event.preventDefault();

                        // Se Ctrl/Cmd está pressionado, abrir em nova aba
                        if (event.ctrlKey || event.metaKey) {
                            window.open(editLink.href, '_blank');
                        } else {
                            window.location.href = editLink.href;
                        }
                    }
                }
            });

            // Adicionar classe para indicar que a linha é clicável
            row.classList.add('clickable-row');
        });

        console.log('Linhas clicáveis configuradas:', tableRows.length);
    }

    // Executar quando DOM estiver pronto
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', makeRowsClickable);
    } else {
        makeRowsClickable();
    }

    // Para SPAs ou conteúdo carregado dinamicamente
    // Observar mudanças no DOM
    if (window.MutationObserver) {
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
})();

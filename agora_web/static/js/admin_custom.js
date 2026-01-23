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
        // Procurar por QUALQUER elemento que contenha o texto "Development" ou "Production"
        const allElements = document.querySelectorAll('*');
        let environmentBadge = null;

        for (const el of allElements) {
            // Verificar apenas elementos que tenham texto direto (não filhos)
            const directText = Array.from(el.childNodes)
                .filter(node => node.nodeType === Node.TEXT_NODE)
                .map(node => node.textContent.trim())
                .join('');

            const fullText = el.textContent.trim();

            if ((directText.includes('Development') || directText.includes('Production') ||
                 fullText.includes('Development') || fullText.includes('Production')) &&
                !el.classList.contains('clickable-badge')) {

                // Verificar se é um elemento pequeno (badge), não um container grande
                const rect = el.getBoundingClientRect();
                if (rect.width < 200 && rect.height < 100) {
                    environmentBadge = el;
                    console.log('Environment badge encontrado:', el, 'Texto:', fullText);
                    break;
                }
            }
        }

        if (environmentBadge && !environmentBadge.classList.contains('has-tooltip')) {
            // Usar versão e data das variáveis globais
            const version = window.AGORA_VERSION || '0.3.2';
            const versionDate = window.AGORA_VERSION_DATE || '2026-01-19';

            // Converter data de YYYY-MM-DD para DD/MM/YYYY
            const [year, month, day] = versionDate.split('-');
            const dateStr = `${day}/${month}/${year}`;

            // Definir tooltip com versão e data do CHANGELOG
            environmentBadge.title = `v${version} | Última atualização: ${dateStr}`;

            environmentBadge.classList.add('has-tooltip');
            console.log('Badge tooltip configurado:', environmentBadge.title);
        } else {
            console.log('Badge não encontrado. Tentando novamente em 2s...');
            setTimeout(makeEnvironmentBadgeClickable, 2000);
        }
    }

    // ========== AUTO-SUGESTÃO DE TAGS FISCAIS ==========

    function getSelectedOperationalTags(tagsField) {
        /**
         * Extrai códigos das tags operacionais selecionadas
         * Suporta ambos os lados do widget FilteredSelectMultiple (from/to)
         */
        if (!tagsField) return [];

        const selectedTags = [];

        // Tentar ambos os campos do FilteredSelectMultiple
        const fromField = document.querySelector('#id_tags_from');
        const toField = document.querySelector('#id_tags_to');

        // O campo "to" (direita) contém as tags selecionadas
        const activeField = toField || tagsField;

        if (activeField && activeField.options) {
            for (let option of activeField.options) {
                if (option.value) {
                    selectedTags.push(option.value);
                }
            }
        }

        return selectedTags;
    }

    // Mapeamento de Tags Operacionais → Tags Fiscais
    // Baseado nos códigos das TagDespesa
    const FISCAL_TAG_MAP = {
        // Equipamento e Serviços
        'EQUIPAMENTO': { irc: 'IRC_INVESTIMENTO', iva: 'IVA_DEDUTIVEL_100', irs: null, tsu: null },
        'SERVICO': { irc: 'IRC_DEDUTIVEL_100', iva: 'IVA_DEDUTIVEL_100', irs: null, tsu: null },
        'ADMINISTRATIVO': { irc: 'IRC_DEDUTIVEL_100', iva: 'IVA_DEDUTIVEL_100', irs: null, tsu: null },
        'PRODUCAO': { irc: 'IRC_DEDUTIVEL_100', iva: 'IVA_DEDUTIVEL_100', irs: null, tsu: null },

        // Pessoal
        'PESSOAL': { irc: 'IRC_DEDUTIVEL_100', iva: null, irs: 'IRS_RETENCAO_TRABALHO', tsu: 'TSU_TRABALHADOR' },
        'ORDENADO': { irc: 'IRC_DEDUTIVEL_100', iva: null, irs: 'IRS_RETENCAO_TRABALHO', tsu: 'TSU_TRABALHADOR' },
        'SUB_ALIMENTACAO': { irc: 'IRC_DEDUTIVEL_100', iva: null, irs: 'IRS_ISENTO', tsu: 'TSU_ISENTO' },
        'PESSOAL_BA': { irc: 'IRC_DEDUTIVEL_100', iva: null, irs: 'IRS_RETENCAO_TRABALHO', tsu: 'TSU_GERENTE' },
        'PESSOAL_RR': { irc: 'IRC_DEDUTIVEL_100', iva: null, irs: 'IRS_RETENCAO_TRABALHO', tsu: 'TSU_GERENTE' },

        // Comissões e Prémios
        'PREMIO': { irc: 'IRC_DEDUTIVEL_100', iva: null, irs: 'IRS_RETENCAO_TRABALHO', tsu: 'TSU_TRABALHADOR' },
        'COMISSAO_VENDA': { irc: 'IRC_DEDUTIVEL_100', iva: null, irs: 'IRS_RETENCAO_25', tsu: 'TSU_INDEPENDENTE' },

        // Alimentação e Deslocações
        'ALIMENTACAO': { irc: 'IRC_DEDUTIVEL_PARCIAL', iva: 'IVA_NAO_DEDUTIVEL', irs: null, tsu: null },
        'DESLOCACAO': { irc: 'IRC_DEDUTIVEL_PARCIAL', iva: 'IVA_MISTO', irs: null, tsu: null },
        'PER_DIEM_PT': { irc: 'IRC_DEDUTIVEL_100', iva: null, irs: 'IRS_ISENTO', tsu: null },
        'PER_DIEM_FORA': { irc: 'IRC_DEDUTIVEL_100', iva: null, irs: 'IRS_ISENTO', tsu: null },

        // IRS
        'IRS_RETENCAO': { irc: 'IRC_NAO_DEDUTIVEL', iva: null, irs: 'IRS_RETENCAO_TRABALHO', tsu: null },
    };

    function suggestFiscalTags() {
        // Detectar se estamos na página de edição de Despesa ou DespesaTemplate
        const isDespesaPage = window.location.pathname.includes('/despesa/') ||
                              window.location.pathname.includes('/despesatemplate/');

        if (!isDespesaPage) return;

        // Verificar se já foi inicializado (prevenir duplicação)
        if (document.querySelector('.fiscal-suggest-button')) return;

        // Encontrar campos de descrição e tags operacionais
        const descField = document.querySelector('#id_descricao, textarea[name="descricao"]');
        const tagsField = document.querySelector('#id_tags_from, #id_tags_to, select[name="tags"]');

        // Campos fiscais
        const ircField = document.querySelector('#id_tag_irc, select[name="tag_irc"]');
        const ivaField = document.querySelector('#id_tag_iva, select[name="tag_iva"]');
        const irsField = document.querySelector('#id_tag_irs, select[name="tag_irs"]');
        const tsuField = document.querySelector('#id_tag_tsu, select[name="tag_tsu"]');

        if (!descField) return;

        // Criar botão de auto-sugestão com Material Symbol (Unfold usa material-symbols-outlined)
        const suggestButton = document.createElement('button');
        suggestButton.type = 'button';
        suggestButton.className = 'button fiscal-suggest-button';
        suggestButton.innerHTML = '<span class="material-symbols-outlined" style="font-size: 1.25rem; vertical-align: middle; margin-right: 4px;">auto_awesome</span>Sugerir Tags Fiscais';
        suggestButton.style.cssText = 'margin-left: 10px; padding: 6px 12px; font-size: 13px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 4px; cursor: pointer; transition: all 0.3s; display: inline-flex; align-items: center;';

        suggestButton.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.05)';
            this.style.boxShadow = '0 4px 12px rgba(102, 126, 234, 0.4)';
        });

        suggestButton.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
            this.style.boxShadow = 'none';
        });

        suggestButton.addEventListener('click', function(e) {
            e.preventDefault();

            // Obter tags operacionais selecionadas
            const selectedTags = getSelectedOperationalTags(tagsField);

            if (!selectedTags || selectedTags.length === 0) {
                showNotification('⚠️ Selecione primeiro uma tag operacional (ex: Equipamento, Pessoal)', 'warning');
                return;
            }

            // Procurar match baseado nas tags operacionais
            let appliedSuggestions = [];

            for (const tagCode of selectedTags) {
                const mapping = FISCAL_TAG_MAP[tagCode];

                if (mapping) {
                    // Aplicar sugestões
                    if (ircField && mapping.irc) setSelectValue(ircField, mapping.irc);
                    if (ivaField && mapping.iva) setSelectValue(ivaField, mapping.iva);
                    if (irsField && mapping.irs) setSelectValue(irsField, mapping.irs);
                    if (tsuField && mapping.tsu) setSelectValue(tsuField, mapping.tsu);

                    const tagCount = [mapping.irc, mapping.iva, mapping.irs, mapping.tsu].filter(x => x).length;
                    appliedSuggestions.push(`${tagCode} (${tagCount} tags)`);
                }
            }

            if (appliedSuggestions.length > 0) {
                showNotification('✅ Tags fiscais sugeridas: ' + appliedSuggestions.join(', '), 'success');
            } else {
                showNotification('⚠️ Nenhuma sugestão disponível para as tags selecionadas', 'warning');
            }
        });

        // Inserir botão junto aos campos fiscais
        // Procurar pelo primeiro campo fiscal visível (IRC, IVA, IRS ou TSU)
        const firstFiscalField = ircField || ivaField || irsField || tsuField;

        if (firstFiscalField) {
            const fiscalRow = firstFiscalField.closest('.form-row, .field, div[class*="field-tag_"]');
            if (fiscalRow) {
                const buttonContainer = document.createElement('div');
                buttonContainer.style.cssText = 'margin-bottom: 12px; padding: 10px; background: #f8f9fa; border-radius: 6px; border-left: 4px solid #667eea;';

                const label = document.createElement('div');
                label.textContent = '💡 Auto-sugestão:';
                label.style.cssText = 'font-size: 12px; color: #666; margin-bottom: 6px; font-weight: 500;';

                buttonContainer.appendChild(label);
                buttonContainer.appendChild(suggestButton);

                // Inserir ANTES do primeiro campo fiscal
                fiscalRow.parentNode.insertBefore(buttonContainer, fiscalRow);
            }
        }
    }

    function setSelectValue(selectElement, value) {
        if (!selectElement || !value) return false;

        // Verificar se é Select2 (autocomplete do Django Admin)
        const hasSelect2Data = typeof jQuery !== 'undefined' && jQuery(selectElement).data('select2');
        const hasSelect2Class = selectElement.classList.contains('select2-hidden-accessible');

        if (hasSelect2Data || hasSelect2Class) {
            // Para Django autocomplete_fields com Select2
            let option = selectElement.querySelector('option[value="' + value + '"]');

            if (!option) {
                // Criar nova opção com o codigo (PK) como valor e texto
                option = new Option(value, value, true, true);
                selectElement.appendChild(option);
            }

            // Atualizar Select2
            const $select = jQuery(selectElement);
            $select.val(value);
            $select.trigger('change');
            $select.trigger('change.select2');

            return true;
        }

        // Select normal (fallback)
        for (let i = 0; i < selectElement.options.length; i++) {
            if (selectElement.options[i].value === value) {
                selectElement.selectedIndex = i;
                selectElement.dispatchEvent(new Event('change', { bubbles: true }));
                return true;
            }
        }

        return false;
    }

    function showNotification(message, type) {
        // Remover notificações anteriores
        const oldNotif = document.querySelector('.fiscal-notification');
        if (oldNotif) oldNotif.remove();

        const notification = document.createElement('div');
        notification.className = 'fiscal-notification';
        notification.textContent = message;

        const bgColor = type === 'success' ? 'rgb(16, 185, 129)' : 'rgb(245, 158, 11)';
        notification.style.cssText = `
            position: fixed;
            top: 80px;
            right: 20px;
            z-index: 10000;
            padding: 12px 20px;
            background: ${bgColor};
            color: white;
            border-radius: 6px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            font-size: 14px;
            font-weight: 500;
            animation: slideIn 0.3s ease-out;
        `;

        // Adicionar animação
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideIn {
                from { transform: translateX(400px); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            @keyframes slideOut {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(400px); opacity: 0; }
            }
        `;
        document.head.appendChild(style);

        document.body.appendChild(notification);

        // Auto-remover após 4 segundos
        setTimeout(function() {
            notification.style.animation = 'slideOut 0.3s ease-in';
            setTimeout(function() {
                notification.remove();
            }, 300);
        }, 4000);
    }

    // ========== INICIALIZAÇÃO ==========

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            initClickableRows();
            initSelectionTotalListeners();
            setTimeout(makeEnvironmentBadgeClickable, 1000);  // Delay for Unfold to load
            setTimeout(suggestFiscalTags, 500);  // Init fiscal suggestions
        });
    } else {
        initClickableRows();
        initSelectionTotalListeners();
        setTimeout(makeEnvironmentBadgeClickable, 1000);  // Delay for Unfold to load
        setTimeout(suggestFiscalTags, 500);  // Init fiscal suggestions
    }
})();

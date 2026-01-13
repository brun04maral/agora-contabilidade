/* Agora Contabilidade - Custom Admin JavaScript */

document.addEventListener('DOMContentLoaded', function() {
    // Tornar linhas inteiras clicáveis nas listas do admin
    const tableRows = document.querySelectorAll('.change-list table tbody tr');

    tableRows.forEach(function(row) {
        // Adicionar handler de clique para toda a linha
        row.addEventListener('click', function(event) {
            // Verificar se o clique foi em um elemento interativo
            const target = event.target;
            const isInteractive = target.matches('input, select, button, a') ||
                                 target.closest('input, select, button, a');

            // Se não foi em elemento interativo, navegar para o link da linha
            if (!isInteractive) {
                // Procurar pelo link de edição (geralmente na primeira coluna com classe 'field-*')
                const editLink = row.querySelector('th.field-__str__ a, td.field-__str__ a, th:first-child a, td:first-child a');

                if (editLink) {
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
});

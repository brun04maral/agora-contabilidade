# 👤 Plano de Implementação - Página Individual de Sócio

Data de atualização: 16/11/2025
Status: Revisado (modelo por sócio)

==================================================
OBJETIVO
==================================================
Criar uma página dedicada à gestão e análise individual de cada sócio (BA ou RR). A página será aberta a partir de uma listagem/seleção inicial e mostra todos os dados pessoais e profissionais desse sócio, com modo visualização/edição exclusivo por sócio.

==================================================
NAVEGAÇÃO E UI
==================================================
Sidebar:
  - Opção única "Sócios"
  - Ao clicar, apresenta uma lista simples com BA e RR (ou dropdown)
Página principal:
  - Seleciona sócio → Abre página individual
  - Exibe card único com dados informativos/editáveis:
      Nome completo
      Cargo
      Data Nascimento
      NIF
      NISS
      Morada
      Salário base
      Subsídio de alimentação
  - Botão "✏️ Editar" ativa modo edição APENAS para o sócio aberto

==================================================
BASE DE DADOS
==================================================
(Tabela: socios = já existente)
Adicionar/Expandir campos conforme migration planeada (ver especificação anterior).

==================================================
LOGIC LAYER
==================================================
SociosManager: já preparado para gerir dados de sócio único
Principais métodos:
  - obter_socio_por_codigo(codigo)
  - atualizar_socio(codigo, dados)

==================================================
UI LAYER - EXEMPLO DE IMPLEMENTAÇÃO
==================================================
(main file: ui/screens/socio.py)
class SocioScreen(ctk.CTkFrame):
    def __init__(self, parent, db_session, codigo_socio):
        self.manager = SociosManager(db_session)
        self.socio = self.manager.obter_socio_por_codigo(codigo_socio)
        self.modo_edicao = False
        # Cria UI para um sócio apenas
        self.criar_interface()
        self.carregar_dados()
# Ao abrir sócio BA, apenas dados de Bruno Amaral visíveis/editáveis
# Ao abrir sócio RR, apenas dados de Rafael Reigota visíveis/editáveis

==================================================
CHECKLIST DE IMPLEMENTAÇÃO
==================================================
1. Atualizar PLANO_SOCIOS.md com este modelo
2. Implementar ecrã de seleção/rota por sócio
3. Criação/expansão do card único
4. Integrar modo edição/guardar apenas para cada sócio
5. Garantir navegação intuitiva: voltar à lista/início

==================================================
NOTAS FINAIS
==================================================
- Mantém-se possibilidade de futuras estatísticas, gráficos e ligações, mas cada página é autónoma por sócio.
- Organização da documentação simplificada: uma especificação central, cada ficheiro/conceito referenciando apenas um sócio de cada vez na UI.

Última atualização: 16/11/2025

# 👥 Plano de Implementação - Página de Sócios

**Data de criação:** 16/11/2025  
**Status:** 📝 Planeamento  
**Prioridade:** Alta

---

## 🎯 Objetivo

Criar uma página dedicada e detalhada para gestão e análise dos sócios BA (Bruno Amaral) e RR (Rafael Reigota), que será uma **main window** na aplicação, posicionada na sidebar antes de Clientes.

Esta página vai centralizar todas as informações pessoais e profissionais dos sócios, estando conectada na base de dados em todas as partes da app que referenciem sócios, permitindo:
- Listagens diversas
- Eventuais gráficos e análises
- Gestão centralizada de dados pessoais

---

## 📊 Contexto Atual

### Estrutura Existente

**Tabela `socios` (database/models/socio.py):**
```python
id              INTEGER PK
codigo          VARCHAR(2)      # "BA" ou "RR"
nome            VARCHAR(100)    # Nome completo
nif             VARCHAR(9)      # Número fiscal
iban            VARCHAR(34)     # Conta bancária
percentagem     DECIMAL(5,2)    # % da sociedade (50.0)
```

**Constantes:**
```python
Socio.BRUNO = "BA"
Socio.RAFAEL = "RR"
```

### Página Atual - Saldos Pessoais

Já existe uma página **"Saldos Pessoais"** (`ui/screens/saldos.py`) que:
- Lista os saldos pessoais dos sócios
- Mostra breakdown de receitas e despesas
- Permite navegação clicável para Projetos, Despesas, Boletins
- **Status:** Funciona perfeitamente, não precisa de alterações

---

## 🎨 Design da Nova Página

### Posicionamento na Sidebar

```
┌─────────────────────┐
│  Logo Agora         │
├─────────────────────┤
│  📊 Dashboard       │
│  💰 Saldos Pessoais │
│  👥 Sócios         │  ← NOVO (antes de Clientes)
│  👤 Clientes        │
│  📂 Projetos        │
│  ...
└─────────────────────┘
```

### Layout da Página

A página terá uma estrutura **dual-column** para visualizar ambos os sócios lado a lado:

```
┌─────────────────────────────────────────────────────────┐
│  👥 Sócios                                    [Editar]  │
├──────────────────────┬──────────────────────────────────┤
│                      │                                  │
│   BRUNO AMARAL (BA)  │   RAFAEL REIGOTA (RR)           │
│                      │                                  │
│   ┌──────────────┐   │   ┌──────────────┐             │
│   │  INFORMAÇÃO  │   │   │  INFORMAÇÃO  │             │
│   │   PESSOAL    │   │   │   PESSOAL    │             │
│   └──────────────┘   │   └──────────────┘             │
│                      │                                  │
│   • Nome Completo    │   • Nome Completo               │
│   • Cargo            │   • Cargo                       │
│   • Data Nascimento  │   • Data Nascimento             │
│   • NIF              │   • NIF                         │
│   • NISS             │   • NISS                        │
│   • Morada           │   • Morada                      │
│   • Salário Base     │   • Salário Base                │
│   • Sub. Alimentação │   • Sub. Alimentação            │
│                      │                                  │
└──────────────────────┴──────────────────────────────────┘
```

---

## 🗄️ Alterações na Base de Dados

### Migration 022 - Expandir tabela `socios`

**Colunas a adicionar:**

```sql
-- Informação pessoal
cargo               VARCHAR(100) NULL   -- Ex: "Sócio-Gerente", "Diretor Técnico"
data_nascimento     DATE NULL           -- Data de nascimento
niss                VARCHAR(11) NULL    -- Número da Segurança Social
morada              TEXT NULL           -- Morada completa

-- Remuneração
salario_base        DECIMAL(10,2) NULL  -- Salário base mensal
subsidio_alimentacao DECIMAL(10,2) NULL -- Subsídio de alimentação mensal

-- Metadata
created_at          DATETIME DEFAULT CURRENT_TIMESTAMP
updated_at          DATETIME DEFAULT CURRENT_TIMESTAMP
```

**Campos mantidos (já existentes):**
- `id`, `codigo`, `nome`, `nif`, `iban`, `percentagem`

**Nota sobre ligação a despesas recorrentes:**
Os campos `salario_base` e `subsidio_alimentacao` **podem estar linkados** na base de dados às despesas fixas mensais recorrentes (via `despesa_templates`). Esta ligação será implementada numa fase posterior, permitindo:
- Auto-geração de despesas mensais de salários
- Consistência entre valores definidos em Sócios e despesas geradas
- Rastreabilidade de alterações de salário ao longo do tempo

---

## 💻 Implementação Técnica

### 1. Database Layer

**Ficheiro:** `database/models/socio.py` (atualizar modelo existente)

```python
from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, Text
from sqlalchemy.sql import func
from database.base import Base

class Socio(Base):
    __tablename__ = 'socios'
    
    # Campos existentes
    id = Column(Integer, primary_key=True)
    codigo = Column(String(2), unique=True, nullable=False)
    nome = Column(String(100), nullable=False)
    nif = Column(String(9))
    iban = Column(String(34))
    percentagem = Column(Numeric(5, 2), default=50.0)
    
    # Novos campos - Informação Pessoal
    cargo = Column(String(100))
    data_nascimento = Column(Date)
    niss = Column(String(11))
    morada = Column(Text)
    
    # Novos campos - Remuneração
    salario_base = Column(Numeric(10, 2))
    subsidio_alimentacao = Column(Numeric(10, 2))
    
    # Metadata
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Constantes
    BRUNO = "BA"
    RAFAEL = "RR"
    
    def __repr__(self):
        return f"<Socio {self.codigo} - {self.nome}>"
```

**Migration:** `database/migrations/versions/022_expandir_socios.py`

```python
"""Expandir tabela socios com informação pessoal e remuneração

Revision ID: 022
Revises: 021
Create Date: 2025-11-16

"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Adicionar colunas de informação pessoal
    op.add_column('socios', sa.Column('cargo', sa.String(100), nullable=True))
    op.add_column('socios', sa.Column('data_nascimento', sa.Date(), nullable=True))
    op.add_column('socios', sa.Column('niss', sa.String(11), nullable=True))
    op.add_column('socios', sa.Column('morada', sa.Text(), nullable=True))
    
    # Adicionar colunas de remuneração
    op.add_column('socios', sa.Column('salario_base', sa.Numeric(10, 2), nullable=True))
    op.add_column('socios', sa.Column('subsidio_alimentacao', sa.Numeric(10, 2), nullable=True))
    
    # Adicionar metadata
    op.add_column('socios', sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()))
    op.add_column('socios', sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()))

def downgrade():
    op.drop_column('socios', 'updated_at')
    op.drop_column('socios', 'created_at')
    op.drop_column('socios', 'subsidio_alimentacao')
    op.drop_column('socios', 'salario_base')
    op.drop_column('socios', 'morada')
    op.drop_column('socios', 'niss')
    op.drop_column('socios', 'data_nascimento')
    op.drop_column('socios', 'cargo')
```

---

### 2. Logic Layer

**Ficheiro:** `logic/socios.py` (criar novo manager)

```python
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from database.models.socio import Socio
from datetime import date
import logging

logger = logging.getLogger(__name__)

class SociosManager:
    """Manager para gestão de sócios."""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def obter_socio_por_codigo(self, codigo: str) -> Optional[Socio]:
        """Obtém sócio por código (BA ou RR)."""
        return self.db.query(Socio).filter(Socio.codigo == codigo).first()
    
    def obter_todos(self) -> list[Socio]:
        """Obtém todos os sócios ordenados por código."""
        return self.db.query(Socio).order_by(Socio.codigo).all()
    
    def atualizar_socio(self, codigo: str, dados: Dict[str, Any]) -> Optional[Socio]:
        """Atualiza informações de um sócio.
        
        Args:
            codigo: Código do sócio (BA ou RR)
            dados: Dicionário com campos a atualizar
                  - cargo: str
                  - data_nascimento: date
                  - nif: str
                  - niss: str
                  - morada: str
                  - salario_base: Decimal
                  - subsidio_alimentacao: Decimal
        
        Returns:
            Socio atualizado ou None se não encontrado
        """
        socio = self.obter_socio_por_codigo(codigo)
        if not socio:
            logger.warning(f"Sócio {codigo} não encontrado")
            return None
        
        # Atualizar campos
        campos_permitidos = [
            'cargo', 'data_nascimento', 'nif', 'niss', 'morada',
            'salario_base', 'subsidio_alimentacao', 'nome', 'iban'
        ]
        
        for campo, valor in dados.items():
            if campo in campos_permitidos and hasattr(socio, campo):
                setattr(socio, campo, valor)
        
        try:
            self.db.commit()
            self.db.refresh(socio)
            logger.info(f"Sócio {codigo} atualizado com sucesso")
            return socio
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao atualizar sócio {codigo}: {e}")
            raise
    
    def validar_nif(self, nif: str) -> bool:
        """Valida formato de NIF português (9 dígitos)."""
        if not nif:
            return True  # Campo opcional
        return nif.isdigit() and len(nif) == 9
    
    def validar_niss(self, niss: str) -> bool:
        """Valida formato de NISS (11 dígitos)."""
        if not niss:
            return True  # Campo opcional
        return niss.isdigit() and len(niss) == 11
```

---

### 3. UI Layer

**Ficheiro:** `ui/screens/socios.py` (criar novo screen)

```python
import customtkinter as ctk
from typing import Optional
from sqlalchemy.orm import Session
from logic.socios import SociosManager
from database.models.socio import Socio
from assets.resources import get_icon, ICON_USER
import logging
from datetime import datetime
from ui.components.date_picker_dropdown import DatePickerDropdown

logger = logging.getLogger(__name__)

class SociosScreen(ctk.CTkFrame):
    """Screen de gestão de sócios."""
    
    def __init__(self, parent, db_session: Session):
        super().__init__(parent)
        self.db_session = db_session
        self.manager = SociosManager(db_session)
        
        self.socio_ba: Optional[Socio] = None
        self.socio_rr: Optional[Socio] = None
        self.modo_edicao = False
        
        self.criar_interface()
        self.carregar_dados()
    
    def criar_interface(self):
        """Cria interface dual-column."""
        self.configure(fg_color="transparent")
        
        # Header com título e botão editar
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))
        
        # Título com ícone
        icon_img = get_icon(ICON_USER, 22)
        ctk_icon = ctk.CTkImage(light_image=icon_img, size=(22, 22))
        
        titulo_frame = ctk.CTkFrame(header, fg_color="transparent")
        titulo_frame.pack(side="left")
        
        icon_label = ctk.CTkLabel(titulo_frame, image=ctk_icon, text="")
        icon_label.pack(side="left", padx=(0, 10))
        
        titulo = ctk.CTkLabel(
            titulo_frame, 
            text="Sócios",
            font=("Segoe UI", 24, "bold")
        )
        titulo.pack(side="left")
        
        # Botão Editar/Guardar
        self.btn_acao = ctk.CTkButton(
            header,
            text="✏️ Editar",
            command=self.toggle_edicao,
            width=120,
            height=32
        )
        self.btn_acao.pack(side="right")
        
        # Container dual-column
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Configurar grid 2 colunas de igual tamanho
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=1)
        
        # Frame Bruno (esquerda)
        self.frame_ba = self.criar_card_socio(container, "BRUNO AMARAL (BA)")
        self.frame_ba.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # Frame Rafael (direita)
        self.frame_rr = self.criar_card_socio(container, "RAFAEL REIGOTA (RR)")
        self.frame_rr.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
    
    def criar_card_socio(self, parent, titulo: str) -> ctk.CTkFrame:
        """Cria card individual para um sócio."""
        card = ctk.CTkFrame(parent)
        
        # Título do card
        titulo_label = ctk.CTkLabel(
            card,
            text=titulo,
            font=("Segoe UI", 18, "bold")
        )
        titulo_label.pack(pady=(15, 20))
        
        # Separador
        separador = ctk.CTkFrame(card, height=2, fg_color=("gray70", "gray30"))
        separador.pack(fill="x", padx=20, pady=(0, 15))
        
        # Área de campos (scrollable)
        scroll_frame = ctk.CTkScrollableFrame(card, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        # Armazenar referência ao scroll_frame no card para acesso posterior
        card.scroll_frame = scroll_frame
        
        return card
    
    def criar_campos_socio(self, parent, socio: Socio) -> dict:
        """Cria campos de informação de um sócio.
        
        Returns:
            dict: Dicionário com referências aos widgets de input
        """
        campos = {}
        
        # Helper para criar label + entry
        def criar_campo(label_text: str, valor, tipo="text", row=None):
            frame = ctk.CTkFrame(parent, fg_color="transparent")
            frame.pack(fill="x", pady=8)
            
            label = ctk.CTkLabel(frame, text=label_text, width=150, anchor="w")
            label.pack(side="left")
            
            if tipo == "date":
                widget = DatePickerDropdown(frame, width=200)
                if valor:
                    widget.set_date(valor)
                widget.configure(state="disabled")
            elif tipo == "textarea":
                widget = ctk.CTkTextbox(frame, height=80, width=200)
                if valor:
                    widget.insert("1.0", valor)
                widget.configure(state="disabled")
            else:  # text/number
                widget = ctk.CTkEntry(frame, width=200)
                if valor:
                    widget.insert(0, str(valor))
                widget.configure(state="disabled")
            
            widget.pack(side="right")
            return widget
        
        # Campos
        campos['nome'] = criar_campo("Nome Completo:", socio.nome)
        campos['cargo'] = criar_campo("Cargo:", socio.cargo)
        campos['data_nascimento'] = criar_campo(
            "Data Nascimento:", 
            socio.data_nascimento, 
            tipo="date"
        )
        campos['nif'] = criar_campo("NIF:", socio.nif)
        campos['niss'] = criar_campo("NISS:", socio.niss)
        campos['morada'] = criar_campo("Morada:", socio.morada, tipo="textarea")
        campos['salario_base'] = criar_campo(
            "Salário Base (€):", 
            socio.salario_base
        )
        campos['subsidio_alimentacao'] = criar_campo(
            "Sub. Alimentação (€):", 
            socio.subsidio_alimentacao
        )
        
        return campos
    
    def carregar_dados(self):
        """Carrega dados dos sócios da base de dados."""
        try:
            self.socio_ba = self.manager.obter_socio_por_codigo(Socio.BRUNO)
            self.socio_rr = self.manager.obter_socio_por_codigo(Socio.RAFAEL)
            
            if not self.socio_ba or not self.socio_rr:
                logger.error("Sócios BA ou RR não encontrados na base de dados")
                return
            
            # Criar campos nos cards
            self.campos_ba = self.criar_campos_socio(
                self.frame_ba.scroll_frame, 
                self.socio_ba
            )
            self.campos_rr = self.criar_campos_socio(
                self.frame_rr.scroll_frame, 
                self.socio_rr
            )
            
        except Exception as e:
            logger.error(f"Erro ao carregar dados de sócios: {e}")
    
    def toggle_edicao(self):
        """Alterna entre modo visualização e edição."""
        if not self.modo_edicao:
            # Entrar em modo edição
            self.ativar_edicao()
            self.btn_acao.configure(text="💾 Guardar")
            self.modo_edicao = True
        else:
            # Guardar alterações
            if self.guardar_alteracoes():
                self.desativar_edicao()
                self.btn_acao.configure(text="✏️ Editar")
                self.modo_edicao = False
    
    def ativar_edicao(self):
        """Ativa campos para edição."""
        for campo in self.campos_ba.values():
            campo.configure(state="normal")
        for campo in self.campos_rr.values():
            campo.configure(state="normal")
    
    def desativar_edicao(self):
        """Desativa campos (apenas visualização)."""
        for campo in self.campos_ba.values():
            campo.configure(state="disabled")
        for campo in self.campos_rr.values():
            campo.configure(state="disabled")
    
    def guardar_alteracoes(self) -> bool:
        """Guarda alterações dos sócios.
        
        Returns:
            bool: True se guardado com sucesso
        """
        try:
            # Validar e recolher dados BA
            dados_ba = self.recolher_dados_form(self.campos_ba)
            if not self.validar_dados(dados_ba, "BA"):
                return False
            
            # Validar e recolher dados RR
            dados_rr = self.recolher_dados_form(self.campos_rr)
            if not self.validar_dados(dados_rr, "RR"):
                return False
            
            # Atualizar na base de dados
            self.manager.atualizar_socio(Socio.BRUNO, dados_ba)
            self.manager.atualizar_socio(Socio.RAFAEL, dados_rr)
            
            # Recarregar dados
            self.carregar_dados()
            
            # Mensagem de sucesso
            # TODO: Adicionar toast/notification
            logger.info("Dados dos sócios atualizados com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao guardar alterações: {e}")
            # TODO: Mostrar erro ao utilizador
            return False
    
    def recolher_dados_form(self, campos: dict) -> dict:
        """Recolhe dados do formulário."""
        dados = {}
        
        for nome, widget in campos.items():
            if isinstance(widget, DatePickerDropdown):
                dados[nome] = widget.get_date()
            elif isinstance(widget, ctk.CTkTextbox):
                dados[nome] = widget.get("1.0", "end-1c").strip()
            else:
                valor = widget.get().strip()
                dados[nome] = valor if valor else None
        
        return dados
    
    def validar_dados(self, dados: dict, codigo: str) -> bool:
        """Valida dados do formulário."""
        # Validar NIF
        if dados.get('nif') and not self.manager.validar_nif(dados['nif']):
            logger.error(f"NIF inválido para {codigo}")
            # TODO: Mostrar erro específico
            return False
        
        # Validar NISS
        if dados.get('niss') and not self.manager.validar_niss(dados['niss']):
            logger.error(f"NISS inválido para {codigo}")
            # TODO: Mostrar erro específico
            return False
        
        # Validar valores numéricos
        try:
            if dados.get('salario_base'):
                float(dados['salario_base'])
            if dados.get('subsidio_alimentacao'):
                float(dados['subsidio_alimentacao'])
        except ValueError:
            logger.error(f"Valores de remuneração inválidos para {codigo}")
            return False
        
        return True
```

**Ficheiro:** `ui/components/sidebar.py` (adicionar menu)

```python
# Adicionar após menu "Saldos Pessoais" e antes de "Clientes"

self.btn_socios = self.criar_botao_menu(
    "Sócios",
    ICON_USER,  # Importar do resources.py
    lambda: self.parent.mostrar_tela("socios")
)
```

**Ficheiro:** `assets/resources.py` (adicionar ícone se necessário)

```python
# Verificar se ICON_USER já existe, senão adicionar
ICON_USER = "..."  # Base64 de ícone de utilizador
```

---

## 📋 Checklist de Implementação

### Fase 1: Database (Migration 022)
- [ ] Atualizar modelo `Socio` em `database/models/socio.py`
- [ ] Criar migration `022_expandir_socios.py`
- [ ] Executar migration localmente
- [ ] Verificar colunas adicionadas com `PRAGMA table_info(socios)`
- [ ] Testar rollback da migration

### Fase 2: Logic Layer
- [ ] Criar `logic/socios.py` com `SociosManager`
- [ ] Implementar método `obter_socio_por_codigo()`
- [ ] Implementar método `obter_todos()`
- [ ] Implementar método `atualizar_socio()`
- [ ] Implementar validações (NIF, NISS)
- [ ] Escrever testes unitários

### Fase 3: UI Layer
- [ ] Criar `ui/screens/socios.py`
- [ ] Implementar layout dual-column
- [ ] Implementar modo visualização/edição
- [ ] Adicionar validações no frontend
- [ ] Integrar `DatePickerDropdown` para data de nascimento
- [ ] Adicionar feedback de sucesso/erro ao utilizador
- [ ] Adicionar ícone `ICON_USER` se necessário
- [ ] Atualizar `sidebar.py` com novo menu

### Fase 4: Integração
- [ ] Registar screen em `main.py`
- [ ] Testar navegação sidebar → Sócios
- [ ] Testar carregamento de dados
- [ ] Testar modo edição completo (BA e RR)
- [ ] Testar validações (NIF inválido, NISS inválido, etc.)
- [ ] Testar persistência de dados

### Fase 5: Documentação
- [ ] Atualizar `ARCHITECTURE.md`
- [ ] Atualizar `DATABASE_SCHEMA.md`
- [ ] Atualizar `CURRENT_STATE.md`
- [ ] Atualizar `CHANGELOG.md`
- [ ] Adicionar screenshots (opcional)

---

## 🎯 Comportamento Esperado

### Visualização (Padrão)
- Página abre em **modo leitura**
- Todos os campos desativados (cinza)
- Botão "✏️ Editar" visível no header
- Dados carregados da base de dados
- Layout dual-column mostra ambos os sócios lado a lado

### Modo Edição
- Utilizador clica "✏️ Editar"
- Todos os campos ficam ativos (brancos)
- Botão muda para "💾 Guardar"
- Campos editáveis:
  - Nome Completo
  - Cargo
  - Data Nascimento (com `DatePickerDropdown`)
  - NIF
  - NISS
  - Morada (textarea)
  - Salário Base
  - Subsídio Alimentação

### Guardar
- Utilizador clica "💾 Guardar"
- Sistema valida todos os campos:
  - NIF: 9 dígitos
  - NISS: 11 dígitos
  - Valores monetários: formato válido
- Se válido:
  - Grava na base de dados
  - Mostra mensagem de sucesso
  - Volta ao modo visualização
- Se inválido:
  - Mostra erro específico
  - Mantém em modo edição

---

## 🔮 Funcionalidades Futuras

Após a implementação da **primeira secção** (informação pessoal), podemos adicionar:

### Secção 2: Estatísticas Pessoais
- Total de projetos geridos
- Total de prémios recebidos
- Total de despesas pessoais
- Total de boletins emitidos
- Gráficos de evolução temporal

### Secção 3: Projetos em Curso
- Lista de projetos ativos do sócio
- Progresso e deadlines
- Clique para navegar ao projeto

### Secção 4: Histórico de Remuneração
- Histórico de alterações de salário
- Gráfico de evolução de remuneração
- Total recebido por ano

### Secção 5: Ligação a Despesas Recorrentes
- Auto-geração de despesas mensais de salários
- Consistência entre Sócios e Templates de Despesas
- Alerta de inconsistências

---

## 📝 Notas Técnicas

### Decisões de Design

1. **Dual-column layout:** Permite comparação visual direta entre sócios
2. **Modo edição único:** Edita ambos os sócios simultaneamente (simplifica UX)
3. **Campos opcionais:** Todos os novos campos são nullable (flexibilidade)
4. **Validações frontend e backend:** Dupla camada de segurança
5. **DatePickerDropdown:** Consistência com resto da aplicação
6. **Scroll interno:** Campos cabem em diferentes tamanhos de ecrã

### Performance

- **Queries simples:** `obter_socio_por_codigo()` usa WHERE em coluna indexada
- **Sem cálculos pesados:** Apenas leitura/escrita de campos
- **Carregamento rápido:** Apenas 2 registos (BA e RR)

### Segurança

- **Dados sensíveis:** NIF, NISS, morada devem ser tratados com cuidado
- **Futura encriptação:** Considerar encriptar campos sensíveis na DB
- **Logs seguros:** Não logar valores de campos pessoais

### Manutenibilidade

- **Manager separado:** Lógica isolada, fácil de testar
- **Validações reutilizáveis:** Métodos de validação podem ser usados noutros contextos
- **Screen modular:** Card creator permite fácil adição de novos campos

---

## 🚀 Próximos Passos

1. **Revisar este plano** com utilizador (aprovar design e campos)
2. **Criar migration 022** e testar localmente
3. **Implementar Logic Layer** com testes
4. **Implementar UI Layer** com design proposto
5. **Testar integração** completa
6. **Documentar** e atualizar ficheiros relevantes
7. **Deploy** e validação em produção

---

**Mantido por:** Equipa Agora  
**Última atualização:** 16/11/2025

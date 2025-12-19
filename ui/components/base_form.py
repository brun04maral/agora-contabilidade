# -*- coding: utf-8 -*-
"""
BaseForm - Template base para formulários CRUD

GUIA RÁPIDO PARA DEVS:
======================

BaseForm é um template genérico para criar formulários CRUD consistentes.
Similar ao BaseScreen, usa o padrão Template Method com slots personalizáveis.

SUPORTE LAYOUTS:
----------------
- 1 coluna (default): Forms simples, campos empilhados verticalmente
- 2 colunas: Forms complexos, melhor aproveitamento de espaço horizontal

Uso:
    # 1 coluna (default)
    super().__init__(parent, db_session)

    # 2 colunas
    super().__init__(parent, db_session, columns=2)

Campos podem ter colspan=2 para ocupar largura total (só em layout 2 colunas):
    {"key": "obs", "type": "textarea", "colspan": 2}

MÉTODOS ABSTRATOS OBRIGATÓRIOS (4):
-----------------------------------
1. get_form_title() → str
   - Retorna título do form (ex: "Novo Cliente", "Editar Fornecedor")

2. get_form_icon() → PIL.Image|None
   - Retorna ícone PIL ou None (ex: get_icon(CLIENTES, size=(28, 28)))

3. get_fields_config() → List[dict]
   - Retorna lista de campos do formulário com configuração
   - Formato de cada campo:
     {
         "key": "nome_campo",           # ID único do campo (obrigatório)
         "label": "Nome do Campo",      # Label exibido (obrigatório)
         "type": "text",                # Tipo: text, number, dropdown, checkbox, date, textarea (obrigatório)
         "required": True,              # Campo obrigatório? (opcional, default=False)
         "placeholder": "Digite...",    # Placeholder para entries (opcional)
         "values": [...],               # Valores para dropdown (obrigatório se type=dropdown)
         "default": valor,              # Valor default (opcional)
         "width": 300,                  # Largura do widget (opcional)
         "validator": func,             # Função de validação custom (opcional)
         "readonly": False,             # Campo read-only? (opcional, default=False)
         "colspan": 2,                  # Ocupa 2 colunas (só em layout 2 colunas, opcional, default=1)
     }

4. on_save(data: dict) → bool|str
   - Chamado quando usuário clica "Guardar"
   - Recebe dict com todos os valores do form
   - Retorna True se sucesso, ou str com mensagem de erro

MÉTODOS UTILITÁRIOS:
-------------------
- set_data(initial_data: dict) - Preenche form com dados iniciais (modo edit)
- get_form_data() → dict - Retorna dict com todos os valores atuais
- set_error_message(msg: str) - Mostra mensagem de erro
- clear_fields() - Limpa todos os campos
- validate_fields() → dict|None - Valida campos, retorna erros ou None
- after_save_callback() - Override para executar após save bem-sucedido
- after_cancel_callback() - Override para executar após cancelar

SLOTS PERSONALIZÁVEIS (4):
--------------------------
- header_slot(parent) - Header customizado (default: ícone + título)
- fields_slot(parent) - Campos customizados (default: cria campos de field_config)
- footer_slot(parent) - Footer customizado (default: botões Guardar/Cancelar)
- error_slot(parent) - Área de erro customizada (default: label vermelho)

EXEMPLO MÍNIMO:
--------------
class ClienteFormScreen(BaseForm):
    def get_form_title(self):
        return "Novo Cliente"

    def get_form_icon(self):
        return get_icon(CLIENTES, size=(28, 28))

    def get_fields_config(self):
        return [
            {"key": "nome", "label": "Nome", "type": "text", "required": True},
            {"key": "nif", "label": "NIF", "type": "text"},
            {"key": "email", "label": "Email", "type": "text", "required": True},
        ]

    def on_save(self, data):
        # Salvar no banco
        cliente = self.manager.criar_cliente(data)
        return True  # ou "Erro: NIF inválido"

LAYOUT:
-------
┌─────────────────────────────────────┐
│ [ícone] Título do Form              │ ← header_slot
├─────────────────────────────────────┤
│ Label 1:  [_______________]         │
│ Label 2:  [_______________]         │ ← fields_slot (scrollable)
│ Label 3:  [▼ dropdown     ]         │
│ ...                                 │
├─────────────────────────────────────┤
│ ⚠️ Erro: campo X obrigatório        │ ← error_slot
│ [Cancelar]  [✅ Guardar]            │ ← footer_slot
└─────────────────────────────────────┘
"""

import customtkinter as ctk
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Callable, Optional
from tkinter import messagebox
from tkcalendar import DateEntry
import datetime


class BaseForm(ctk.CTkFrame, ABC):
    """
    Template base abstrato para formulários CRUD

    Fornece estrutura consistente, validação e API unificada para todos os forms.
    """

    def __init__(self,
                 parent,
                 db_session=None,
                 columns: int = 1,
                 initial_data: Optional[Dict[str, Any]] = None,
                 on_cancel_callback: Optional[Callable] = None,
                 **kwargs):
        """
        Initialize base form

        Args:
            parent: Parent widget
            db_session: SQLAlchemy database session (opcional)
            columns: Número de colunas no layout (1 ou 2, default=1)
            initial_data: Dados iniciais para preencher form (modo edit)
            on_cancel_callback: Callback ao cancelar
        """
        super().__init__(parent, **kwargs)

        self.db_session = db_session
        self.num_columns = columns  # Store layout configuration (1 or 2)
        self.initial_data = initial_data or {}
        self._on_cancel_callback = on_cancel_callback

        # Validate columns parameter
        if self.num_columns not in [1, 2]:
            raise ValueError(f"columns must be 1 or 2, got {self.num_columns}")

        # Storage para widgets de campos
        self.field_widgets = {}  # {"key": widget}

        # Configure
        self.configure(fg_color="transparent")

        # Build layout
        self._build_layout()

        # Load initial data if provided
        if self.initial_data:
            self.set_data(self.initial_data)

    # ===== ABSTRACT METHODS (OBRIGATÓRIOS) =====

    @abstractmethod
    def get_form_title(self) -> str:
        """Return form title"""
        raise NotImplementedError("Subclasses must implement get_form_title()")

    @abstractmethod
    def get_form_icon(self):
        """Return form icon (PIL Image or None)"""
        raise NotImplementedError("Subclasses must implement get_form_icon()")

    @abstractmethod
    def get_fields_config(self) -> List[Dict[str, Any]]:
        """
        Return list of field configurations

        Each field dict should have:
        - key: str (unique identifier)
        - label: str (displayed label)
        - type: str (text, number, dropdown, checkbox, date, textarea)
        - required: bool (optional, default=False)
        - placeholder: str (optional)
        - values: List (required for dropdown)
        - default: Any (optional)
        - width: int (optional)
        - validator: Callable (optional)
        - readonly: bool (optional, default=False)
        """
        raise NotImplementedError("Subclasses must implement get_fields_config()")

    @abstractmethod
    def on_save(self, data: Dict[str, Any]) -> bool | str:
        """
        Called when user clicks save

        Args:
            data: Dict with all form values

        Returns:
            True if success, or error message string
        """
        raise NotImplementedError("Subclasses must implement on_save()")

    # ===== INTERNAL LAYOUT METHODS =====

    def _build_layout(self):
        """Build complete form layout"""
        # Main container
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=30, pady=30)

        # Header
        header_container = ctk.CTkFrame(main_container, fg_color="transparent")
        header_container.pack(fill="x", pady=(0, 20))
        self.header_slot(header_container)

        # Fields (scrollable)
        fields_frame = ctk.CTkScrollableFrame(
            main_container,
            fg_color="transparent",
            height=400
        )
        fields_frame.pack(fill="both", expand=True, pady=(0, 20))
        self.fields_slot(fields_frame)

        # Error message
        error_container = ctk.CTkFrame(main_container, fg_color="transparent")
        error_container.pack(fill="x", pady=(0, 10))
        self.error_slot(error_container)

        # Footer
        footer_container = ctk.CTkFrame(main_container, fg_color="transparent")
        footer_container.pack(fill="x")
        self.footer_slot(footer_container)

    # ===== SLOTS (PERSONALIZÁVEIS) =====

    def header_slot(self, parent):
        """Create form header (default: icon + title)"""
        # Title with icon
        icon_pil = self.get_form_icon()

        if icon_pil:
            icon_ctk = ctk.CTkImage(
                light_image=icon_pil,
                dark_image=icon_pil,
                size=(28, 28)
            )
            title_label = ctk.CTkLabel(
                parent,
                image=icon_ctk,
                text=f" {self.get_form_title()}",
                compound="left",
                font=ctk.CTkFont(size=24, weight="bold")
            )
        else:
            title_label = ctk.CTkLabel(
                parent,
                text=self.get_form_title(),
                font=ctk.CTkFont(size=24, weight="bold")
            )

        title_label.pack(side="left")

    def fields_slot(self, parent):
        """
        Create form fields with flexible layout (1 or 2 columns)

        Layout 1 coluna: campos empilhados verticalmente (pack)
        Layout 2 colunas: campos em grid 2x com suporte a colspan
        """
        fields_config = self.get_fields_config()

        if self.num_columns == 1:
            # ========== LAYOUT 1 COLUNA (PACK - ATUAL) ==========
            # Mantém compatibilidade total com forms existentes
            for field_config in fields_config:
                field_frame = self._create_field(parent, field_config)
                field_frame.pack(fill="x", pady=(0, 15))

        elif self.num_columns == 2:
            # ========== LAYOUT 2 COLUNAS (GRID - NOVO) ==========
            # Container com grid para layout 2 colunas
            grid_frame = ctk.CTkFrame(parent, fg_color="transparent")
            grid_frame.pack(fill="both", expand=True, padx=0, pady=0)

            # Configurar 2 colunas com peso igual
            grid_frame.grid_columnconfigure(0, weight=1)
            grid_frame.grid_columnconfigure(1, weight=1)

            # Posicionar campos em grid
            row = 0
            col = 0

            for field_config in fields_config:
                # Obter colspan (default=1)
                colspan = field_config.get("colspan", 1)

                # Criar campo
                field_frame = self._create_field(grid_frame, field_config)

                # Posicionar em grid
                field_frame.grid(
                    row=row,
                    column=col,
                    columnspan=colspan,
                    sticky="ew",
                    padx=10,
                    pady=(0, 15)
                )

                # Calcular próxima posição
                if colspan == 2:
                    # Campo full-width: próximo campo na linha seguinte, coluna 0
                    row += 1
                    col = 0
                else:
                    # Campo normal (1 coluna): avançar coluna
                    col += 1
                    if col >= 2:
                        # Completou linha: próxima linha, coluna 0
                        row += 1
                        col = 0

    def footer_slot(self, parent):
        """Create form footer (default: Cancel + Save buttons)"""
        # Cancel button (left)
        cancel_btn = ctk.CTkButton(
            parent,
            text="Cancelar",
            command=self._handle_cancel,
            width=120,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color=("#95a5a6", "#7f8c8d"),
            hover_color=("#7f8c8d", "#6c7a7b")
        )
        cancel_btn.pack(side="left", padx=(0, 10))

        # Save button (right)
        self.save_btn = ctk.CTkButton(
            parent,
            text="✅ Guardar",
            command=self._handle_save,
            width=140,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("#27AE60", "#229954"),
            hover_color=("#229954", "#1E8449")
        )
        self.save_btn.pack(side="left")

    def error_slot(self, parent):
        """Create error message area (default: red label)"""
        self.error_label = ctk.CTkLabel(
            parent,
            text="",
            font=ctk.CTkFont(size=13),
            text_color=("#E74C3C", "#C0392B")
        )
        self.error_label.pack()

    # ===== FIELD CREATION (INTERNAL) =====

    def _create_field(self, parent, config: Dict[str, Any]) -> ctk.CTkFrame:
        """
        Create a single field based on config

        Args:
            parent: Parent container
            config: Field configuration dict

        Returns:
            Field frame (NOT packed/gridded - positioning done by caller)
        """
        field_type = config.get("type")
        key = config.get("key")
        label = config.get("label", key)
        required = config.get("required", False)
        width = config.get("width", 400)
        readonly = config.get("readonly", False)

        # Field container (NOT packed - positioning done by fields_slot)
        field_frame = ctk.CTkFrame(parent, fg_color="transparent")

        # Label with required indicator
        label_text = f"{label}{'*' if required else ''}"
        field_label = ctk.CTkLabel(
            field_frame,
            text=label_text,
            font=ctk.CTkFont(size=13, weight="bold" if required else "normal"),
            anchor="w"
        )
        field_label.pack(anchor="w", pady=(0, 5))

        # Create widget based on type
        widget = None

        if field_type == "text":
            widget = ctk.CTkEntry(
                field_frame,
                placeholder_text=config.get("placeholder", ""),
                width=width,
                height=35,
                state="readonly" if readonly else "normal"
            )
            widget.pack(anchor="w")

        elif field_type == "number":
            widget = ctk.CTkEntry(
                field_frame,
                placeholder_text=config.get("placeholder", "0"),
                width=width,
                height=35,
                state="readonly" if readonly else "normal"
            )
            widget.pack(anchor="w")
            # Add validation for numbers only
            widget.configure(validate="key", validatecommand=(widget.register(self._validate_number), '%P'))

        elif field_type == "dropdown":
            values = config.get("values", [])
            default = config.get("default", values[0] if values else "")

            var = ctk.StringVar(value=default)
            widget = ctk.CTkOptionMenu(
                field_frame,
                variable=var,
                values=values,
                width=width,
                height=35,
                state="disabled" if readonly else "normal"
            )
            widget.pack(anchor="w")
            # Store variable for later retrieval
            widget._var = var

        elif field_type == "checkbox":
            var = ctk.BooleanVar(value=config.get("default", False))
            widget = ctk.CTkCheckBox(
                field_frame,
                text="",
                variable=var,
                font=ctk.CTkFont(size=13),
                state="disabled" if readonly else "normal"
            )
            widget.pack(anchor="w")
            # Store variable for later retrieval
            widget._var = var

        elif field_type == "date":
            widget = DateEntry(
                field_frame,
                width=width // 8,  # DateEntry uses character width
                background='darkblue',
                foreground='white',
                borderwidth=2,
                font=('Arial', 11),
                state="readonly" if readonly else "normal"
            )
            widget.pack(anchor="w")

        elif field_type == "textarea":
            widget = ctk.CTkTextbox(
                field_frame,
                width=width,
                height=100,
                font=ctk.CTkFont(size=13)
            )
            widget.pack(anchor="w")
            if readonly:
                widget.configure(state="disabled")

        else:
            raise ValueError(f"Unsupported field type: {field_type}")

        # Store widget for later access
        self.field_widgets[key] = {
            "widget": widget,
            "config": config
        }

        # Set default value if provided
        default = config.get("default")
        if default is not None and field_type not in ["dropdown", "checkbox"]:
            self._set_field_value(key, default)

        # Return field frame (positioning done by caller)
        return field_frame

    def _validate_number(self, value):
        """Validate that input is a valid number"""
        if value == "" or value == "-":
            return True
        try:
            float(value)
            return True
        except ValueError:
            return False

    # ===== PUBLIC API METHODS =====

    def set_data(self, data: Dict[str, Any]):
        """
        Populate form with data

        Args:
            data: Dict with field values (keys match field config keys)
        """
        for key, value in data.items():
            if key in self.field_widgets:
                self._set_field_value(key, value)

    def get_form_data(self) -> Dict[str, Any]:
        """
        Get current form data

        Returns:
            Dict with all field values
        """
        data = {}

        for key, field_info in self.field_widgets.items():
            widget = field_info["widget"]
            field_config = field_info["config"]
            field_type = field_config.get("type")

            if field_type == "text" or field_type == "number":
                data[key] = widget.get()

            elif field_type == "dropdown":
                data[key] = widget._var.get()

            elif field_type == "checkbox":
                data[key] = widget._var.get()

            elif field_type == "date":
                try:
                    data[key] = widget.get_date()
                except:
                    data[key] = None

            elif field_type == "textarea":
                data[key] = widget.get("1.0", "end-1c")

        return data

    def set_error_message(self, msg: str):
        """Show error message"""
        if hasattr(self, 'error_label'):
            self.error_label.configure(text=f"⚠️ {msg}")

    def clear_error_message(self):
        """Clear error message"""
        if hasattr(self, 'error_label'):
            self.error_label.configure(text="")

    def clear_fields(self):
        """Clear all form fields"""
        for key in self.field_widgets.keys():
            self._set_field_value(key, "")

    def validate_fields(self) -> Optional[Dict[str, str]]:
        """
        Validate all fields

        Returns:
            Dict with errors {"field_key": "error_message"} or None if valid
        """
        errors = {}
        data = self.get_form_data()

        for key, field_info in self.field_widgets.items():
            config = field_info["config"]
            value = data.get(key)

            # Check required fields
            if config.get("required", False):
                if value is None or value == "" or (isinstance(value, str) and not value.strip()):
                    errors[key] = f"{config.get('label', key)} é obrigatório"

            # Run custom validator if provided
            validator = config.get("validator")
            if validator and value:
                try:
                    if not validator(value):
                        errors[key] = f"{config.get('label', key)} é inválido"
                except Exception as e:
                    errors[key] = str(e)

        return errors if errors else None

    def after_save_callback(self):
        """
        Override this to execute code after successful save
        Default: does nothing
        """
        pass

    def after_cancel_callback(self):
        """
        Override this to execute code after cancel
        Default: calls on_cancel_callback if provided
        """
        if self._on_cancel_callback:
            self._on_cancel_callback()

    # ===== INTERNAL HELPERS =====

    def _set_field_value(self, key: str, value: Any):
        """Set value for a specific field"""
        if key not in self.field_widgets:
            return

        field_info = self.field_widgets[key]
        widget = field_info["widget"]
        field_config = field_info["config"]
        field_type = field_config.get("type")

        if field_type == "text" or field_type == "number":
            widget.delete(0, "end")
            if value:
                widget.insert(0, str(value))

        elif field_type == "dropdown":
            if hasattr(widget, '_var'):
                widget._var.set(str(value))

        elif field_type == "checkbox":
            if hasattr(widget, '_var'):
                widget._var.set(bool(value))

        elif field_type == "date":
            if isinstance(value, datetime.date):
                widget.set_date(value)
            elif isinstance(value, str):
                try:
                    date_obj = datetime.datetime.strptime(value, "%Y-%m-%d").date()
                    widget.set_date(date_obj)
                except:
                    pass

        elif field_type == "textarea":
            widget.delete("1.0", "end")
            if value:
                widget.insert("1.0", str(value))

    def _handle_save(self):
        """Handle save button click"""
        self.clear_error_message()

        # Validate fields
        errors = self.validate_fields()
        if errors:
            # Show first error
            first_error = list(errors.values())[0]
            self.set_error_message(first_error)
            return

        # Get form data
        data = self.get_form_data()

        # Call subclass on_save
        result = self.on_save(data)

        if result is True:
            # Success
            messagebox.showinfo("Sucesso", "Guardado com sucesso!")
            self.after_save_callback()
        else:
            # Error (result is error message)
            self.set_error_message(str(result))

    def _handle_cancel(self):
        """Handle cancel button click"""
        self.after_cancel_callback()

import customtkinter as ctk
from utils.base_dialogs import BaseDialogMedium
from tkinter import messagebox
from sqlalchemy.orm import Session
from logic.orcamentos import OrcamentoManager
from logic.freelancers import FreelancersManager
from logic.fornecedores import FornecedoresManager
from database.models.orcamento import OrcamentoReparticao
from decimal import Decimal
from typing import Optional, Dict

class ComissaoDialog(BaseDialogMedium):
    def __init__(
        self,
        parent,
        db_session: Session,
        orcamento_id: int,
        base_calculo: Decimal,
        item_id: Optional[int] = None
    ):
        super().__init__(parent, title="Adicionar Comissão" if not item_id else "Editar Comissão", width=500, height=450)
        self.db_session = db_session
        self.manager = OrcamentoManager(db_session)
        self.freelancers_manager = FreelancersManager(db_session)
        self.fornecedores_manager = FornecedoresManager(db_session)
        self.orcamento_id = orcamento_id
        self.base_calculo = base_calculo
        self.item_id = item_id
        self.success = False

        self.beneficiarios_map: Dict[str, str] = {}
        self._carregar_beneficiarios()

        self.create_widgets()
        if item_id:
            self.carregar_dados()
        self.atualizar_total()

    def _carregar_beneficiarios(self):
        self.beneficiarios_map["BA"] = "BA - Bruno Amaral"
        self.beneficiarios_map["RR"] = "RR - Rafael Ribeiro"
        self.beneficiarios_map["AGORA"] = "AGORA - Empresa"
        try:
            freelancers = self.freelancers_manager.listar_ativos()
            for freelancer in freelancers:
                key = f"FREELANCER_{freelancer.id}"
                self.beneficiarios_map[key] = f"{key} - {freelancer.nome}"
        except:
            pass
        try:
            fornecedores = self.fornecedores_manager.listar_ativos()
            for fornecedor in fornecedores:
                key = f"FORNECEDOR_{fornecedor.id}"
                self.beneficiarios_map[key] = f"{key} - {fornecedor.nome}"
        except:
            pass

    def create_widgets(self):
        main = self.main_frame

        ctk.CTkLabel(main, text="Comissão - LADO EMPRESA", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(0, 20))
        ctk.CTkLabel(main, text="Beneficiário: *", font=ctk.CTkFont(size=13, weight="bold"), text_color="#f44336").pack(anchor="w", pady=(0, 5))

        dropdown_values = list(self.beneficiarios_map.values())
        self.beneficiario_var = ctk.StringVar(value="")
        self.beneficiario_dropdown = ctk.CTkOptionMenu(
            main,
            variable=self.beneficiario_var,
            values=dropdown_values if dropdown_values else ["BA - Bruno Amaral", "RR - Rafael Ribeiro", "AGORA - Empresa"],
            height=35
        )
        self.beneficiario_dropdown.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(main, text="Descrição:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(0, 5))
        self.descricao_entry = ctk.CTkEntry(main, placeholder_text="Ex: Comissão de Venda", height=35)
        self.descricao_entry.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(main, text="Percentagem (%):", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(0, 5))
        self.percentagem_entry = ctk.CTkEntry(main, placeholder_text="Ex: 5.125 (suporta 3 decimais)", height=35)
        self.percentagem_entry.pack(fill="x", pady=(0, 15))
        self.percentagem_entry.bind("<KeyRelease>", lambda e: self.atualizar_total())

        ctk.CTkLabel(main, text="Base de Cálculo:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(0, 5))
        self.base_label = ctk.CTkLabel(main, text=f"€{float(self.base_calculo):.2f}", font=ctk.CTkFont(size=14, weight="bold"),
                                       fg_color=("#e3f2fd", "#1e3a5f"), corner_radius=6, padx=15, pady=10, anchor="w")
        self.base_label.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(main, text="Total Calculado:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(0, 5))
        self.total_label = ctk.CTkLabel(main, text="€0.00", font=ctk.CTkFont(size=18, weight="bold"),
                                        fg_color=("#e8f5e0", "#2b4a2b"), corner_radius=6, padx=15, pady=10, anchor="w")
        self.total_label.pack(fill="x", pady=(0, 20))

        btn_frame = ctk.CTkFrame(main, fg_color="transparent")
        btn_frame.pack(fill="x")
        ctk.CTkButton(btn_frame, text="Cancelar", command=self.destroy, width=120, fg_color="gray", hover_color="#5a5a5a").pack(side="left", padx=(0, 10))
        ctk.CTkButton(btn_frame, text="Gravar", command=self.gravar, width=120, fg_color="#9C27B0", hover_color="#7B1FA2").pack(side="right")

    def atualizar_total(self):
        try:
            percentagem_str = self.percentagem_entry.get().strip()
            if percentagem_str:
                percentagem = Decimal(percentagem_str.replace(',', '.'))
                total = self.base_calculo * (percentagem / Decimal('100'))
                self.total_label.configure(text=f"€{float(total):.2f}")
            else:
                self.total_label.configure(text="€0.00")
        except (ValueError, Exception):
            self.total_label.configure(text="€0.00")

    def carregar_dados(self):
        item = self.db_session.query(OrcamentoReparticao).filter(OrcamentoReparticao.id == self.item_id).first()
        if not item:
            messagebox.showerror("Erro", "Item não encontrado!")
            self.destroy()
            return
        if item.beneficiario:
            display_name = self.beneficiarios_map.get(item.beneficiario, item.beneficiario)
            self.beneficiario_var.set(display_name)
        if item.descricao:
            self.descricao_entry.delete(0, "end")
            self.descricao_entry.insert(0, item.descricao)
        if item.percentagem:
            self.percentagem_entry.delete(0, "end")
            self.percentagem_entry.insert(0, str(float(item.percentagem)))
        if item.base_calculo:
            self.base_calculo = item.base_calculo
            self.base_label.configure(text=f"€{float(self.base_calculo):.2f}")
        self.atualizar_total()

    def gravar(self):
        try:
            beneficiario_display = self.beneficiario_var.get()
            if not beneficiario_display:
                messagebox.showwarning("Aviso", "Beneficiário é obrigatório!")
                return
            beneficiario_id = None
            for key, value in self.beneficiarios_map.items():
                if value == beneficiario_display:
                    beneficiario_id = key
                    break
            if not beneficiario_id:
                messagebox.showerror("Erro", "Beneficiário inválido!")
                return
            if beneficiario_id.startswith("FREELANCER_"):
                freelancer_id = int(beneficiario_id.replace("FREELANCER_", ""))
                freelancer = self.freelancers_manager.buscar_por_id(freelancer_id)
                if not freelancer or not freelancer.ativo:
                    messagebox.showerror("Erro", "Freelancer não encontrado ou inativo!")
                    return
            elif beneficiario_id.startswith("FORNECEDOR_"):
                fornecedor_id = int(beneficiario_id.replace("FORNECEDOR_", ""))
                fornecedor = self.fornecedores_manager.buscar_por_id(fornecedor_id)
                if not fornecedor:
                    messagebox.showerror("Erro", "Fornecedor não encontrado!")
                    return
            descricao = self.descricao_entry.get().strip()
            if not descricao:
                messagebox.showwarning("Aviso", "Descrição é obrigatória!")
                return
            percentagem_str = self.percentagem_entry.get().strip()
            if not percentagem_str:
                messagebox.showwarning("Aviso", "Percentagem é obrigatória!")
                return
            try:
                percentagem = Decimal(percentagem_str.replace(',', '.'))
            except ValueError:
                messagebox.showerror("Erro", "Percentagem inválida!")
                return
            if percentagem <= 0:
                messagebox.showwarning("Aviso", "Percentagem deve ser maior que 0!")
                return
            if percentagem > 100:
                messagebox.showwarning("Aviso", "Percentagem não pode ser maior que 100%!")
                return
            if self.item_id:
                sucesso, item, erro = self.manager.atualizar_reparticao(
                    reparticao_id=self.item_id,
                    tipo='comissao',
                    beneficiario=beneficiario_id,
                    descricao=descricao,
                    percentagem=percentagem,
                    base_calculo=self.base_calculo
                )
                if not sucesso:
                    messagebox.showerror("Erro", f"Erro ao gravar: {erro}")
            else:
                reparticao = OrcamentoReparticao(
                    orcamento_id=self.orcamento_id,
                    tipo='comissao',
                    beneficiario=beneficiario_id,
                    descricao=descricao,
                    percentagem=percentagem,
                    base_calculo=self.base_calculo,
                    total=Decimal('0')
                )
                reparticao.total = reparticao.calcular_total()
                self.db_session.add(reparticao)
                self.db_session.commit()
                sucesso = True
            if sucesso:
                self.success = True
                self.destroy()
        except Exception as e:
            self.db_session.rollback()
            messagebox.showerror("Erro", f"Erro inesperado: {str(e)}")

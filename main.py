"""
Agora Media - Sistema de Contabilidade
Ponto de entrada principal da aplicação
"""

import customtkinter as ctk
from dotenv import load_dotenv
import os

# Carregar variáveis de ambiente
load_dotenv()

def main():
    """Função principal da aplicação"""
    
    # Configurar tema do CustomTkinter
    ctk.set_appearance_mode("dark")  # "dark" ou "light"
    ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"
    
    # Criar janela principal
    app = ctk.CTk()
    app.title(os.getenv("APP_NAME", "Agora Media Contabilidade"))
    app.geometry("1200x800")
    
    # Label temporário
    label = ctk.CTkLabel(
        app, 
        text="🎬 Agora Media - Sistema de Contabilidade\n\nEm desenvolvimento...",
        font=("Arial", 24)
    )
    label.pack(pady=50)
    
    # Botão de teste
    button = ctk.CTkButton(
        app,
        text="Testar Conexão",
        command=lambda: print("Sistema funcionando!")
    )
    button.pack(pady=20)
    
    # Iniciar aplicação
    app.mainloop()

if __name__ == "__main__":
    main()

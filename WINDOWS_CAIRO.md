# 🪟 Instalação do Cairo no Windows (Opcional)

## ℹ️ Quando é Necessário?

O Cairo é necessário **apenas** se quiseres usar **logos SVG** na aplicação.

- ✅ **Sem Cairo**: Aplicação funciona normalmente com fallback de texto para logos
- ✅ **Ícones PNG (Base64)**: Funcionam sempre, sem necessidade de Cairo
- 🎨 **Com Cairo**: Logos SVG escaláveis de alta qualidade

## 🚀 Opção 1: Usar Fallback (Recomendado)

A forma mais simples é **não instalar Cairo** e deixar a aplicação usar o fallback automático:

- Login: Mostra "AGORA Media Production" em texto
- Sidebar: Mostra "AGORA" em texto
- Todos os ícones do menu funcionam normalmente (usam Base64)

**Nenhuma configuração necessária!** ✨

## 🛠️ Opção 2: Instalar Cairo (Avançado)

Se realmente precisas de logos SVG escaláveis, tens estas opções:

### Método 1: GTK+ para Windows

1. Download GTK+ All-in-One Bundle:
   - https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases

2. Instalar com todas as opções marcadas

3. Adicionar ao PATH do Windows:
   ```
   C:\Program Files\GTK3-Runtime Win64\bin
   ```

4. Reiniciar PowerShell e testar:
   ```powershell
   .\venv\Scripts\activate
   python -c "import cairosvg; print('✅ Cairo funciona!')"
   ```

### Método 2: MSYS2 (Para Desenvolvedores)

1. Instalar MSYS2: https://www.msys2.org/

2. No terminal MSYS2:
   ```bash
   pacman -S mingw-w64-x86_64-cairo
   ```

3. Adicionar ao PATH:
   ```
   C:\msys64\mingw64\bin
   ```

### Método 3: Conda (Se usas Anaconda)

```bash
conda install -c conda-forge cairo
```

## 🧪 Verificar Instalação

```powershell
# Ativar venv
.\venv\Scripts\activate

# Testar
python -c "from assets.resources import CAIROSVG_AVAILABLE; print('Cairo disponível:', CAIROSVG_AVAILABLE)"
```

## ❓ Troubleshooting

### Erro: "no library called cairo-2 was found"

**Causa**: Biblioteca Cairo DLL não encontrada

**Solução**:
1. Verificar se Cairo está instalado
2. Verificar se o PATH está correto
3. Reiniciar PowerShell após alterar PATH

### Aplicação não inicia

**Causa**: Pode ter havido erro ao carregar Cairo

**Solução**:
```powershell
# A aplicação deve funcionar automaticamente sem Cairo
# Os fallbacks de texto serão usados
.\run_windows.bat
```

## 💡 Recomendação

Para a maioria dos utilizadores, **não instalar Cairo** é a melhor opção:

- ✅ Mais simples e rápido
- ✅ Menos dependências
- ✅ Aplicação funciona igual (com texto em vez de logo SVG)
- ✅ Todos os ícones do menu funcionam (Base64)
- ✅ Menos problemas de compatibilidade

Se realmente precisas dos logos SVG escaláveis, experimenta a **Opção 1: GTK+** que é a mais fácil.

---

**Dúvidas?** A aplicação está configurada para funcionar perfeitamente sem Cairo! 🎉

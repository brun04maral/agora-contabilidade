# 📥 Instruções: Importar Dados do Excel

## 🎯 Processo em 3 Passos

---

## **PASSO 1: Gerar JSON com o Claude Chat**

### 1.1 - Vai ao Claude Chat
Abre uma nova conversa em **https://claude.ai**

### 1.2 - Envia esta prompt + o teu ficheiro Excel

Copia e cola esta prompt completa:

```
Olá! Preciso da tua ajuda para transformar este ficheiro Excel num formato que possa ser importado para uma aplicação de contabilidade.

CONTEXTO DA APLICAÇÃO:
Tenho uma app Python com os seguintes modelos de dados:

1. CLIENTES:
   - nome (obrigatório)
   - nif, morada, pais, contacto, email, angariacao, nota

2. FORNECEDORES:
   - nome (obrigatório)
   - estatuto: "EMPRESA", "FREELANCER" ou "ESTADO"
   - area, funcao, classificacao (1-5), nif, iban, morada, contacto, email
   - validade_seguro_trabalho (data)

3. PROJETOS:
   - tipo: "EMPRESA", "PESSOAL_BRUNO" ou "PESSOAL_RAFAEL"
   - cliente_nome (para fazer match)
   - descricao
   - valor_sem_iva
   - data_inicio, data_fim, data_faturacao, data_vencimento
   - premio_bruno, premio_rafael (para projetos EMPRESA)
   - estado: "NAO_FATURADO", "FATURADO" ou "RECEBIDO"
   - nota: Se tens "data_recebimento" no Excel, usa como data_faturacao para projetos RECEBIDOS

4. DESPESAS:
   - tipo: "FIXA_MENSAL", "PESSOAL_BRUNO", "PESSOAL_RAFAEL", "EQUIPAMENTO" ou "PROJETO"
   - data
   - credor_nome (para fazer match com fornecedor)
   - projeto_descricao (opcional, para fazer match)
   - descricao
   - valor_sem_iva, valor_com_iva
   - estado: "ATIVO", "VENCIDO" ou "PAGO"
   - data_pagamento (se estado=PAGO)

5. BOLETINS:
   - socio: "BRUNO" ou "RAFAEL"
   - data_emissao
   - valor
   - estado: "PENDENTE" ou "PAGO"
   - data_pagamento (se estado=PAGO)
   - descricao, nota

TAREFA:
1. Analisa este Excel e identifica:
   - Que sheets/separadores existem
   - Que dados existem em cada sheet
   - Como mapear os dados para os modelos acima

2. Gera um ficheiro JSON com esta estrutura:

{
  "clientes": [
    {
      "nome": "Nome do Cliente",
      "nif": "123456789",
      "morada": "Rua X, 123",
      "pais": "Portugal",
      "contacto": "+351 912345678",
      "email": "email@exemplo.pt",
      "angariacao": "Como foi angariado",
      "nota": "Notas adicionais"
    }
  ],
  "fornecedores": [
    {
      "nome": "Nome Fornecedor",
      "estatuto": "FREELANCER",
      "area": "Produção",
      "funcao": "Técnico de Som",
      "classificacao": 4,
      "nif": "123456789",
      "iban": "PT50...",
      "morada": "Rua Y, 456",
      "contacto": "+351 923456789",
      "email": "fornecedor@exemplo.pt",
      "validade_seguro_trabalho": "2025-12-31",
      "nota": "Notas"
    }
  ],
  "projetos": [
    {
      "tipo": "PESSOAL_BRUNO",
      "cliente_nome": "Nome do Cliente",
      "descricao": "Descrição do Projeto",
      "valor_sem_iva": 5000.00,
      "data_inicio": "2024-01-15",
      "data_fim": "2024-02-28",
      "data_faturacao": "2024-03-01",
      "data_vencimento": "2024-03-30",
      "premio_bruno": 0,
      "premio_rafael": 0,
      "estado": "RECEBIDO",
      "nota": "Notas"
    }
  ],
  "despesas": [
    {
      "tipo": "FIXA_MENSAL",
      "data": "2024-01-15",
      "credor_nome": "Nome Fornecedor",
      "projeto_descricao": null,
      "descricao": "Descrição da Despesa",
      "valor_sem_iva": 100.00,
      "valor_com_iva": 123.00,
      "estado": "PAGO",
      "data_pagamento": "2024-01-20",
      "nota": "Notas"
    }
  ],
  "boletins": [
    {
      "socio": "BRUNO",
      "data_emissao": "2024-01-15",
      "valor": 500.00,
      "estado": "PAGO",
      "data_pagamento": "2024-01-25",
      "descricao": "Ajuda de custo Janeiro",
      "nota": "Notas"
    }
  ],
  "mapeamento_explicacao": {
    "descricao": "Explica aqui como fizeste o mapeamento, que decisões tomaste, e se há alguma nuance ou dados que não conseguiste mapear perfeitamente"
  }
}

IMPORTANTE:
- Se um campo não existir no Excel, usa null
- Datas no formato YYYY-MM-DD
- Valores numéricos sem vírgulas (ex: 1500.00 não 1.500,00)
- Para "tipo" e "estado", usa EXATAMENTE os valores que listei acima
- Inclui TODOS os registos do Excel
- Na secção "mapeamento_explicacao", explica as nuances e decisões que tomaste

Por favor, gera este JSON completo. Obrigado!
```

### 1.3 - Anexa o teu ficheiro Excel
Arrasta o ficheiro Excel para o chat ou usa o botão de anexar.

### 1.4 - Aguarda o JSON
O Claude Chat vai analisar o Excel e gerar o JSON.

### 1.5 - Copia o JSON
Quando o Claude Chat devolver o JSON:
1. Copia TODO o JSON (desde o primeiro `{` até ao último `}`)
2. Cria um novo ficheiro chamado `dados_excel.json`
3. Cola o JSON nesse ficheiro
4. Guarda o ficheiro em: `~/Documents/github/agora-contabilidade/dados_excel.json`

---

## **PASSO 2: Executar o Script de Importação**

### 2.1 - Abrir Terminal
```bash
cd ~/Documents/github/agora-contabilidade
```

### 2.2 - Verificar que o JSON está lá
```bash
ls -la dados_excel.json
```

Deves ver algo como:
```
-rw-r--r--  1 bruno  staff  45678 Oct 27 12:00 dados_excel.json
```

### 2.3 - (OPCIONAL) Fazer Backup da Base de Dados
**IMPORTANTE**: Se já tens dados na base de dados, faz backup primeiro!

```bash
cp agora_media.db agora_media.db.backup
```

### 2.4 - Executar Importação
```bash
python3 import_excel.py
```

O script vai:
1. Ler o `dados_excel.json`
2. Mostrar o que vai importar
3. Pedir confirmação
4. Importar tudo
5. Mostrar resumo

### 2.5 - Confirmar a Importação
Quando o script perguntar:
```
Continuar? (sim/não):
```

Escreve `sim` e pressiona Enter.

---

## **PASSO 3: Verificar os Dados**

### 3.1 - Executar a Aplicação
```bash
python3 main.py
```

### 3.2 - Fazer Login
- Bruno: `bruno@agoramedia.pt` / `bruno123`
- Rafael: `rafael@agoramedia.pt` / `rafael123`

### 3.3 - Verificar os Módulos
Navega pelos menus e verifica:
- 👥 **Clientes** - Todos importados?
- 🏢 **Fornecedores** - Todos importados?
- 🎬 **Projetos** - Valores corretos?
- 💸 **Despesas** - Associações corretas?
- 📄 **Boletins** - Sócios corretos?
- 📊 **Dashboard** - Estatísticas fazem sentido?
- 💰 **Saldos Pessoais** - Valores batem certo?

---

## 🐛 Resolução de Problemas

### Erro: "Ficheiro 'dados_excel.json' não encontrado"

**Causa**: O ficheiro não está na pasta correta.

**Solução**:
```bash
# Verificar onde estás
pwd

# Deve mostrar: /Users/brunoamaral/Documents/github/agora-contabilidade

# Listar ficheiros
ls -la *.json
```

### Erro: "JSON inválido" ou "Erro ao ler JSON"

**Causa**: O JSON tem erros de sintaxe.

**Solução**:
1. Abre `dados_excel.json` num editor de texto
2. Verifica que:
   - Começa com `{` e acaba com `}`
   - Todas as strings estão entre aspas duplas `"`
   - Não há vírgulas a mais no final de listas
3. Ou pede ao Claude Chat para corrigir o JSON

### Erro durante a importação

**Causa**: Dados incompatíveis ou campos obrigatórios em falta.

**Solução**:
1. O script mostra erros específicos
2. Copia os erros
3. Pede ao Claude Chat para corrigir o JSON com base nos erros
4. Tenta novamente

### Dados importados incorretamente

**Causa**: Mapeamento errado do Claude Chat.

**Solução**:
1. Se poucos registos errados: Corrige manualmente na app
2. Se muitos erros:
   ```bash
   # Restaurar backup
   rm agora_media.db
   cp agora_media.db.backup agora_media.db

   # Ou limpar tudo e começar de novo
   rm agora_media.db
   python3 init_setup.py

   # Pedir ao Claude Chat para ajustar o JSON
   # Tentar importação novamente
   ```

---

## 💡 Dicas

### Importação Incremental
Se queres importar em várias fases:

1. **Primeira vez**: Importa só clientes e fornecedores
   - Edita o JSON e deixa só essas secções
   - Importa
   - Verifica

2. **Segunda vez**: Importa projetos
   - Cria novo JSON só com projetos
   - Importa

3. **Terceira vez**: Importa despesas e boletins

### Valores Calculados
Após importação, verifica o **Dashboard** e **Saldos Pessoais**:
- Os valores devem ser calculados automaticamente
- Se não baterem certo, pode ser:
  - Estados errados (RECEBIDO vs FATURADO)
  - Tipos errados (PESSOAL_BRUNO vs EMPRESA)
  - Datas em falta

### Teste Primeiro
Se não tens certeza do mapeamento:
1. Cria um JSON pequeno com 2-3 registos de teste
2. Importa
3. Verifica se está correto
4. Só depois importa tudo

---

## 📞 Preciso de Ajuda?

1. **Erros no JSON**: Mostra o erro ao Claude Chat e pede para corrigir
2. **Erros na importação**: Copia a mensagem de erro completa
3. **Dúvidas no mapeamento**: Descreve a estrutura do teu Excel

---

## ✅ Checklist Final

Após importação bem-sucedida:

- [ ] Todos os clientes importados?
- [ ] Todos os fornecedores importados?
- [ ] Projetos com valores corretos?
- [ ] Despesas associadas aos fornecedores certos?
- [ ] Boletins associados aos sócios corretos?
- [ ] Dashboard mostra estatísticas corretas?
- [ ] Saldos Pessoais batem certo com o Excel?
- [ ] Fiz backup do ficheiro `agora_media.db`?

Se tudo ✅, está pronto! 🎉

---

*Script criado com Claude Code • Importação segura de dados do Excel*

# 💾 Backup e Restore - Agora Contabilidade

Guia completo para configurar backups automáticos e restaurar dados.

---

## 🔧 Configuração Inicial (No Servidor)

### 1. Copiar script de backup

```bash
# No servidor
cd ~/zumine/amp/docker/app/agora_web

# Pull do repositório (se ainda não tens o script)
git pull origin claude/self-hosted-brainstorm-heo8m

# Tornar executável
chmod +x backup.sh

# Criar diretório de backups
mkdir -p ~/backups/agora_contabilidade
```

### 2. Testar backup manual

```bash
./backup.sh
```

Deves ver algo como:
```
==================================
🔄 Backup Agora Contabilidade
==================================
Data: Mon Dec 29 14:30:00 UTC 2025
Destino: /home/zumine/backups/agora_contabilidade/agora_db_20251229_143000.sql.gz

📦 A fazer backup da base de dados...
✅ Backup criado com sucesso: 45K
🔗 Link 'latest' atualizado
📊 Total de backups retidos: 1

==================================
✅ Backup concluído com sucesso!
==================================
```

---

## ⏰ Configurar Backup Automático (Cron)

### Editar crontab

```bash
crontab -e
```

### Adicionar linha para backup diário às 3h da manhã

```cron
# Backup Agora Contabilidade - Todos os dias às 3h
0 3 * * * /home/zumine/zumine/amp/docker/app/agora_web/backup.sh >> /home/zumine/backups/agora_contabilidade/backup.log 2>&1
```

**Explicação**:
- `0 3 * * *` = Às 3h da manhã, todos os dias
- `>> backup.log` = Guarda logs de cada execução
- `2>&1` = Inclui erros no log

### Verificar se o cron está ativo

```bash
# Ver cron jobs ativos
crontab -l

# Ver logs de backup
tail -f ~/backups/agora_contabilidade/backup.log
```

---

## 📂 Estrutura de Backups

```
~/backups/agora_contabilidade/
├── agora_db_20251229_030000.sql.gz   # Backup dia 29/12 às 3h
├── agora_db_20251230_030000.sql.gz   # Backup dia 30/12 às 3h
├── agora_db_20251231_030000.sql.gz   # Backup dia 31/12 às 3h
├── agora_db_latest.sql.gz → agora_db_20251231_030000.sql.gz  (link simbólico)
└── backup.log                         # Logs das execuções
```

**Retenção**: 30 dias (backups mais antigos são automaticamente eliminados)

---

## 🔄 Restaurar Backup

### 1. Ver backups disponíveis

```bash
ls -lh ~/backups/agora_contabilidade/
```

### 2. Restaurar o último backup

```bash
cd ~/zumine/amp/docker/app/agora_web

# ATENÇÃO: Isto VAI APAGAR todos os dados atuais!
# Backup atual primeiro (por segurança)
./backup.sh

# Parar os containers
docker compose -f docker-compose.cloudflare.yml down

# Restaurar base de dados
zcat ~/backups/agora_contabilidade/agora_db_latest.sql.gz | \
  docker compose -f docker-compose.cloudflare.yml exec -T db psql -U agora agora_production

# Reiniciar containers
docker compose -f docker-compose.cloudflare.yml up -d
```

### 3. Restaurar backup específico

```bash
# Substituir TIMESTAMP pela data desejada (ex: 20251225_030000)
zcat ~/backups/agora_contabilidade/agora_db_TIMESTAMP.sql.gz | \
  docker compose -f docker-compose.cloudflare.yml exec -T db psql -U agora agora_production
```

---

## 📊 Monitorização

### Ver tamanho dos backups

```bash
du -h ~/backups/agora_contabilidade/
```

### Ver logs de backup

```bash
# Últimas 20 linhas
tail -20 ~/backups/agora_contabilidade/backup.log

# Ver em tempo real
tail -f ~/backups/agora_contabilidade/backup.log
```

### Verificar integridade de um backup

```bash
# Testar se o backup pode ser descomprimido
zcat ~/backups/agora_contabilidade/agora_db_latest.sql.gz | head -20
```

---

## 🚨 Troubleshooting

### Backup não é criado

**Problema**: Script termina com erro ou backup está vazio.

**Solução**:
```bash
# Verificar se o container DB está a correr
docker ps | grep agora_db

# Ver logs do container
docker logs agora_db

# Testar pg_dump manualmente
docker compose -f docker-compose.cloudflare.yml exec db pg_dump -U agora agora_production | head
```

### Cron não executa

**Problema**: Backup manual funciona, mas cron não.

**Solução**:
```bash
# Verificar logs do sistema
grep CRON /var/log/syslog | tail -20

# Usar caminho absoluto no crontab
# ✅ Correto: /home/zumine/zumine/amp/docker/app/agora_web/backup.sh
# ❌ Errado: ~/zumine/amp/docker/app/agora_web/backup.sh
```

### Restauro falha

**Problema**: Erro ao restaurar backup.

**Solução**:
```bash
# Verificar se o backup está válido
zcat backup.sql.gz | grep -i "PostgreSQL database dump"

# Dropar e recriar a base antes de restaurar
docker compose -f docker-compose.cloudflare.yml exec db psql -U agora -c "DROP DATABASE agora_production;"
docker compose -f docker-compose.cloudflare.yml exec db psql -U agora -c "CREATE DATABASE agora_production;"
```

---

## ✅ Checklist de Segurança

- [ ] Backup manual testado e funcional
- [ ] Cron job configurado e ativo
- [ ] Primeiro backup automático criado com sucesso
- [ ] Logs de backup a funcionar
- [ ] Restauro testado pelo menos uma vez
- [ ] Backups antigos estão a ser limpos (verificar após 31 dias)

---

## 💡 Dicas Importantes

1. **Testa o restauro regularmente** - Backup sem teste de restauro é inútil!
2. **Mantém backups off-site** - Copia periodicamente para outro servidor/nuvem
3. **Monitoriza o espaço em disco** - Backups ocupam espaço
4. **Documenta qualquer alteração** - Se mudares passwords/configurações, atualiza
5. **Backup antes de updates** - Sempre que fizeres deploy de código novo

---

**Último update**: 2025-12-29

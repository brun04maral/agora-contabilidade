# Guia: Configuração da Tabela Socios

## Problema
A migração 0004 foi marcada como `--fake` porque incluía tabelas já existentes (Equipamento, Orcamento).
Isso impediu a criação da tabela `core_socio` que é nova e necessária.

## Solução: Criar a tabela manualmente

### Passo 1: Copiar arquivos para o servidor

```bash
# No servidor (instante)
cd ~/amp/docker/app/agora_web
git pull origin claude/self-hosted-brainstorm-heo8m
```

### Passo 2: Executar SQL para criar a tabela

```bash
docker compose -f docker-compose.cloudflare.yml exec -T db psql -U agora -d agora_contabilidade < create_socios_table.sql
```

OU usando o Django dbshell:

```bash
docker compose -f docker-compose.cloudflare.yml exec web python manage.py dbshell
```

Depois cole o conteúdo de `create_socios_table.sql`.

### Passo 3: Carregar fixtures dos sócios

```bash
docker compose -f docker-compose.cloudflare.yml exec web python manage.py loaddata socios.json
```

### Passo 4: Migrar dados antigos para FK

```bash
docker compose -f docker-compose.cloudflare.yml exec web python manage.py migrate_socios
```

### Passo 5: Verificar no admin

1. Acesse o admin Django
2. Verifique se os sócios BA e RR aparecem
3. Verifique se Projetos, Boletins e Orçamentos têm o campo "Sócio" preenchido

## Próximos Passos (Futuro)

Depois de confirmar que tudo funciona:
1. Remover campos deprecated: `owner`, `socio_codigo`
2. Criar nova migração para limpar os campos antigos
3. Atualizar código que ainda referencia os campos antigos

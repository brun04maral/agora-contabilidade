# 🚀 Guia de Deploy - Agora Contabilidade (Português)

## ⚠️ IMPORTANTE: Corre estes comandos NO TEU SERVIDOR Ubuntu!

Este guia é para totós! Basta copiar e colar cada comando 😊

---

## 📋 Pré-requisitos (verifica primeiro!)

### 1. Verifica se o Docker está instalado:
```bash
docker --version
docker-compose --version
```

Se não estiver, instala:
```bash
sudo apt update
sudo apt install docker.io docker-compose -y
sudo systemctl start docker
sudo systemctl enable docker
```

### 2. Verifica se o Traefik está a correr:
```bash
docker ps | grep traefik
```

### 3. Verifica se a network do Traefik existe:
```bash
docker network ls | grep traefik
```

Se não existir, cria:
```bash
docker network create traefik_proxy
```

---

## 🎯 DEPLOY EM 5 PASSOS SIMPLES

### **PASSO 1: Ir para o diretório de deploy**
```bash
cd ~/zumine/amp/docker/app
```

### **PASSO 2: Verificar se os ficheiros estão lá**
```bash
ls -la
```

Deves ver:
- ✅ `docker-compose.production.yml`
- ✅ `Dockerfile`
- ✅ `deploy.sh`
- ✅ `.env`
- ✅ `manage.py`
- ✅ pasta `config/`
- ✅ pasta `core/`

**Se faltarem ficheiros**, copia-os do repo:
```bash
cd /home/user/agora-contabilidade/agora_web
cp -r * ~/zumine/amp/docker/app/
cd ~/zumine/amp/docker/app
```

### **PASSO 3: Configurar o .env (SE AINDA NÃO EXISTIR)**

Se o ficheiro `.env` não existir, cria-o:

```bash
cat > .env << 'EOF'
# Django Settings
DEBUG=False
SECRET_KEY=f#&l*&fzdxbrdttr1rjfn279x-aey=86p%a0a3yxgjj4-@vp12
DJANGO_SETTINGS_MODULE=config.settings

# Domain
DOMAIN=app.agoramediaproduction.pt
ALLOWED_HOSTS=app.agoramediaproduction.pt,localhost,127.0.0.1

# Database
DB_NAME=agora_production
DB_USER=agora
DB_PASSWORD=Agora2025Prod!SecureDB

# Backup settings
BACKUP_ENABLED=true
BACKUP_RETENTION_DAYS=30
EOF
```

**OPCIONAL:** Se quiseres mudar a password da BD:
```bash
nano .env
# Muda a linha: DB_PASSWORD=Agora2025Prod!SecureDB
# Ctrl+X, Y, Enter para guardar
```

### **PASSO 4: Dar permissões ao script de deploy**
```bash
chmod +x deploy.sh
```

### **PASSO 5: EXECUTAR O DEPLOY! 🚀**

**OPÇÃO A - Script Automático (Recomendado para totós!):**
```bash
./deploy.sh
```

O script vai:
1. ✅ Parar containers antigos (se existirem)
2. ✅ Construir as imagens Docker
3. ✅ Iniciar a base de dados PostgreSQL
4. ✅ Correr as migrações Django
5. ✅ Recolher ficheiros estáticos
6. ✅ Pedir-te para criar um superuser (username + password)
7. ✅ Iniciar todos os serviços

**OPÇÃO B - Manual (se quiseres controlo total):**

```bash
# 1. Parar tudo (se estiver a correr)
docker-compose -f docker-compose.production.yml down

# 2. Construir imagens
docker-compose -f docker-compose.production.yml build --no-cache

# 3. Iniciar base de dados
docker-compose -f docker-compose.production.yml up -d db

# 4. Esperar 10 segundos
sleep 10

# 5. Correr migrações
docker-compose -f docker-compose.production.yml run --rm web python manage.py migrate

# 6. Recolher static files
docker-compose -f docker-compose.production.yml run --rm web python manage.py collectstatic --noinput

# 7. Criar superuser (interativo)
docker-compose -f docker-compose.production.yml run --rm web python manage.py createsuperuser

# 8. Iniciar tudo
docker-compose -f docker-compose.production.yml up -d

# 9. Ver logs
docker-compose -f docker-compose.production.yml logs -f
```

---

## 🎉 DEPLOY COMPLETO!

### Acede à aplicação:
- 🌐 **App:** https://app.agoramediaproduction.pt
- 🔧 **Admin:** https://app.agoramediaproduction.pt/admin/

**Login:** Usa o username e password que criaste no passo do superuser!

---

## 📊 Comandos Úteis Pós-Deploy

### Ver se está tudo a correr:
```bash
cd ~/zumine/amp/docker/app
docker-compose -f docker-compose.production.yml ps
```

### Ver logs em tempo real:
```bash
docker-compose -f docker-compose.production.yml logs -f web
```

### Ver apenas últimas 50 linhas:
```bash
docker-compose -f docker-compose.production.yml logs --tail=50 web
```

### Reiniciar a aplicação:
```bash
docker-compose -f docker-compose.production.yml restart web
```

### Parar tudo:
```bash
docker-compose -f docker-compose.production.yml down
```

### Iniciar de novo:
```bash
docker-compose -f docker-compose.production.yml up -d
```

---

## 🐛 Problemas? TROUBLESHOOTING!

### Problema: "Cannot connect to database"
```bash
# Verifica se a BD está a correr
docker-compose -f docker-compose.production.yml ps db

# Verifica logs da BD
docker-compose -f docker-compose.production.yml logs db

# Reinicia a BD
docker-compose -f docker-compose.production.yml restart db
```

### Problema: "502 Bad Gateway" no browser
```bash
# Verifica se o web está a correr
docker-compose -f docker-compose.production.yml ps web

# Verifica logs
docker-compose -f docker-compose.production.yml logs web

# Reinicia
docker-compose -f docker-compose.production.yml restart web
```

### Problema: CSS não carrega (página sem estilo)
```bash
# Recolhe static files de novo
docker-compose -f docker-compose.production.yml exec web python manage.py collectstatic --noinput --clear
```

### Problema: Certificado SSL não funciona
**Espera 2-5 minutos!** O Let's Encrypt demora um bocado.

Verifica logs do Traefik:
```bash
docker logs traefik
```

Se continuar com problemas após 10 minutos:
```bash
# Força renovação (se o Traefik permitir)
docker restart traefik
```

---

## 🔐 Segurança - Checklist

- [x] `DEBUG=False` no .env
- [x] `SECRET_KEY` foi gerada automaticamente
- [x] `DB_PASSWORD` é forte
- [x] HTTPS via Let's Encrypt (Traefik)
- [ ] **Cria um superuser com password FORTE!**

---

## 🔄 Atualizar a Aplicação (quando fizeres mudanças)

```bash
# 1. Vai buscar código novo do git
cd /home/user/agora-contabilidade
git pull origin claude/self-hosted-brainstorm-heo8m

# 2. Copia para deploy
cp -r agora_web/* ~/zumine/amp/docker/app/

# 3. Vai para deploy
cd ~/zumine/amp/docker/app

# 4. Rebuild e restart
docker-compose -f docker-compose.production.yml build web
docker-compose -f docker-compose.production.yml up -d web

# 5. Migra BD (se houver mudanças)
docker-compose -f docker-compose.production.yml exec web python manage.py migrate

# 6. Static files
docker-compose -f docker-compose.production.yml exec web python manage.py collectstatic --noinput
```

---

## 💾 Backup da Base de Dados

### Criar backup:
```bash
cd ~/zumine/amp/docker/app
docker-compose -f docker-compose.production.yml exec db pg_dump -U agora agora_production > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Restaurar backup:
```bash
docker-compose -f docker-compose.production.yml exec -T db psql -U agora agora_production < backup_20251229_103000.sql
```

---

## 🆘 AJUDA!

Se continuas com problemas:

1. **Verifica logs:** `docker-compose -f docker-compose.production.yml logs -f`
2. **Verifica se está tudo a correr:** `docker-compose -f docker-compose.production.yml ps`
3. **Reinicia tudo:** `docker-compose -f docker-compose.production.yml restart`
4. **Última hipótese - restart total:**
   ```bash
   docker-compose -f docker-compose.production.yml down
   docker-compose -f docker-compose.production.yml up -d
   ```

---

**Data:** 29 Dezembro 2025
**Deploy para:** ~/zumine/amp/docker/app
**Domínio:** app.agoramediaproduction.pt
**Certresolver:** httpchallenge (igual ao FreeScout!)

---

**BOA SORTE! 🚀 Qualquer coisa, grita!**

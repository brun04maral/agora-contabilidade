# 🚀 Deploy para Servidor Remoto (via SSH)

## 📍 Situação: Servidor Ubuntu está numa máquina REMOTA

---

## PASSO-A-PASSO PARA TOTÓS 🎯

### **PASSO 1: SSH para o teu servidor**

```bash
ssh teu-usuario@teu-servidor-ip

# Exemplo:
# ssh bruno@192.168.1.100
# ou
# ssh bruno@server.agoramediaproduction.pt
```

### **PASSO 2: Verifica se o repositório JÁ EXISTE no servidor**

```bash
ls -la /home/user/agora-contabilidade
```

**Se existir:** Vai para o PASSO 3A
**Se NÃO existir:** Vai para o PASSO 3B

---

### **PASSO 3A: Se o repo JÁ EXISTE (git pull)**

```bash
# Vai para o diretório do repo
cd /home/user/agora-contabilidade

# Pull das mudanças
git pull origin claude/self-hosted-brainstorm-heo8m

# Vai para PASSO 4
```

---

### **PASSO 3B: Se o repo NÃO EXISTE (git clone)**

```bash
# Clone do repositório
cd /home/user
git clone https://github.com/brun04maral/agora-contabilidade.git
cd agora-contabilidade

# Checkout para a branch certa
git checkout claude/self-hosted-brainstorm-heo8m

# Vai para PASSO 4
```

---

### **PASSO 4: Copia ficheiros para a pasta de deploy**

```bash
# Cria a pasta de deploy (se não existir)
mkdir -p ~/zumine/amp/docker/app

# Copia TUDO
cp -r /home/user/agora-contabilidade/agora_web/* ~/zumine/amp/docker/app/

# Verifica se copiou
ls -la ~/zumine/amp/docker/app/
```

Deves ver:
- ✅ `docker-compose.production.yml`
- ✅ `Dockerfile`
- ✅ `deploy.sh`
- ✅ `manage.py`
- ✅ pastas `config/` e `core/`

---

### **PASSO 5: Configura o ficheiro .env**

```bash
cd ~/zumine/amp/docker/app

# Cria o ficheiro .env
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

# Verifica se criou
cat .env
```

**OPCIONAL:** Muda a DB_PASSWORD se quiseres:
```bash
nano .env
# Altera a linha DB_PASSWORD=...
# Ctrl+X, Y, Enter para guardar
```

---

### **PASSO 6: Verifica pré-requisitos**

```bash
# Docker instalado?
docker --version

# Traefik a correr?
docker ps | grep traefik

# Network do Traefik existe?
docker network ls | grep traefik_proxy
```

**Se a network NÃO existir:**
```bash
docker network create traefik_proxy
```

---

### **PASSO 7: DEPLOY! 🚀**

```bash
cd ~/zumine/amp/docker/app

# Dá permissões ao script
chmod +x deploy.sh

# CORRE O DEPLOY!!!
./deploy.sh
```

O script vai:
1. ✅ Parar containers antigos
2. ✅ Build das imagens
3. ✅ Iniciar PostgreSQL
4. ✅ Correr migrações
5. ✅ Recolher static files
6. ✅ **Pedir-te para criar SUPERUSER** (escolhe username + password forte!)
7. ✅ Iniciar tudo

---

### **PASSO 8: Verifica se está a correr**

```bash
# Ver containers
docker-compose -f docker-compose.production.yml ps

# Ver logs
docker-compose -f docker-compose.production.yml logs -f web
```

**Ctrl+C** para sair dos logs

---

### **PASSO 9: Testa no browser! 🎉**

Abre o browser e vai a:
- 🌐 **https://app.agoramediaproduction.pt**
- 🔧 **https://app.agoramediaproduction.pt/admin/**

**Login:** Username e password que criaste no superuser!

---

## 🐛 PROBLEMAS COMUNS

### Erro: "Permission denied" ao correr deploy.sh
```bash
chmod +x deploy.sh
sudo ./deploy.sh
```

### Erro: "docker: command not found"
```bash
# Instala o Docker
sudo apt update
sudo apt install docker.io docker-compose -y
sudo systemctl start docker
sudo systemctl enable docker

# Adiciona teu user ao grupo docker (para não precisar de sudo)
sudo usermod -aG docker $USER
# LOGOUT e LOGIN de novo para aplicar!
```

### Erro: "network traefik_proxy not found"
```bash
docker network create traefik_proxy
```

### Erro: "Cannot connect to database"
```bash
# Verifica se PostgreSQL está a correr
docker-compose -f docker-compose.production.yml ps db

# Reinicia
docker-compose -f docker-compose.production.yml restart db

# Ver logs
docker-compose -f docker-compose.production.yml logs db
```

### Erro: 502 Bad Gateway no browser
```bash
# Espera 1-2 minutos (pode estar a fazer build ainda)

# Verifica logs
docker-compose -f docker-compose.production.yml logs web

# Reinicia
docker-compose -f docker-compose.production.yml restart web
```

### Certificado SSL não funciona
```bash
# Espera 2-5 minutos para Let's Encrypt provisionar

# Verifica logs do Traefik
docker logs traefik

# Se continuar com problemas, reinicia Traefik
docker restart traefik
```

---

## 🔄 UPDATES FUTUROS

Quando fizeres mudanças no código:

```bash
# 1. SSH para servidor
ssh teu-usuario@teu-servidor

# 2. Pull do código novo
cd /home/user/agora-contabilidade
git pull origin claude/self-hosted-brainstorm-heo8m

# 3. Copia para deploy
cp -r agora_web/* ~/zumine/amp/docker/app/

# 4. Rebuild e restart
cd ~/zumine/amp/docker/app
docker-compose -f docker-compose.production.yml build web
docker-compose -f docker-compose.production.yml up -d web

# 5. Migra BD (se houver mudanças nos models)
docker-compose -f docker-compose.production.yml exec web python manage.py migrate

# 6. Static files
docker-compose -f docker-compose.production.yml exec web python manage.py collectstatic --noinput
```

---

## 💾 BACKUP

```bash
# Criar backup da BD
cd ~/zumine/amp/docker/app
docker-compose -f docker-compose.production.yml exec db pg_dump -U agora agora_production > backup_$(date +%Y%m%d_%H%M%S).sql

# Restaurar
docker-compose -f docker-compose.production.yml exec -T db psql -U agora agora_production < backup_20251229_120000.sql
```

---

## ℹ️ INFO

- **Domain:** app.agoramediaproduction.pt
- **Deploy path:** ~/zumine/amp/docker/app
- **Database:** PostgreSQL 16
- **SSL:** Let's Encrypt via Traefik (httpchallenge)
- **Branch:** claude/self-hosted-brainstorm-heo8m

---

**Boa sorte! 🚀**

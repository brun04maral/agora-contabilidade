# Deployment Guide - Agora Contabilidade

## 🎯 Deployment Target

**Server Path:** `~/zumine/amp/docker/app`
**Domain:** `app.agoramediaproduction.pt`
**Environment:** Production (Local Server with Traefik)

---

## 📋 Prerequisites

1. **Docker & Docker Compose** installed on server
2. **Traefik** running with network `traefik_proxy`
3. **Domain DNS** pointing to your server IP (app.agoramediaproduction.pt)
4. **Ports available:** 5432 (PostgreSQL - internal only)

---

## 🚀 Quick Deployment

### Step 1: Copy files to server

```bash
# From your development machine
cd /home/user/agora-contabilidade/agora_web

# Copy to server deployment directory
mkdir -p ~/zumine/amp/docker/app
cp -r . ~/zumine/amp/docker/app/
cd ~/zumine/amp/docker/app
```

### Step 2: Configure environment

```bash
# Copy and edit production environment file
cp .env.production .env

# IMPORTANT: Edit these values!
nano .env
```

**Required changes in `.env`:**

```bash
# Generate a strong secret key (run this command):
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

# Update these values:
SECRET_KEY=<paste_generated_key_here>
DB_PASSWORD=<choose_strong_password>
```

### Step 3: Use deployment script

```bash
# Run automated deployment
./deploy.sh
```

The script will:
1. ✅ Create deployment directory structure
2. ✅ Build Docker images
3. ✅ Start PostgreSQL database
4. ✅ Run Django migrations
5. ✅ Collect static files
6. ✅ Create superuser (interactive)
7. ✅ Start all services

---

## 🔧 Manual Deployment (Alternative)

If you prefer manual control:

```bash
cd ~/zumine/amp/docker/app

# 1. Build images
docker-compose -f docker-compose.production.yml build

# 2. Start database
docker-compose -f docker-compose.production.yml up -d db

# 3. Wait for database to be ready (10-15 seconds)
sleep 10

# 4. Run migrations
docker-compose -f docker-compose.production.yml run --rm web python manage.py migrate

# 5. Collect static files
docker-compose -f docker-compose.production.yml run --rm web python manage.py collectstatic --noinput

# 6. Create superuser
docker-compose -f docker-compose.production.yml run --rm web python manage.py createsuperuser

# 7. Start all services
docker-compose -f docker-compose.production.yml up -d
```

---

## 🌐 Accessing the Application

After deployment:

- **Main App:** https://app.agoramediaproduction.pt
- **Admin Panel:** https://app.agoramediaproduction.pt/admin/
- **Login:** Use the superuser credentials you created

---

## 📊 Monitoring & Logs

### View logs
```bash
cd ~/zumine/amp/docker/app

# All logs
docker-compose -f docker-compose.production.yml logs -f

# Web logs only
docker-compose -f docker-compose.production.yml logs -f web

# Database logs only
docker-compose -f docker-compose.production.yml logs -f db

# Last 100 lines
docker-compose -f docker-compose.production.yml logs --tail=100 web
```

### Check container status
```bash
docker-compose -f docker-compose.production.yml ps
```

### Check health
```bash
docker-compose -f docker-compose.production.yml exec web python manage.py check
```

---

## 🔄 Common Operations

### Restart services
```bash
cd ~/zumine/amp/docker/app
docker-compose -f docker-compose.production.yml restart
```

### Stop services
```bash
docker-compose -f docker-compose.production.yml down
```

### Update application
```bash
# Pull latest code
cd /home/user/agora-contabilidade
git pull origin claude/self-hosted-brainstorm-heo8m

# Copy to deployment directory
cp -r agora_web/* ~/zumine/amp/docker/app/

# Rebuild and restart
cd ~/zumine/amp/docker/app
docker-compose -f docker-compose.production.yml build web
docker-compose -f docker-compose.production.yml up -d web

# Run migrations if needed
docker-compose -f docker-compose.production.yml exec web python manage.py migrate
```

### Backup database
```bash
cd ~/zumine/amp/docker/app

# Create backup
docker-compose -f docker-compose.production.yml exec db pg_dump -U agora agora_production > backup_$(date +%Y%m%d_%H%M%S).sql

# Or using docker
docker exec agora_db pg_dump -U agora agora_production > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Restore database
```bash
cd ~/zumine/amp/docker/app

# Restore from backup
docker-compose -f docker-compose.production.yml exec -T db psql -U agora agora_production < backup_20241229_120000.sql
```

---

## 🐛 Troubleshooting

### Issue: Containers won't start
```bash
# Check logs for errors
docker-compose -f docker-compose.production.yml logs

# Check if Traefik network exists
docker network ls | grep traefik_proxy

# If not, create it:
docker network create traefik_proxy
```

### Issue: Database connection errors
```bash
# Check database is healthy
docker-compose -f docker-compose.production.yml exec db pg_isready -U agora

# Check database logs
docker-compose -f docker-compose.production.yml logs db

# Restart database
docker-compose -f docker-compose.production.yml restart db
```

### Issue: 502 Bad Gateway
```bash
# Check if web container is running
docker-compose -f docker-compose.production.yml ps web

# Check web container logs
docker-compose -f docker-compose.production.yml logs web

# Check if port 8000 is listening inside container
docker-compose -f docker-compose.production.yml exec web netstat -tulpn | grep 8000
```

### Issue: Static files not loading
```bash
# Recollect static files
docker-compose -f docker-compose.production.yml exec web python manage.py collectstatic --noinput --clear

# Check volume permissions
docker-compose -f docker-compose.production.yml exec web ls -la /app/static
```

### Issue: Permission denied
```bash
# Fix ownership
docker-compose -f docker-compose.production.yml exec web chown -R agora:agora /app/static /app/media
```

---

## 🔐 Security Checklist

- [ ] Changed `SECRET_KEY` in `.env`
- [ ] Changed `DB_PASSWORD` in `.env`
- [ ] Set `DEBUG=False` in `.env`
- [ ] Created strong superuser password
- [ ] Domain DNS configured correctly
- [ ] SSL certificate provisioned by Traefik/Let's Encrypt
- [ ] Regular database backups configured
- [ ] Server firewall configured (only 80, 443, 22 open)

---

## 📚 Next Steps

After successful deployment:

1. **Login to admin panel** and verify everything works
2. **Migrate data** from desktop app (use data migration script - to be created)
3. **Test all features** (Projetos, Despesas, Boletins, Saldos)
4. **Configure automatic backups** (cron job for database dumps)
5. **Monitor logs** for the first few days
6. **Train users** on new web interface

---

## 🆘 Support

If you encounter issues:

1. Check logs: `docker-compose -f docker-compose.production.yml logs -f`
2. Verify environment variables in `.env`
3. Ensure Traefik is running and configured correctly
4. Check domain DNS resolution: `nslookup app.agoramediaproduction.pt`
5. Test direct container access: `docker-compose -f docker-compose.production.yml exec web curl http://localhost:8000/admin/`

---

**Deployment Date:** 2025-12-29
**Django Version:** 5.0
**Python Version:** 3.11
**Database:** PostgreSQL 16

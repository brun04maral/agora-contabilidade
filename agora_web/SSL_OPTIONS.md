# 🔐 SSL/TLS Options - Cloudflare vs Traefik

## 📊 Comparação Rápida

| Feature | Cloudflare Proxied | Traefik Let's Encrypt |
|---------|-------------------|----------------------|
| **SSL Management** | Cloudflare automático | Traefik Let's Encrypt |
| **DDoS Protection** | ✅ Sim | ❌ Não |
| **CDN/Caching** | ✅ Sim | ❌ Não |
| **IP Oculto** | ✅ Sim | ❌ Não (exposto) |
| **Complexidade** | 🟢 Simples | 🟡 Moderada |
| **Controlo Total** | 🟡 Moderado | ✅ Total |
| **Privacidade** | 🟡 CF vê tráfego | ✅ End-to-end |
| **Custo** | 🟢 Grátis | 🟢 Grátis |

---

## 🎯 OPÇÃO 1: Cloudflare Proxied (RECOMENDADO)

### ✅ Use quando:
- Queres **simplicidade máxima**
- Queres **proteção DDoS**
- Queres **CDN grátis** (site mais rápido)
- Não te importas que Cloudflare veja o tráfego
- **Aplicações web normais** (como esta!)

### 📝 Configuração:

#### 1. DNS Cloudflare:
```
Type:    A
Name:    app
Content: 172.66.0.70
Proxy:   🟠 Proxied (LARANJA)
TTL:     Auto
```

#### 2. SSL/TLS Cloudflare:
```
SSL/TLS → Overview → Encryption mode: Flexible
```

**Flexible** = Cloudflare (HTTPS) → Servidor (HTTP)
- Mais simples
- Cloudflare lida com tudo
- Servidor não precisa de certificado

**OU Full** = Cloudflare (HTTPS) → Servidor (HTTPS self-signed)
- Mais seguro
- Traefik ainda pode gerar cert, mas não precisa ser Let's Encrypt válido

#### 3. Docker Compose:
Usa: `docker-compose.cloudflare.yml`

```bash
# No servidor
cd ~/zumine/amp/docker/app/agora_web
docker compose -f docker-compose.cloudflare.yml up -d
```

**Diferença:**
- ❌ Sem `tls=true`
- ❌ Sem `certresolver`
- ✅ Só usa `entrypoints=web` (HTTP)
- ✅ Cloudflare adiciona HTTPS por cima

---

## 🔓 OPÇÃO 2: DNS Only + Traefik Let's Encrypt

### ✅ Use quando:
- Queres **end-to-end encryption** sem intermediários
- Não confias no Cloudflare (privacidade máxima)
- Não precisas de DDoS protection
- Queres **controlo total**
- **Aplicações sensíveis** (mail, VPN, etc.)

### 📝 Configuração:

#### 1. DNS Cloudflare:
```
Type:    A
Name:    app
Content: 172.66.0.70
Proxy:   🔘 DNS only (CINZENTO)
TTL:     Auto
```

#### 2. Docker Compose:
Usa: `docker-compose.production.yml` (atual)

```bash
cd ~/zumine/amp/docker/app/agora_web
docker compose -f docker-compose.production.yml up -d
```

**Características:**
- ✅ `tls=true`
- ✅ `certresolver=httpchallenge`
- ✅ Traefik pede certificado ao Let's Encrypt
- ✅ Renovação automática cada 90 dias

---

## 🤔 Qual escolher?

### Para a **Agora Contabilidade** (app Django):

**RECOMENDO: Cloudflare Proxied** 🟠

**Porquê?**
1. ✅ **Mais simples** - Cloudflare lida com SSL
2. ✅ **Mais rápido** - CDN do Cloudflare
3. ✅ **Mais seguro** - DDoS protection
4. ✅ **Zero configuração SSL** no servidor
5. ✅ É uma app web normal (não sensível como email)

---

### Para o **FreeScout** (mail):

**Recomendo: DNS Only** 🔘

**Porquê?**
1. ✅ **Email precisa de IP direto** (SPF, DKIM)
2. ✅ **SMTP não funciona bem** com proxy Cloudflare
3. ✅ End-to-end encryption para email
4. ✅ Menos problemas com deliverability

---

## 🚀 Setup Recomendado FINAL:

```
FreeScout (mail):     🔘 DNS only  + Traefik Let's Encrypt
Agora App (app):      🟠 Proxied   + Cloudflare SSL
```

**Melhor dos dois mundos!** 🎉

---

## 📋 Passos para Cloudflare Proxied:

```bash
# 1. Cloudflare DNS
# - Add record: A → app → 172.66.0.70
# - Proxy: 🟠 Proxied

# 2. Cloudflare SSL/TLS
# - Encryption mode: Flexible (ou Full se quiseres)

# 3. No servidor
ssh teu-usuario@servidor
cd ~/zumine/amp/docker/app/agora_web

# 4. Usa o docker-compose simplificado
docker compose -f docker-compose.cloudflare.yml down
docker compose -f docker-compose.cloudflare.yml build
docker compose -f docker-compose.cloudflare.yml up -d

# 5. Testa
curl -I https://app.agoramediaproduction.pt
```

---

## ⚠️ Importante:

Se mudares de DNS only → Proxied:
1. **Espera 5 minutos** para DNS propagar
2. **Para containers** existentes
3. **Usa docker-compose.cloudflare.yml** (sem TLS)
4. **Testa** https://app.agoramediaproduction.pt

Se mudares de Proxied → DNS only:
1. **Para containers** existentes
2. **Usa docker-compose.production.yml** (com TLS)
3. **Espera** Let's Encrypt provisionar cert (2-5 min)
4. **Testa** https://app.agoramediaproduction.pt

---

**Data:** 2025-12-29
**Recomendação:** Cloudflare Proxied para apps web, DNS only para mail/SMTP

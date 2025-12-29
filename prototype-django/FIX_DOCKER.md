# 🔧 Fix Docker - Troubleshooting

## Problema: "service web is not running"

### Solução 1: Ver Logs do Docker

```bash
# Ver o que aconteceu quando tentou iniciar
docker compose up --build

# Deixa correr e vê os logs
# Se der erro, copia e cola o erro aqui
```

### Solução 2: Verificar Docker Está a Correr

```bash
# Ver se Docker daemon está up
docker ps

# Se der erro "cannot connect to daemon":
# 1. Abre Docker Desktop (Spotlight → "Docker")
# 2. Espera ícone Docker ficar verde
# 3. Tenta novamente: docker compose up --build
```

### Solução 3: Limpar e Recomeçar

```bash
# Parar tudo
docker compose down

# Limpar volumes antigos
docker compose down -v

# Rebuild do zero
docker compose up --build --force-recreate
```

### Solução 4: Remover Warnings

O warning sobre `version` é inofensivo, mas podes removê-lo:

```yaml
# docker-compose.yml - apaga a primeira linha:
# version: '3.8'  ← APAGA ISTO

services:
  db:
    ...
```

### Debug: Ver Logs de Container Específico

```bash
# Ver logs da base de dados
docker compose logs db

# Ver logs do web (Django)
docker compose logs web

# Follow logs em tempo real
docker compose logs -f web
```

### Comandos Úteis

```bash
# Ver containers a correr
docker compose ps

# Entrar dentro do container
docker compose exec web bash

# Parar tudo
docker compose down

# Rebuild completo
docker compose build --no-cache
docker compose up
```

### Se Continuar a Falhar

Envia-me o output completo de:

```bash
docker compose up --build
```

E ajudo a debugar!

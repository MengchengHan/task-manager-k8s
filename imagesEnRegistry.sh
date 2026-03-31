#!/bin/bash
set -e

echo "==> Levantando registry local..."
if docker ps -a --format '{{.Names}}' | grep -q "^registry$"; then
  docker start registry 2>/dev/null || true
  echo "    El registry ya existía, arrancado."
else
  docker run -d --name registry --restart=always -p 5000:5000 registry:2
  echo "    Registry creado."
fi

echo "==> Construyendo imágenes..."
docker build -t localhost:5000/task-api:1.0   ./api
docker build -t localhost:5000/task-nginx:1.0 ./nginx

echo "==> Subiendo imágenes al registry..."
docker push localhost:5000/task-api:1.0
docker push localhost:5000/task-nginx:1.0

echo ""
echo "✅ Imágenes disponibles en el registry local."

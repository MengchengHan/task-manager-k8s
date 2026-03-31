#!/bin/bash
set -e

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║     task-manager — arranque en K8s       ║"
echo "╚══════════════════════════════════════════╝"

# ── 1. Imágenes en el registry ──────────────────────────────────
echo ""
echo "▶ [1/4] Construyendo y pusheando imágenes..."
bash imagesEnRegistry.sh

# ── 2. Clúster Kubernetes ───────────────────────────────────────
echo ""
echo "▶ [2/4] Creando clúster kind..."
bash createCluster.sh

# ── 3. Secret y manifiestos ─────────────────────────────────────
echo ""
echo "▶ [3/4] Aplicando secret y manifiestos K8s..."

# Secret con la contraseña de PostgreSQL
# NOTA: en producción usar openssl rand -base64 32 y un gestor de secretos externo
kubectl create secret generic db-secret \
  --from-literal=db-password='taskpass' \
  --dry-run=client -o yaml | kubectl apply -f -

kubectl apply -f k8s/

# ── 4. Esperar pods ─────────────────────────────────────────────
echo ""
echo "▶ [4/4] Esperando a que los pods estén listos..."
kubectl wait --for=condition=ready pod --all --timeout=180s

echo ""
kubectl get pods,svc,hpa

echo ""
echo "✅ ¡Todo listo! Abriendo en http://localhost:8080"
echo "   (Ctrl+C para detener el port-forward)"
echo ""
kubectl port-forward service/nginx 8080:80

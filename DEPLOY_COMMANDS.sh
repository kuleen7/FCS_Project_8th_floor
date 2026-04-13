#!/usr/bin/env bash
set -euo pipefail

echo "==> Frontend production build"
npm --prefix frontend run build

echo "==> Backend syntax sanity check"
python3 -m py_compile backend/app/main.py backend/app/api/auth.py backend/app/api/applications.py

cat <<'EOF'

Next steps require your cloud account login:

1) Deploy backend on Render:
   - Use render.yaml from repo root
   - Set required env vars from backend/.env.production.example

2) Deploy frontend on Vercel:
   - Root directory: frontend
   - Set env var:
     REACT_APP_API_BASE_URL=https://<your-backend-domain>/api

EOF

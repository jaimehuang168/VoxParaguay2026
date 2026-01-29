#!/bin/bash

# VoxParaguay 2026 - Setup Script
# Configura el entorno de desarrollo

set -e

echo "🇵🇾 VoxParaguay 2026 - Configuración del Entorno"
echo "================================================"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo -e "\n${YELLOW}Verificando prerequisitos...${NC}"

command -v python3 >/dev/null 2>&1 || { echo "Python 3 es requerido"; exit 1; }
command -v node >/dev/null 2>&1 || { echo "Node.js es requerido"; exit 1; }
command -v npm >/dev/null 2>&1 || { echo "npm es requerido"; exit 1; }

echo -e "${GREEN}✓ Prerequisitos verificados${NC}"

# Backend setup
echo -e "\n${YELLOW}Configurando Backend...${NC}"
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Generate encryption key
echo -e "\n${YELLOW}Generando clave de encriptación (Ley 7593/2025)...${NC}"
ENCRYPTION_KEY=$(python3 -c "from app.utils.encryption import generate_encryption_key; print(generate_encryption_key())")

# Create .env if not exists
if [ ! -f .env ]; then
    cp .env.example .env
    # Set encryption key
    sed -i '' "s/ENCRYPTION_KEY=/ENCRYPTION_KEY=$ENCRYPTION_KEY/" .env
    echo -e "${GREEN}✓ Archivo .env creado con clave de encriptación${NC}"
else
    echo -e "${YELLOW}⚠ Archivo .env ya existe, no se modificó${NC}"
fi

# Generate Prisma client
echo -e "\n${YELLOW}Generando cliente Prisma...${NC}"
prisma generate

cd ..

# Frontend setup
echo -e "\n${YELLOW}Configurando Frontend...${NC}"
cd frontend

# Install dependencies
npm install

# Create .env.local if not exists
if [ ! -f .env.local ]; then
    cat > .env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
NEXT_PUBLIC_MAPBOX_TOKEN=
EOF
    echo -e "${GREEN}✓ Archivo .env.local creado${NC}"
fi

cd ..

echo -e "\n${GREEN}================================================${NC}"
echo -e "${GREEN}✓ Configuración completada${NC}"
echo -e "\n${YELLOW}Próximos pasos:${NC}"
echo "1. Configurar PostgreSQL y Redis (o usar docker-compose)"
echo "2. Configurar las variables de entorno en backend/.env"
echo "3. Ejecutar migraciones: cd backend && prisma migrate dev"
echo "4. Iniciar backend: cd backend && uvicorn app.main:app --reload"
echo "5. Iniciar frontend: cd frontend && npm run dev"
echo ""
echo "O usar Docker:"
echo "  docker-compose up -d"
echo ""

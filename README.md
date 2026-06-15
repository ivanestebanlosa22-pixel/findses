# VideoAgent AI

Sistema automático de generación de videos mediante IA. Convierte cualquier tema en un video completo con guion, imágenes, narración, subtítulos y música de fondo.

## Arquitectura

```
┌─────────────────┐     ┌─────────────────────────────────────────────┐
│   Frontend      │     │              Backend (FastAPI)              │
│  React +        │────►│                                             │
│  Tailwind CSS   │     │  Pipeline Orchestrator                      │
│                 │     │  ├─ Research Agent                          │
│                 │     │  ├─ Script Agent                            │
│                 │     │  ├─ Scene Agent                             │
│                 │     │  ├─ Prompt Agent                            │
│                 │     │  ├─ Image Agent                             │
│                 │     │  ├─ Voice Agent                             │
│                 │     │  ├─ Subtitle Agent                          │
│                 │     │  ├─ Video Editor Agent                      │
│                 │     │  └─ Quality Agent                           │
│                 │     │                                             │
│                 │     │  Database ───── SQLite/PostgreSQL           │
│                 │     │  Cache   ───── Redis                        │
│                 │     │  Storage ───── File System                  │
└─────────────────┘     └─────────────────────────────────────────────┘
```

## Stack Tecnológico

- **Backend**: Python 3.12, FastAPI, SQLAlchemy, Celery
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS
- **IA**: OpenAI GPT-4o, DALL-E 3, Stable Diffusion, ElevenLabs, Edge-TTS
- **Video**: FFmpeg, MoviePy
- **Infra**: Docker, PostgreSQL, Redis

## Estructura del Proyecto

```
video-agent-ai/
├── backend/
│   ├── api/               # Endpoints REST + WebSockets
│   ├── agents/            # Agentes IA (Research, Script, Scene, etc.)
│   ├── core/              # Configuración, seguridad, excepciones
│   ├── database/          # ORM, sesiones, CRUD
│   ├── models/            # Modelos SQLAlchemy
│   ├── prompts/           # Prompts del sistema para OpenAI
│   ├── utils/             # Utilidades (OpenAI, storage)
│   ├── workers/           # Tareas Celery
│   └── main.py            # Punto de entrada FastAPI
├── frontend/
│   ├── src/
│   │   ├── components/    # Componentes React reutilizables
│   │   ├── pages/         # Páginas (Dashboard, CreateProject, etc.)
│   │   └── services/      # API client + WebSocket
│   └── ...
├── storage/               # Almacenamiento de archivos generados
├── docker/                # Configuración Docker/Nginx
├── tests/                 # Tests automatizados
└── docker-compose.yml     # Orquestación de servicios
```

## Instalación y Ejecución

### Requisitos

- Python 3.12+
- Node.js 20+
- FFmpeg
- Docker (opcional)

### Desarrollo Local

```bash
# Backend
cd backend
pip install -r ../requirements.txt
cp ../.env.example .env
# Editar .env con tus API keys
uvicorn backend.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

### Docker (Producción)

```bash
docker-compose up -d
```

## Variables de Entorno

| Variable | Descripción | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | API Key de OpenAI | - |
| `ELEVENLABS_API_KEY` | API Key de ElevenLabs | - |
| `REPLICATE_API_KEY` | API Key de Replicate | - |
| `DATABASE_URL` | URL de base de datos | `sqlite+aiosqlite:///./storage/videoagent.db` |
| `REDIS_URL` | URL de Redis | `redis://localhost:6379/0` |

## API Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/v1/health` | Health check |
| GET | `/api/v1/projects` | Listar proyectos |
| POST | `/api/v1/projects` | Crear proyecto |
| GET | `/api/v1/projects/{id}` | Obtener proyecto |
| PUT | `/api/v1/projects/{id}` | Actualizar proyecto |
| DELETE | `/api/v1/projects/{id}` | Eliminar proyecto |
| POST | `/api/v1/projects/{id}/generate` | Iniciar generación |
| POST | `/api/v1/projects/{id}/cancel` | Cancelar proyecto |
| GET | `/api/v1/projects/{id}/scenes` | Obtener escenas |
| GET | `/api/v1/projects/{id}/logs` | Obtener logs |
| WS | `/api/v1/projects/{id}/ws` | WebSocket en tiempo real |

## Pipeline de Agentes

1. **Research Agent**: Investiga el tema usando IA
2. **Script Agent**: Genera guion optimizado para redes sociales
3. **Scene Agent**: Divide el guion en escenas
4. **Prompt Agent**: Genera prompts visuales para cada escena
5. **Image Agent**: Genera imágenes con DALL-E o Stable Diffusion
6. **Voice Agent**: Genera narración con Edge-TTS o ElevenLabs
7. **Subtitle Agent**: Crea subtítulos sincronizados
8. **Video Editor Agent**: Monta el video final con MoviePy
9. **Quality Agent**: Verifica calidad y corrige errores

## Licencia

MIT

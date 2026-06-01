# Backend Structure

This FastAPI backend is intentionally layered so the Demo can grow into a commercial product without moving core responsibilities later.

## Layers

- `app/api/routes/`: HTTP route declarations and request/response wiring.
- `app/models/`: SQLAlchemy database models.
- `app/schemas/`: Pydantic request and response schemas.
- `app/repositories/`: Database access and persistence concerns.
- `app/services/`: Business workflow orchestration.
- `app/ai/`: OpenAI-compatible client abstractions and prompt loading.
- `app/core/`: Configuration, database setup, and security extension points.
- `migrations/`: Future database migration files.

Routes should stay thin. Business workflows belong in services, database queries belong in repositories, and prompts must stay in the root `prompts/` directory.


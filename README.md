# AI Research Assistant

A multi-agent research assistant built using:

- LangGraph
- FastAPI
- Python

## Current Features

- Research Planning
- Research Analysis
- Report Generation
- REST API
- Swagger Documentation

## Roadmap

- [ ] Search Agent
- [ ] Fact Checker
- [ ] Reviewer Agent
- [ ] Report Storage
- [ ] PDF Export
- [ ] React FrontendYou are a Senior Full-Stack Architect.

Upgrade my AI Research Assistant with authentication and user ownership.

Current Stack:
- React
- TypeScript
- FastAPI
- SQLite
- SQLAlchemy
- LangGraph
- PDF Export
- Citations

Requirements:

Backend:

1. Create User model:
   - id
   - email
   - password_hash
   - created_at

2. Create authentication routes:
   POST /auth/register
   POST /auth/login
   GET /auth/me

3. Use JWT authentication.

4. Protect:
   GET /reports
   GET /reports/{id}
   DELETE /reports/{id}
   GET /reports/{id}/pdf

5. Associate reports with users.

Frontend:

1. Login page
2. Register page
3. Protected routes
4. Auth context
5. Logout button
6. Store JWT securely

Generate complete code.
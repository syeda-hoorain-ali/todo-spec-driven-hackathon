---
id: "0005"
title: "Create auth system implementation plan"
stage: "plan"
date: "2025-12-09"
surface: "agent"
model: "claude-opus-4-5-20251101"
feature: "phase-02/001-auth-system"
branch: "001-auth-system"
user: "user"
command: "/sp.plan"
labels: ["authentication", "implementation-plan", "jwt", "better-auth", "fastapi"]
links:
  spec: "specs/phase-02/001-auth-system/spec.md"
  ticket: null
  adr: null
  pr: null
files:
  - specs/phase-02/001-auth-system/plan.md
  - specs/phase-02/001-auth-system/research.md
  - specs/phase-02/001-auth-system/data-model.md
  - specs/phase-02/001-auth-system/quickstart.md
  - specs/phase-02/001-auth-system/contracts/auth-api.yaml
tests:
  - none
---

## Prompt

plan this feature with technical context, project structure with Next.js App Router, data models, API contracts, and quickstart guide. Include

More details

# **Securing the REST API**

*Better Auth + FastAPI Integration*

# **The Challenge**

Better Auth is a JavaScript/TypeScript authentication library that runs on your **Next.js frontend**. However, your **FastAPI backend** is a separate Python service that needs to verify which user is making API requests.

# **The Solution: JWT Tokens**

Better Auth can be configured to issue **JWT (JSON Web Token)** tokens when users log in. These tokens are self-contained credentials that include user information and can be verified by any service that knows the secret key.

# **How It Works**

* User logs in on Frontend → Better Auth creates a session and issues a JWT token
* Frontend makes API call → Includes the JWT token in the Authorization: Bearer <token> header
* Backend receives request → Extracts token from header, verifies signature using shared secret
* Backend identifies user → Decodes token to get user ID, email, etc. and matches it with the user ID in the URL
* Backend filters data → Returns only tasks belonging to that user

# **What Needs to Change**

| Component | Changes Required |
| :---- | :---- |
| **Better Auth Config** | Enable JWT plugin to issue tokens |
| **Frontend API Client** | Attach JWT token to every API request header |
| **FastAPI Backend** | Add middleware to verify JWT and extract user |
| **API Routes** | Filter all queries by the authenticated user's ID |

# **The Shared Secret**

Both frontend (Better Auth) and backend (FastAPI) must use the **same secret key** for JWT signing and verification. This is typically set via environment variable **BETTER_AUTH_SECRET** in both services.

# **Security Benefits**

| Benefit | Description |
| :---- | :---- |
| **User Isolation** | Each user only sees their own tasks |
| **Stateless Auth** | Backend doesn't need to call frontend to verify users |
| **Token Expiry** | JWTs expire automatically (e.g., after 7 days) |
| **No Shared DB Session** | Frontend and backend can verify auth independently |

# **API Behavior Change**

**After Auth:**

| All endpoints require valid JWT token |
| :---- |
| Requests without token receive 401 Unauthorized |
| Each user only sees/modifies their own tasks |
| Task ownership is enforced on every operation |

# **Bottom Line**

The REST API endpoints stay the same (**GET /api/user_id/tasks**, **POST /api/user_id/tasks**, etc.), but every request now must include a JWT token, and all responses are filtered to only include that user's data.

## Response snapshot

Created a complete implementation plan for the authentication system with Better Auth + FastAPI integration, including technical context, project structure with Next.js App Router, data models, API contracts, and quickstart guide.

## Outcome

- ✅ Impact: Complete implementation plan created with all required artifacts
- 🧪 Tests: none
- 📁 Files: plan.md, research.md, data-model.md, quickstart.md, contracts/auth-api.yaml
- 🔁 Next prompts: /sp.tasks to generate implementation tasks
- 🧠 Reflection: Implementation plan provides clear architecture for JWT-based authentication system

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
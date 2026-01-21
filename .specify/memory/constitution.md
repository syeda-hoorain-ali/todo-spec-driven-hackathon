<!-- SYNC IMPACT REPORT
Version change: N/A (initial version) → 1.0.0
Added sections: All principles and sections as specified
Removed sections: None
Templates requiring updates:
- .specify/templates/plan-template.md ⚠ pending
- .specify/templates/spec-template.md ⚠ pending
- .specify/templates/tasks-template.md ⚠ pending
- .specify/templates/commands/*.md ⚠ pending
Follow-up TODOs: None
-->
# Todo Spec-Driven Development Hackathon Constitution

## Core Principles

### Phase-Based Organization
All project artifacts must be organized by hackathon phases (Phase I-V) with dedicated folders in both code and specification directories: `specs/phase-01/`, `src/phase-01/`, etc. This ensures clear separation of concerns and progress tracking across the five hackathon phases.

### Spec-Driven Development
All development follows the Spec-Kit Plus methodology with proper specification, planning, and task documentation before implementation. No code implementation should proceed without approved specifications.

### Test-Driven Development (NON-NEGOTIABLE)
All Python code must follow TDD principles - write tests first, then implement functionality. The Red-Green-Refactor cycle must be strictly enforced. All code must have corresponding tests with adequate coverage before acceptance.

### Python Package Management with uv
Use `uv` as the exclusive package manager for all Python dependencies. All Python projects must use `pyproject.toml` for dependency specifications and follow modern Python packaging standards.

### Technology Stack Adherence
Adhere to the specified technology stack: Next.js 16+, TypeScript, Tailwind CSS for frontend; Python FastAPI with uv for backend; SQLModel with Neon Serverless PostgreSQL for database; Better Auth with JWT for authentication; OpenAI Agents SDK and MCP SDK for AI integration; DAPR for distributed application runtime; Apache Kafka for event streaming; Kubernetes for container orchestration; Docker for containerization.

### Quality Assurance Standards
Maintain high code quality through testing, documentation, and peer reviews. All features must include proper documentation and pass automated quality checks before acceptance.

### Clean Code Architecture Standards
All components and modules must follow clean architecture principles to ensure maintainability and scalability:

- **Minimize Prop Drilling**: Components should use hooks directly to access data rather than receiving functions through props. Dialogs and forms should use `use[Feature]` hooks directly instead of receiving callback functions to reduce prop chains.

- **Centralized Configurations**: Define shared configuration objects (options, display configs) in a central file like `src/features/[feature-name]/config.ts` to avoid duplication and ensure consistency.

- **Component Minimalism**: Each component should have minimal necessary props, with complex logic encapsulated in hooks rather than passed through multiple prop layers.

- **Icon Naming Convention**: All Lucide React icons must be imported with the "Icon" postfix (e.g., `PlusIcon`, `Trash2Icon`) to avoid naming conflicts.

## Additional Constraints

### Python Development Standards
- Follow PEP 8 guidelines for Python code
- Use type hints for all public interfaces
- Maintain high test coverage (minimum 80%)
- Use modern Python features appropriately
- Follow security best practices

### Deployment Standards
- Containerize all applications using Docker
- Use Kubernetes for orchestration (Minikube for local, DigitalOcean DOKS for production)
- Implement proper CI/CD pipelines
- Maintain environment parity across development, staging, and production

## Development Workflow

### Implementation Process
1. Create proper specifications before implementation
2. Follow the 5-phase hackathon progression
3. Develop reusable intelligence through skills and subagents
4. Perform regular integration and testing
5. Maintain continuous integration practices

### Review Process
- All code changes require peer review
- Specifications must be approved before implementation
- Test coverage must meet minimum requirements
- Documentation must be updated with each feature

### Quality Gates
- All tests must pass before merging
- Code coverage must meet minimum thresholds
- Security scans must pass
- Performance benchmarks must be met

## Governance

This constitution supersedes all other development practices and guidelines. Amendments to this constitution require explicit documentation, approval from project leadership, and a migration plan for existing code. All pull requests and code reviews must verify compliance with these principles. Complexity must be justified with clear benefits, and teams should reference this constitution for runtime development guidance.

All team members are expected to follow these principles consistently across all hackathon phases. Deviations must be documented and approved through the proper channels.

**Version**: 1.2.0 | **Ratified**: 2025-12-12 | **Last Amended**: 2025-12-12

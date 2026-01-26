# TaskFlow - The Evolution of Todo

TaskFlow is an innovative todo application that demonstrates the complete evolution of software development from a simple in-memory Python console app to a sophisticated, AI-powered, cloud-native application deployed on Kubernetes. It showcases modern development practices, progressive feature enhancement, and scalable architecture patterns.

---

## Todo App Feature Progression

### Basic Level (Core Essentials)

1. **Add Task** – Create new todo items ✅
2. **Delete Task** – Remove tasks from the list ✅
3. **Update Task** – Modify existing task details ✅
4. **View Task List** – Display all tasks ✅
5. **Mark as Complete** – Toggle task completion status ✅

### Intermediate Level (Organization & Usability)

1. **Priorities & Tags/Categories** – Assign levels (high/medium/low) or labels (work/home) ✅
2. **Search & Filter** – Search by keyword; filter by status, priority, or date ✅
3. **Sort Tasks** – Reorder by due date, priority, or alphabetically ✅

### Advanced Level (Intelligent Features)

1. **Recurring Tasks** – Auto-reschedule repeating tasks (e.g., "weekly meeting") ✅
2. **Due Dates & Time Reminders** – Set deadlines with date/time pickers; browser notifications ✅

### Bonus Features

1. **Reusable Intelligence** – Create and use reusable intelligence via Claude Code Subagents and Agent Skills ✅
2. **Cloud-Native Blueprints** – Create and use Cloud-Native Blueprints via Agent Skills ✅
3. **Multi-language Support** – Support Urdu in chatbot
4. **Voice Commands** – Add voice input for todo commands

---

## Hackathon Phases Overview

| Phase     | Description                  | Technology Stack                             |
| --------- | ---------------------------- | -------------------------------------------- |
| Phase I   | In-Memory Python Console App | Python, Claude Code, Spec-Kit Plus           |
| Phase II  | Full-Stack Web Application   | Next.js, FastAPI, SQLModel, Neon DB          |
| Phase III | AI-Powered Todo Chatbot      | OpenAI ChatKit, Agents SDK, Official MCP SDK |
| Phase IV  | Local Kubernetes Deployment  | Docker, Minikube, Helm, kubectl-ai, kagent   |
| Phase V   | Advanced Cloud Deployment    | Kafka, Dapr, DigitalOcean DOKS               |

---

## Phase Breakdown

### Phase I: Todo In-Memory Python Console App ✅
**Status:** Completed
**Tech Stack:** Python, Claude Code, Spec-Kit Plus
**Description:** Built a foundational todo application with core CRUD operations in an in-memory Python console. Implemented basic task management features with add, delete, update, and view functionality. Used Claude Code for rapid development and Spec-Kit Plus for structured development approach.
**Documentation:** [Phase I README](phase-01/README.md)

### Phase II: Todo Full-Stack Web Application ✅
**Status:** Completed
**Tech Stack:** Next.js, React Query, FastAPI, SQLModel, Neon DB, Better Auth, Tailwind CSS, date-fns, react-hook-form, zod
**Description:** Developed a full-stack web application with Next.js/React frontend and FastAPI backend. Added advanced features like priorities, tags, search, filtering, and sorting. Integrated with Neon PostgreSQL database for persistent storage and implemented proper data modeling with SQLModel. Added authentication with Better Auth and responsive UI with Tailwind CSS.
**Documentation:** [Phase II README](phase-02/README.md)

### Phase III: Todo AI Chatbot ✅
**Status:** Completed
**Tech Stack:** OpenAI ChatKit, OpenAI Agents SDK, Official MCP SDK
**Description:** Created an AI-powered todo chatbot that can understand natural language commands. Integrated OpenAI ChatKit for conversational interface and Model Context Protocol (MCP) servers for enhanced functionality. Added intelligent task management capabilities and multi-language support.
**Documentation:** [Phase III README](phase-03/README.md)

### Phase IV: Local Kubernetes Deployment ✅
**Status:** Completed
**Tech Stack:** Docker, Minikube, Helm, kubectl, kubectl-ai, kagent
**Description:** Containerized the entire application and deployed it on a local Kubernetes cluster. Created Helm charts for easy deployment, implemented service discovery, persistent storage, and ingress routing. Set up proper networking and configuration management for all services.
**Documentation:** [Phase IV README](phase-04/README.md)

### Phase V: Advanced Cloud Deployment ✅
**Status:** Implementation Complete, Awaiting Deployment
**Tech Stack:** Kafka, Dapr, DigitalOcean DOKS
**Description:** Implemented advanced cloud-native deployment with microservices architecture, event streaming with Kafka, and Dapr for distributed application runtime. Ready to deploy on DigitalOcean Kubernetes Service with advanced observability and scaling capabilities. Features separate audit, notification, and reminder services with shared Kafka components.
**Documentation:** [Phase V README](phase-05/README.md)

---

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for more details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

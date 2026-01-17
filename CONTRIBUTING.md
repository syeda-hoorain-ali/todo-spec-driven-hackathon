# Contributing to TaskFlow

Thank you for your interest in contributing to TaskFlow! We welcome contributions from the community and are grateful for your help in improving the project.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct. Please be respectful and considerate in all interactions.

## How to Contribute

### Reporting Bugs
- Use the issue tracker to report bugs
- Describe the issue clearly with steps to reproduce
- Include your environment details (OS, Python/Node.js version, etc.)
- Check if the issue already exists before creating a new one

### Suggesting Features
- Use the issue tracker to suggest new features
- Explain the feature and why it would be useful
- Discuss the potential implementation approach
- Consider the project's goals and scope

### Pull Requests
1. Fork the repository
2. Create a new branch for your feature or bug fix
3. Make your changes following the project's coding standards
4. Add tests if applicable
5. Update documentation as needed
6. Submit a pull request with a clear description of your changes

## Development Setup

### Prerequisites
- Python 3.8+ for backend development
- Node.js 18+ for frontend development
- Docker for containerization
- Minikube and Helm for Kubernetes deployment

### Getting Started
1. Clone the repository:
   ```bash
   git clone https://github.com/syeda-hoorain-ali/todo-spec-driven-hackathon.git
   cd taskflow
   ```

2. For Phase II (Full-Stack Web Application):
   ```bash
   # Backend
   cd phase-02/backend
   uv sync
   python main.py

   # Frontend
   cd phase-02/frontend
   npm install
   npm run dev
   ```

3. For Phase III (AI Chatbot):
   ```bash
   cd phase-03
   docker-compose up --build
   ```

4. For Phase IV (Kubernetes Deployment):
   ```bash
   cd phase-04
   # Run the setup and deployment scripts
   ./scripts/setup-minikube.sh
   ./scripts/deploy-app.sh
   ```

## Code Style

- Follow PEP 8 guidelines for Python code
- Use TypeScript for type safety where applicable
- Write clear, concise commit messages
- Include documentation for public APIs
- Add tests for new functionality

## Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests after the first line

## Testing

- Write unit tests for new functionality
- Ensure all tests pass before submitting a pull request
- Test your changes manually to verify they work as expected

## Questions?

If you have questions about contributing, feel free to open an issue or reach out to the maintainers.

Thank you for contributing to TaskFlow!

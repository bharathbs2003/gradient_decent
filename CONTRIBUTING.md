# Contributing to Multilingual AI Video Dubbing Platform

Thank you for your interest in contributing to the Multilingual AI Video Dubbing Platform! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Guidelines](#contributing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Documentation](#documentation)
- [Community](#community)

## Code of Conduct

This project adheres to a code of conduct that we expect all contributors to follow. Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md) to help us maintain a welcoming and inclusive community.

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Git
- Node.js 18+ (for frontend development)
- Python 3.11+ (for backend development)
- NVIDIA GPU (optional, for AI services)

### Quick Setup

1. **Fork the repository**
   ```bash
   git clone https://github.com/your-username/multilingual-ai-dubbing-platform.git
   cd multilingual-ai-dubbing-platform
   ```

2. **Run the setup script**
   ```bash
   chmod +x scripts/setup/install.sh
   ./scripts/setup/install.sh
   ```

3. **Start development environment**
   ```bash
   docker-compose up -d
   ```

## Development Setup

### Backend Development

1. **Set up Python environment**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Run backend locally**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Development

1. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Start development server**
   ```bash
   npm run dev
   ```

### AI Services Development

1. **Set up AI services environment**
   ```bash
   cd ai-services
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Run individual services**
   ```bash
   # ASR Service
   python -m asr.service
   
   # Translation Service
   python -m translation.service
   
   # TTS Service
   python -m tts.service
   
   # Face Animation Service
   python -m face-animation.service
   ```

## Contributing Guidelines

### Types of Contributions

We welcome various types of contributions:

- **Bug fixes**: Fix issues in existing functionality
- **Feature development**: Add new features per the roadmap
- **Documentation**: Improve or add documentation
- **Testing**: Add or improve test coverage
- **Performance**: Optimize existing code
- **AI Models**: Improve or add new AI models
- **Translations**: Add support for new languages

### Coding Standards

#### Python (Backend & AI Services)
- Follow PEP 8 style guide
- Use type hints for function parameters and return values
- Maximum line length: 88 characters (Black formatter)
- Use docstrings for all public functions and classes
- Use `structlog` for logging

```python
from typing import Dict, Any, Optional
import structlog

logger = structlog.get_logger()

async def process_video(
    video_path: str,
    target_languages: List[str],
    quality_mode: str = "structural"
) -> Dict[str, Any]:
    """
    Process video for multilingual dubbing.
    
    Args:
        video_path: Path to input video file
        target_languages: List of target language codes
        quality_mode: Processing quality mode
        
    Returns:
        Dictionary containing processing results
    """
    logger.info("Processing video", video_path=video_path)
    # Implementation here
```

#### TypeScript/React (Frontend)
- Use TypeScript for all new code
- Follow React best practices and hooks patterns
- Use functional components over class components
- Use Tailwind CSS for styling
- Maximum line length: 100 characters

```typescript
interface DubbingJobProps {
  jobId: string
  onComplete: (result: DubbingResult) => void
}

export const DubbingJob: React.FC<DubbingJobProps> = ({ 
  jobId, 
  onComplete 
}) => {
  const [progress, setProgress] = useState(0)
  
  // Implementation here
  
  return (
    <div className="card p-6">
      {/* JSX here */}
    </div>
  )
}
```

#### Database Migrations
- Use Alembic for database migrations
- Include both upgrade and downgrade functions
- Test migrations on sample data
- Document breaking changes

### Git Workflow

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clean, well-documented code
   - Add tests for new functionality
   - Update documentation as needed

3. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add multilingual voice cloning support"
   ```

4. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

### Commit Message Format

We use conventional commits for clear commit history:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(ai): add support for emotion-aware TTS
fix(frontend): resolve video upload progress display
docs(api): update authentication endpoint documentation
test(backend): add unit tests for dubbing service
```

## Pull Request Process

### Before Submitting

1. **Run tests**
   ```bash
   # Backend tests
   cd backend && pytest
   
   # Frontend tests
   cd frontend && npm test
   
   # AI services tests
   cd ai-services && python -m pytest
   ```

2. **Run linting and formatting**
   ```bash
   # Backend
   cd backend && black . && isort . && mypy .
   
   # Frontend
   cd frontend && npm run lint:fix && npm run type-check
   ```

3. **Update documentation**
   - Update API documentation if endpoints changed
   - Update user guide if UI changed
   - Add or update inline code comments

### Pull Request Template

When creating a pull request, please use this template:

```markdown
## Description
Brief description of the changes made.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] AI model quality metrics meet targets

## Quality Metrics (if applicable)
- LSE-C Score: X.XX
- FID Score: X.XX
- BLEU Score: X.XX
- Processing Time: X.X minutes per minute of video

## Screenshots (if applicable)
Add screenshots for UI changes.

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Code is commented, particularly in hard-to-understand areas
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] No breaking changes (or breaking changes documented)
```

### Review Process

1. **Automated Checks**: All PRs must pass automated tests and linting
2. **Code Review**: At least one maintainer must review and approve
3. **AI Quality Review**: Changes to AI services require quality metric validation
4. **Documentation Review**: Documentation changes reviewed for accuracy
5. **Security Review**: Security-sensitive changes require additional review

## Issue Reporting

### Bug Reports

Use the bug report template:

```markdown
**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected behavior**
A clear and concise description of what you expected to happen.

**Screenshots**
If applicable, add screenshots to help explain your problem.

**Environment:**
- OS: [e.g. Ubuntu 20.04]
- Browser: [e.g. Chrome 91]
- Version: [e.g. 1.0.0]
- GPU: [e.g. NVIDIA RTX 4090]

**Additional context**
Add any other context about the problem here.
```

### Feature Requests

Use the feature request template:

```markdown
**Is your feature request related to a problem?**
A clear and concise description of what the problem is.

**Describe the solution you'd like**
A clear and concise description of what you want to happen.

**Describe alternatives you've considered**
A clear and concise description of any alternative solutions or features you've considered.

**Additional context**
Add any other context or screenshots about the feature request here.

**PRD Alignment**
How does this feature align with the Product Requirements Document?
```

## Testing

### Test Categories

1. **Unit Tests**: Test individual functions and components
2. **Integration Tests**: Test service interactions
3. **End-to-End Tests**: Test complete user workflows
4. **Performance Tests**: Test processing speed and resource usage
5. **Quality Tests**: Test AI model output quality

### Running Tests

```bash
# All tests
docker-compose run --rm backend pytest
docker-compose run --rm frontend npm test

# Specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/quality/

# With coverage
pytest --cov=app tests/
```

### Writing Tests

#### Backend Tests (pytest)
```python
import pytest
from app.services.dubbing import DubbingService

@pytest.mark.asyncio
async def test_dubbing_service_creates_job():
    """Test that dubbing service creates job correctly."""
    service = DubbingService(db_session)
    
    job = await service.create_dubbing_job(
        user=test_user,
        video_file=test_video,
        request=test_request
    )
    
    assert job.id is not None
    assert job.status == JobStatus.PENDING
```

#### Frontend Tests (Jest + React Testing Library)
```typescript
import { render, screen, fireEvent } from '@testing-library/react'
import { DubbingPage } from '@/pages/DubbingPage'

test('renders dubbing form', () => {
  render(<DubbingPage />)
  
  expect(screen.getByText('Create New Dubbing Project')).toBeInTheDocument()
  expect(screen.getByText('Upload your video')).toBeInTheDocument()
})

test('handles file upload', async () => {
  render(<DubbingPage />)
  
  const file = new File(['video content'], 'test.mp4', { type: 'video/mp4' })
  const input = screen.getByLabelText(/upload/i)
  
  fireEvent.change(input, { target: { files: [file] } })
  
  expect(screen.getByText('test.mp4')).toBeInTheDocument()
})
```

## Documentation

### Types of Documentation

1. **API Documentation**: OpenAPI/Swagger specs
2. **User Guides**: Step-by-step tutorials
3. **Architecture Docs**: System design and components
4. **Code Comments**: Inline documentation
5. **README Files**: Project and component overviews

### Documentation Standards

- Use clear, concise language
- Include code examples
- Add screenshots for UI features
- Keep documentation up-to-date with code changes
- Use Markdown for all documentation files

### Building Documentation

```bash
# Generate API docs
cd backend && python -c "
from app.main import app
import json
with open('openapi.json', 'w') as f:
    json.dump(app.openapi(), f, indent=2)
"

# Build user guide
cd docs && mkdocs build
```

## Community

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and discussions
- **Discord**: Real-time chat (link in README)
- **Email**: maintainers@aidubbing.ai

### Getting Help

1. **Check existing issues**: Search for similar problems
2. **Read documentation**: Check docs/ directory
3. **Ask in discussions**: Use GitHub Discussions for questions
4. **Join Discord**: Get real-time help from community

### Recognition

Contributors are recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project README
- Annual contributor awards

## AI Ethics Guidelines

### Responsible AI Development

- **Bias Testing**: Test models across diverse demographics
- **Fairness Metrics**: Measure and report fairness metrics
- **Transparency**: Document model capabilities and limitations
- **Privacy**: Implement privacy-preserving techniques
- **Consent**: Ensure proper consent for voice and likeness use

### Quality Standards

All AI contributions must meet PRD quality targets:
- LSE-C ≥ 0.85 for lip-sync accuracy
- FID ≤ 15 for visual fidelity
- AU correlation ≥ 0.75 for emotion preservation
- BLEU ≥ 35 for translation quality

### Model Contributions

When contributing AI models:
1. Include model cards with performance metrics
2. Document training data and methodology
3. Test on diverse datasets
4. Provide quality benchmarks
5. Include ethical considerations

## Release Process

### Version Numbering

We use Semantic Versioning (SemVer):
- MAJOR.MINOR.PATCH (e.g., 1.2.3)
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes (backward compatible)

### Release Checklist

- [ ] All tests pass
- [ ] Documentation updated
- [ ] Quality metrics validated
- [ ] Security review completed
- [ ] Performance benchmarks run
- [ ] Breaking changes documented
- [ ] Migration scripts tested

Thank you for contributing to the Multilingual AI Video Dubbing Platform! Your contributions help make high-quality multilingual content accessible to everyone.
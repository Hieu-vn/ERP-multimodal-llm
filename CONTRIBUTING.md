# 🤝 Contributing Guide

Cám ơn bạn đã quan tâm đến việc đóng góp cho **ERP AI Pro Version**! Chúng tôi hoan nghênh mọi đóng góp từ cộng đồng để cùng nhau xây dựng một hệ thống AI ERP tốt nhất.

## 📋 Mục lục

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
- [Issue Guidelines](#issue-guidelines)
- [Community](#community)

## 📜 Code of Conduct

Dự án này tuân theo [Contributor Covenant](https://www.contributor-covenant.org/). Bằng cách tham gia, bạn đồng ý tuân thủ các quy tắc này. Vui lòng báo cáo hành vi không phù hợp tại [email@example.com].

### Các nguyên tắc cốt lõi:
- **Tôn trọng**: Đối xử tôn trọng với mọi người
- **Inclusive**: Chào đón mọi background và kinh nghiệm
- **Constructive**: Phản hồi xây dựng và hữu ích
- **Professional**: Duy trì môi trường chuyên nghiệp

## 🚀 Getting Started

### Prerequisites

1. **Python 3.10+**
2. **Git**
3. **Docker & Docker Compose**
4. **Neo4j** (local hoặc Docker)
5. **GPU** (optional, cho development)

### Development Setup

```bash
# 1. Fork và clone repository
git clone https://github.com/yourusername/ERP-multimodel-llm.git
cd ERP-multimodel-llm

# 2. Tạo development branch
git checkout -b feature/your-feature-name

# 3. Cài đặt development environment
python -m venv venv
source venv/bin/activate  # Trên Windows: venv\Scripts\activate

# 4. Cài đặt dependencies
pip install -r requirements.pro.txt
pip install -r requirements-dev.txt  # Development dependencies

# 5. Setup pre-commit hooks
pre-commit install

# 6. Cấu hình environment
cp .env.example .env.development
# Chỉnh sửa .env.development với settings phù hợp

# 7. Setup databases
docker-compose -f docker-compose.dev.yml up -d neo4j redis

# 8. Chạy ETL và tạo vector store
python data_ingestion/etl_erp_data.py
python run_create_vector_store.py

# 9. Chạy tests để đảm bảo setup đúng
python -m pytest tests/

# 10. Start development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 🔄 Development Workflow

### Git Workflow

Chúng tôi sử dụng **Git Flow** cho development workflow:

```bash
# 1. Luôn bắt đầu từ main branch mới nhất
git checkout main
git pull origin main

# 2. Tạo feature branch
git checkout -b feature/your-feature-name
# hoặc
git checkout -b fix/bug-description
# hoặc
git checkout -b docs/documentation-update

# 3. Commit thường xuyên với descriptive messages
git add .
git commit -m "feat: add new query enhancement feature"

# 4. Push và tạo Pull Request
git push origin feature/your-feature-name
```

### Branch Naming Convention

- `feature/feature-name`: New features
- `fix/bug-description`: Bug fixes
- `docs/documentation-topic`: Documentation updates
- `refactor/component-name`: Code refactoring
- `test/test-description`: Test improvements
- `chore/task-description`: Maintenance tasks

### Commit Message Format

Sử dụng [Conventional Commits](https://conventionalcommits.org/):

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Maintenance

**Examples:**
```
feat(rag-pipeline): add query rewriting functionality
fix(neo4j): resolve connection timeout issue
docs(api): update endpoint documentation
refactor(agents): improve error handling in finance agent
test(unit): add tests for vector search functionality
```

## 📝 Coding Standards

### Python Style Guide

Chúng tôi tuân theo **PEP 8** với một số modifications:

```python
# 1. Imports organization
from __future__ import annotations

# Standard library imports
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Third-party imports
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import torch

# Local imports
from erp_ai_core.models import QueryRequest
from config.rag_config import RAGConfig

# 2. Class definitions
class RAGPipeline:
    """
    A professional, end-to-end RAG pipeline for the ERP assistant.
    
    This class orchestrates the retrieval, prompt formatting, and 
    language model generation process.
    """
    
    def __init__(self) -> None:
        """Initialize the pipeline components."""
        self.config = RAGConfig()
        self.vector_store: Optional[VectorStore] = None
        self.llm: Optional[LLM] = None

    async def query(self, role: str, question: str) -> Dict[str, Any]:
        """
        Process a user query and return AI-generated response.
        
        Args:
            role: User role in the ERP system
            question: Natural language question
            
        Returns:
            Dictionary containing answer and source documents
            
        Raises:
            RuntimeError: If pipeline is not properly initialized
        """
        if not self.llm:
            raise RuntimeError("Pipeline not initialized")
            
        # Implementation here...
        return {"answer": "", "source_documents": []}

# 3. Type hints
def process_documents(docs: List[Document]) -> Dict[str, List[str]]:
    """Process and categorize documents."""
    result: Dict[str, List[str]] = {}
    return result

# 4. Constants
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30
API_VERSION = "1.0.0"
```

### Code Quality Tools

```bash
# Linting với flake8
flake8 erp_ai_core/ --max-line-length=100

# Type checking với mypy
mypy erp_ai_core/

# Code formatting với black
black erp_ai_core/ --line-length=100

# Import sorting với isort
isort erp_ai_core/ --profile black

# Security scanning với bandit
bandit -r erp_ai_core/
```

### Configuration trong .pre-commit-config.yaml

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
        language_version: python3
        args: [--line-length=100]

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: [--profile, black]

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=100]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.0.1
    hooks:
      - id: mypy
```

## 🧪 Testing Guidelines

### Test Structure

```
tests/
├── unit/                   # Unit tests
│   ├── test_rag_pipeline.py
│   ├── test_agents.py
│   └── test_tools.py
├── integration/            # Integration tests
│   ├── test_api_endpoints.py
│   ├── test_database_operations.py
│   └── test_model_pipeline.py
├── e2e/                    # End-to-end tests
│   └── test_full_workflow.py
├── performance/            # Performance tests
│   └── test_load_testing.py
├── fixtures/               # Test data và fixtures
│   ├── sample_queries.json
│   └── mock_responses.json
└── conftest.py            # Pytest configuration
```

### Writing Tests

```python
# tests/unit/test_rag_pipeline.py
import pytest
from unittest.mock import Mock, patch
from erp_ai_core.rag_pipeline import RAGPipeline
from erp_ai_core.models import QueryRequest

class TestRAGPipeline:
    """Test suite for RAG Pipeline functionality."""
    
    @pytest.fixture
    def mock_pipeline(self):
        """Create a mock RAG pipeline for testing."""
        pipeline = RAGPipeline()
        pipeline.llm = Mock()
        pipeline.vector_store = Mock()
        return pipeline
    
    @pytest.mark.asyncio
    async def test_query_success(self, mock_pipeline):
        """Test successful query processing."""
        # Arrange
        role = "warehouse_manager"
        question = "Làm thế nào để kiểm tra tồn kho?"
        expected_answer = "Để kiểm tra tồn kho..."
        
        mock_pipeline.llm.generate.return_value = expected_answer
        mock_pipeline.vector_store.search.return_value = []
        
        # Act
        result = await mock_pipeline.query(role, question)
        
        # Assert
        assert result["answer"] == expected_answer
        assert "source_documents" in result
        mock_pipeline.llm.generate.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_query_with_invalid_role(self, mock_pipeline):
        """Test query with invalid user role."""
        # Arrange
        role = "invalid_role"
        question = "Test question"
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid role"):
            await mock_pipeline.query(role, question)

    @pytest.mark.parametrize("role,expected_tools", [
        ("admin", ["get_current_date", "vector_search", "graph_erp_lookup"]),
        ("sales_rep", ["get_current_date", "vector_search"]),
        ("warehouse_manager", ["get_current_date", "vector_search", "get_product_stock_level"]),
    ])
    def test_role_based_tool_access(self, mock_pipeline, role, expected_tools):
        """Test that tools are correctly assigned based on user role."""
        # Arrange & Act
        allowed_tools = mock_pipeline._get_allowed_tools(role)
        
        # Assert
        assert set(expected_tools).issubset(set(allowed_tools))
```

### Test Commands

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=erp_ai_core --cov-report=html

# Run specific test categories
python -m pytest tests/unit/          # Unit tests only
python -m pytest tests/integration/   # Integration tests only
python -m pytest -m slow             # Slow tests only

# Run tests với specific markers
python -m pytest -m "not gpu"        # Skip GPU tests
python -m pytest -k "test_query"     # Run query-related tests only

# Performance testing
python -m pytest tests/performance/ --benchmark-only
```

## 📚 Documentation

### Code Documentation

```python
def query_enhancement(self, query: str, max_expansions: int = 3) -> List[str]:
    """
    Enhance user query through rewriting and expansion.
    
    This method takes a user's natural language query and generates
    alternative formulations to improve retrieval performance.
    
    Args:
        query: Original user query in Vietnamese
        max_expansions: Maximum number of query variations to generate
        
    Returns:
        List of enhanced query strings, including the original
        
    Raises:
        ValueError: If query is empty or max_expansions is invalid
        
    Example:
        >>> enhancer = QueryEnhancer()
        >>> enhanced = enhancer.query_enhancement("Tồn kho hiện tại?")
        >>> print(enhanced)
        ['Tồn kho hiện tại?', 'Kiểm tra tồn kho', 'Số lượng hàng tồn kho']
        
    Note:
        This method uses the configured LLM for query rewriting.
        Performance may vary based on model capabilities.
    """
    if not query.strip():
        raise ValueError("Query cannot be empty")
        
    if max_expansions < 1 or max_expansions > 10:
        raise ValueError("max_expansions must be between 1 and 10")
        
    # Implementation...
    return enhanced_queries
```

### API Documentation

Sử dụng FastAPI's automatic documentation:

```python
from fastapi import FastAPI, HTTPException, Query
from typing import Optional

app = FastAPI(
    title="ERP AI Pro API",
    description="AI-powered assistant for ERP systems",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.post("/query", 
          summary="Process natural language query",
          description="Submit a question in Vietnamese and receive AI-generated answer",
          response_description="AI response with sources and reasoning")
async def query_endpoint(
    request: QueryRequest,
    include_reasoning: Optional[bool] = Query(
        False, 
        description="Include step-by-step reasoning in response"
    )
) -> QueryResponse:
    """
    Process a natural language query about ERP data.
    
    - **role**: User role (admin, finance_manager, sales_rep, etc.)
    - **question**: Question in Vietnamese natural language
    - **include_reasoning**: Whether to include AI reasoning steps
    
    Returns comprehensive answer with source citations.
    """
    # Implementation...
```

## 🔄 Pull Request Process

### Before Submitting

1. **Code Quality Checklist:**
   - [ ] Code follows style guidelines
   - [ ] All tests pass locally
   - [ ] New tests added for new functionality
   - [ ] Documentation updated
   - [ ] No security vulnerabilities
   - [ ] Performance impact considered

2. **Testing Checklist:**
   - [ ] Unit tests cover new code
   - [ ] Integration tests updated if needed
   - [ ] Manual testing completed
   - [ ] Edge cases considered

### PR Template

```markdown
## Description
Brief description of changes and motivation.

## Type of Change
- [ ] Bug fix (non-breaking change)
- [ ] New feature (non-breaking change)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed
- [ ] Performance impact assessed

## Screenshots (if applicable)
Include screenshots for UI changes.

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Code is commented where necessary
- [ ] Documentation updated
- [ ] No new warnings or errors
```

### Review Process

1. **Automated Checks**: CI/CD pipeline runs automatically
2. **Code Review**: At least 2 reviewers required
3. **Testing**: All tests must pass
4. **Documentation**: Must be updated if applicable
5. **Approval**: Maintainer approval required for merge

## 🐛 Issue Guidelines

### Bug Reports

Sử dụng template sau cho bug reports:

```markdown
**Bug Description**
Clear và concise description of the bug.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected Behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment:**
- OS: [e.g. Ubuntu 20.04]
- Python Version: [e.g. 3.10.8]
- Docker Version: [e.g. 20.10.21]
- GPU: [e.g. NVIDIA RTX 4080]

**Additional Context**
Any other context about the problem.
```

### Feature Requests

```markdown
**Feature Description**
Clear description of the proposed feature.

**Problem Statement**
What problem does this feature solve?

**Proposed Solution**
Detailed description of the proposed implementation.

**Alternatives Considered**
Alternative solutions you've considered.

**Additional Context**
Any other context, mockups, or examples.
```

### Issue Labels

- `bug`: Something isn't working
- `enhancement`: New feature or request
- `documentation`: Improvements or additions to docs
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention is needed
- `priority:high`: High priority issue
- `priority:low`: Low priority issue

## 👥 Community

### Communication Channels

- **GitHub Issues**: Bug reports và feature requests
- **GitHub Discussions**: General discussions và Q&A
- **Discord**: Real-time chat và community support
- **Email**: [maintainers@erp-ai-pro.com] cho private concerns

### Getting Help

1. **Documentation**: Check existing docs first
2. **Search Issues**: Look for existing solutions
3. **GitHub Discussions**: Ask questions in discussions
4. **Discord**: Get real-time help from community

### Recognition

Chúng tôi recognize contributors through:

- **Contributors file**: Listed in CONTRIBUTORS.md
- **Release notes**: Major contributions mentioned
- **Discord roles**: Special roles for active contributors
- **Swag**: Stickers và merchandise cho active contributors

## 🏆 Contribution Areas

### High-Priority Areas

1. **Model Optimization**: Fine-tuning và performance improvements
2. **Multi-language Support**: Adding support for English, Chinese
3. **Advanced Analytics**: ML-powered insights và predictions
4. **Mobile SDK**: React Native hoặc Flutter SDK
5. **Documentation**: Tutorials, guides, examples

### Good First Issues

- Fix typos trong documentation
- Add unit tests cho existing functionality
- Improve error messages
- Add Vietnamese translations
- Create example notebooks

## 📈 Roadmap Contributions

Interested trong shaping the future? Check out our:

- **Project Roadmap**: Long-term vision và plans
- **Architecture Decisions**: Technical design discussions
- **Feature Proposals**: Community-driven feature planning

---

**Cảm ơn bạn đã đóng góp vào ERP AI Pro Version! 🚀**

Mọi đóng góp, dù lớn hay nhỏ, đều được đánh giá cao và giúp cải thiện dự án cho toàn bộ cộng đồng.
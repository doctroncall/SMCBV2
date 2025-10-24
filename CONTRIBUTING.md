# 🤝 Contributing to MT5 Sentiment Analysis Bot

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## 📋 Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Code Style](#code-style)

## 📜 Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Follow project conventions

## 🚀 Getting Started

1. Fork the repository
2. Clone your fork
3. Create a feature branch
4. Make your changes
5. Submit a pull request

## 💻 Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/CURSOR-SMC-MAIN.git
cd CURSOR-SMC-MAIN

# Add upstream remote
git remote add upstream https://github.com/doctroncall/CURSOR-SMC-MAIN.git

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-cov black flake8 mypy
```

## 🔨 Making Changes

### Branch Naming
```
feature/your-feature-name
bugfix/issue-description
hotfix/critical-fix
docs/documentation-update
```

### Commit Messages
Follow conventional commits:
```
feat: Add new indicator
fix: Resolve MT5 connection issue
docs: Update README
refactor: Improve code structure
test: Add unit tests for analyzer
```

## 🧪 Testing

### Run All Tests
```bash
pytest
```

### Run with Coverage
```bash
pytest --cov=src tests/
```

### Test Specific Module
```bash
pytest tests/unit/test_indicators.py
```

### Write Tests

```python
def test_rsi_calculation():
    """Test RSI indicator calculation"""
    indicators = TechnicalIndicators()
    df = create_test_data()
    rsi = indicators.calculate_rsi(df)
    assert rsi is not None
    assert len(rsi) > 0
```

## 📤 Submitting Changes

### Pull Request Process

1. **Update your fork**:
```bash
git fetch upstream
git rebase upstream/main
```

2. **Make sure tests pass**:
```bash
pytest
```

3. **Format code**:
```bash
black .
flake8 .
```

4. **Commit and push**:
```bash
git add .
git commit -m "feat: Your feature description"
git push origin your-branch-name
```

5. **Create Pull Request**:
- Go to GitHub
- Click "New Pull Request"
- Select your branch
- Fill in template
- Submit

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass
- [ ] New tests added
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings generated
```

## 🎨 Code Style

### Python Style Guide

Follow PEP 8 with these specifics:

```python
# Good
def calculate_sentiment(
    df: pd.DataFrame,
    symbol: str,
    timeframe: str
) -> Dict[str, Any]:
    """
    Calculate market sentiment
    
    Args:
        df: OHLCV DataFrame
        symbol: Trading symbol
        timeframe: Analysis timeframe
        
    Returns:
        Dict with sentiment analysis
    """
    # Implementation
    pass

# Bad
def calculate_sentiment(df,symbol,timeframe):
    # No docstring, no types
    pass
```

### Formatting Tools

```bash
# Format code
black src/

# Check style
flake8 src/

# Type checking
mypy src/
```

### Docstring Format

```python
def function_name(arg1: Type1, arg2: Type2) -> ReturnType:
    """
    Brief description of function
    
    Detailed description if needed
    
    Args:
        arg1: Description of arg1
        arg2: Description of arg2
        
    Returns:
        Description of return value
        
    Raises:
        ExceptionType: When this exception occurs
        
    Example:
        >>> result = function_name(val1, val2)
        >>> print(result)
    """
```

## 📁 Project Structure

```
src/
├── mt5/            # MT5 integration
├── indicators/     # Technical indicators & SMC
├── analysis/       # Sentiment analysis
├── ml/             # Machine learning
├── health/         # Health monitoring
├── reporting/      # Reports and charts
├── database/       # Data persistence
└── utils/          # Utilities

gui/
└── components/     # Streamlit components

config/             # Configuration files
tests/              # Test suite
```

## 🐛 Reporting Bugs

### Bug Report Template

```markdown
## Bug Description
Clear description of the bug

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: [e.g., Windows 10]
- Python: [e.g., 3.10.5]
- Version: [e.g., v1.0.0]

## Additional Context
Any other relevant information
```

## 💡 Feature Requests

### Feature Request Template

```markdown
## Feature Description
Clear description of the feature

## Use Case
Why is this feature needed?

## Proposed Solution
How should it work?

## Alternatives Considered
Other approaches you've thought about

## Additional Context
Any other relevant information
```

## 📚 Documentation

### Documentation Updates

- Keep README.md up to date
- Update SETUP_GUIDE.md for setup changes
- Add docstrings to all functions
- Update YAML configs for new parameters
- Create examples for new features

### Documentation Style

```python
"""
Module Description
One-line description

Detailed description of the module,
its purpose, and usage.
"""

class ClassName:
    """
    Class description
    
    Attributes:
        attr1: Description
        attr2: Description
    """
    
    def method_name(self, param: Type) -> ReturnType:
        """
        Method description
        
        Args:
            param: Parameter description
            
        Returns:
            Return value description
        """
```

## 🏆 Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in documentation

## ❓ Questions?

- Open an issue for questions
- Check existing issues first
- Provide as much context as possible

---

Thank you for contributing! 🙏

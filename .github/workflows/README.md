# GitHub Actions Workflows

This directory contains the CI/CD workflows for the gpt-buddy project.

## Workflows

### 1. Run Tests (`test.yml`)
**Trigger:** Every push and pull request to any branch

**Purpose:** Run the test suite across multiple Python versions

**Steps:**
- Test on Python 3.10, 3.11, and 3.12
- Install system dependencies (portaudio)
- Install Python dependencies from requirements.txt and requirements-dev.txt
- Run black code formatter check
- Execute pytest with coverage
- Upload coverage reports to Codecov
- Archive test results as artifacts

**Artifacts:**
- Test coverage reports (HTML and XML)
- Coverage data files

### 2. Create Release (`release.yml`)
**Trigger:** Push to `main` branch (excluding documentation and test changes)

**Purpose:** Automatically create a new release when code is merged to main

**Steps:**
- Generate version number (from git tag or date-based)
- Check if version already exists (avoid duplicates)
- Create release archive (tar.gz) excluding unnecessary files
- Generate release notes from commit history
- Create GitHub release with archive attachment
- Tag the release

**Release Contents:**
- Source code (excluding .git, lib, bin, venv, etc.)
- All application files
- Configuration templates
- Documentation

**Version Format:**
- If git tag exists: use tag name
- Otherwise: `vYYYY.MM.DD-<short-hash>`

### 3. Code Quality (`lint.yml`)
**Trigger:** Every push and pull request to any branch

**Purpose:** Check code quality and security

**Steps:**
- Check code formatting with black
- Lint code with flake8
- Run security analysis with bandit
- Check for known vulnerabilities with safety

**Artifacts:**
- Bandit security report (JSON)

## Setting Up Workflows

### Prerequisites
No additional setup required. The workflows use GitHub Actions' built-in features and public actions.

### Optional: Codecov Integration
To enable coverage reporting to Codecov:
1. Sign up at https://codecov.io
2. Add your repository
3. No token needed for public repositories
4. Coverage reports will be automatically uploaded

### Customization

#### Changing Python Versions
Edit `test.yml`:
```yaml
matrix:
  python-version: ["3.10", "3.11", "3.12"]  # Modify this list
```

#### Adjusting Release Triggers
Edit `release.yml` to change when releases are created:
```yaml
on:
  push:
    branches:
      - main  # Change this to release branch name
```

#### Modifying Code Quality Checks
Edit `lint.yml` to adjust linting rules:
- Black: Change line length in pyproject.toml
- Flake8: Modify `--max-complexity` and `--max-line-length` flags
- Bandit: Add exclusions with `-x` flag
- Safety: Add ignored vulnerabilities with `--ignore` flag

## Viewing Results

### Test Results
1. Go to Actions tab in GitHub repository
2. Click on "Run Tests" workflow
3. View test results and coverage for each Python version
4. Download artifacts for detailed HTML coverage reports

### Releases
1. Go to Releases page in GitHub repository
2. View all created releases with download links
3. Each release includes:
   - Release notes with commit history
   - Source code archive (tar.gz)
   - Installation instructions

### Code Quality
1. Go to Actions tab in GitHub repository
2. Click on "Code Quality" workflow
3. View linting results and security reports
4. Download bandit report artifact for detailed security analysis

## Troubleshooting

### Tests Failing
1. Check if all dependencies are installed correctly
2. Verify Python version compatibility
3. Review test logs in Actions tab
4. Run tests locally: `pytest --cov=. --cov-report=term-missing`

### Release Not Created
1. Check if push was to main branch
2. Verify changes are not documentation-only
3. Check workflow logs for errors
4. Ensure GitHub token has write permissions

### Linting Errors
1. Run black locally: `black .`
2. Run flake8 locally: `flake8 .`
3. Fix reported issues
4. Commit and push changes

## Local Testing

Before pushing, test workflows locally:

```bash
# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests
pytest --cov=. --cov-report=html

# Check formatting
black --check .

# Run linter
flake8 .

# Security check
bandit -r .

# Check for vulnerabilities
safety check
```

## Workflow Status Badges

Add these badges to your README.md:

```markdown
![Tests](https://github.com/janiluuk/gpt-buddy/actions/workflows/test.yml/badge.svg)
![Code Quality](https://github.com/janiluuk/gpt-buddy/actions/workflows/lint.yml/badge.svg)
```

## Future Enhancements

Potential improvements for workflows:
- [ ] Add Docker build and push workflow
- [ ] Add deployment workflow for staging/production
- [ ] Integrate with issue/PR templates
- [ ] Add automatic changelog generation
- [ ] Set up scheduled dependency updates (Dependabot)
- [ ] Add performance benchmarking
- [ ] Integrate with code review tools

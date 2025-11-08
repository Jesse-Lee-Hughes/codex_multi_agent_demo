# Repository Guidelines

## Project Structure & Module Organization
Keep source modules in `agents/` with one directory per agent, and shared utilities under `core/`. Support scripts belong in `scripts/`, documentation updates go to `docs/`, and integration assets such as prompts or fixtures live in `resources/`. Mirror test layout in `tests/` so each agent module has a matching test module (for example, `agents/chat/builder.py` pairs with `tests/chat/test_builder.py`). This structure keeps agent logic isolated while reusing shared tooling.

## Build, Test, and Development Commands
Create an isolated environment before installing dependencies:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```
Run formatting, linting, typing, and tests locally before opening a pull request:
```bash
ruff check .
ruff format .
mypy agents core
pytest
```
If you add scripts, wrap them in `python -m` invocations or expose them via `scripts/` with executable bits removed.

## Coding Style & Naming Conventions
Follow PEP 8 with 4-space indentation and black-compatible line wrapping (88 columns). Name agent classes with the pattern `XYZAgent` and keep module names snake_case. Prefer explicit imports over `*`. Use type hints throughout, and document public entry points with succinct docstrings explaining agent responsibilities and side effects. Enforce formatting with `ruff format` and static checks with `mypy`.

## Testing Guidelines
Write unit tests with `pytest` and place fixtures under `tests/fixtures/`. Name test files `test_<module>.py` and individual tests `test_<behavior>`. Maintain at least 90% coverage for agent-critical paths; run `pytest --cov=agents --cov=core --cov-report=term-missing` before submitting. Capture asynchronous flows using `pytest.mark.asyncio` where applicable, and add regression tests for every bug fix.

## Commit & Pull Request Guidelines
Use Conventional Commit prefixes (`feat:`, `fix:`, `docs:`, `chore:`, `refactor:`) to keep history searchable. Each PR should include a concise summary, implementation notes, test results, and links to tracking issues. When altering agent behavior, outline expected inputs/outputs and provide examples or updated prompt snippets in the description. Request reviews from domain owners and keep diffs focused; split mechanic changes from behavior updates when possible.

## Agent-Specific Notes
Document new tools or integrations in `agents/<name>/README.md`, including environment variables and rate limits. When shipping prompt updates, archive the prior version in `docs/prompts/CHANGELOG.md` so operators can audit differences. Treat configuration secrets via `.env.example` only—never commit real credentials.

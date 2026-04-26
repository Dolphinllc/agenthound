.PHONY: help install dev test lint format scan serve ui ui-build clean

help:  ## Show this help.
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

install:  ## Install backend + frontend dependencies.
	uv sync --all-extras --dev
	cd frontend && pnpm install

dev:  ## Run backend + frontend in two tmux panes.
	tmux new-session -d -s agenthound 'uv run agenthound serve --reload'
	tmux split-window -h -t agenthound 'cd frontend && pnpm dev'
	tmux attach -t agenthound

test:  ## Run backend tests with coverage.
	uv run pytest --cov=agenthound --cov-report=term-missing

lint:  ## Lint backend (ruff) and frontend.
	uv run ruff check src tests
	cd frontend && pnpm lint

format:  ## Auto-format backend (ruff) and frontend (prettier).
	uv run ruff format src tests
	cd frontend && pnpm format 2>/dev/null || true

scan:  ## Run a sample scan and pretty-print the summary.
	uv run agenthound scan

serve:  ## Run backend only.
	uv run agenthound serve --reload

ui:  ## Run frontend dev server only.
	cd frontend && pnpm dev

ui-build:  ## Build frontend for production.
	cd frontend && pnpm build

clean:  ## Remove caches and build artifacts.
	rm -rf .pytest_cache .ruff_cache dist build *.egg-info
	rm -rf frontend/.next frontend/node_modules

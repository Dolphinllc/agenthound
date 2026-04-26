# Multi-stage build: builds the Next.js UI then ships it together with the
# FastAPI backend. The result is a single image that runs `agenthound serve`
# and serves the UI via a sibling Caddy or Nginx process — or you can run
# the UI separately for development.
FROM node:lts-slim AS ui-builder
WORKDIR /ui
COPY frontend/package.json frontend/bun.lock* frontend/package-lock.json* ./
RUN npm install -g pnpm && pnpm install --frozen-lockfile || pnpm install
COPY frontend/ .
RUN pnpm build

FROM python:3.14-slim AS runtime
WORKDIR /app
RUN pip install --no-cache-dir uv
COPY pyproject.toml uv.lock README.md ./
COPY src/ ./src/
RUN uv sync --frozen --no-dev
COPY --from=ui-builder /ui/.next ./frontend/.next
COPY --from=ui-builder /ui/public ./frontend/public
EXPOSE 8765
ENV PYTHONUNBUFFERED=1
CMD ["uv", "run", "agenthound", "serve", "--host", "0.0.0.0", "--port", "8765"]

"""FastAPI application exposing the scan pipeline as a JSON HTTP API.

Routes:
    GET  /api/health       — liveness probe
    GET  /api/scan/sample  — run the bundled sample and return ScanResult
    POST /api/scan         — run a scan against an uploaded config + catalog
"""

from __future__ import annotations

import json
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Annotated

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from agenthound.models import ScanResult
from agenthound.scan import scan, sample_paths


def create_app() -> FastAPI:
    app = FastAPI(
        title="AgentHound API",
        version="0.1.0",
        description="Map AI agent attack paths through MCP tool chains.",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "agenthound"}

    @app.get("/api/scan/sample", response_model=ScanResult)
    def scan_sample() -> ScanResult:
        return scan()

    @app.get("/api/samples")
    def samples() -> JSONResponse:
        cfg, cat = sample_paths()
        return JSONResponse({
            "claude_desktop_config": json.loads(Path(cfg).read_text()),
            "tool_catalog": json.loads(Path(cat).read_text()),
        })

    @app.post("/api/scan", response_model=ScanResult)
    async def scan_upload(
        config: Annotated[UploadFile, File(description="claude_desktop_config.json")],
        catalog: Annotated[UploadFile, File(description="MCP tool catalog JSON")],
    ) -> ScanResult:
        try:
            with (
                NamedTemporaryFile("wb", suffix=".json", delete=False) as cfg_tmp,
                NamedTemporaryFile("wb", suffix=".json", delete=False) as cat_tmp,
            ):
                cfg_tmp.write(await config.read())
                cat_tmp.write(await catalog.read())
                cfg_path = cfg_tmp.name
                cat_path = cat_tmp.name
            return scan(cfg_path, cat_path)
        except json.JSONDecodeError as exc:
            raise HTTPException(status_code=400, detail=f"invalid JSON: {exc.msg}") from exc

    return app


app = create_app()

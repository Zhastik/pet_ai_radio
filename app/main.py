import logging
from pathlib import Path

import anyio
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse
from starlette.concurrency import run_in_threadpool

from app.music import STATIONS, Genre, MusicGenerator

logger = logging.getLogger(__name__)
app = FastAPI(title="AI Radio")
generator = MusicGenerator()
generation_slot = anyio.CapacityLimiter(1)


@app.get("/healthz", include_in_schema=False)
async def health():
    return {"status": "ok"}


@app.get("/", include_in_schema=False)
async def player():
    return FileResponse(Path(__file__).with_name("player.html"))


@app.get("/api/genres")
async def genres():
    return [{"id": genre.value, "name": station[0]} for genre, station in STATIONS.items()]


@app.post(
    "/api/genres/{genre}/tracks",
    response_class=Response,
    responses={
        200: {"content": {"audio/wav": {}}},
        503: {"description": "The generator is busy or temporarily unavailable."},
    },
)
async def next_track(genre: Genre, request: Request):
    try:
        generation_slot.acquire_nowait()
    except anyio.WouldBlock:
        raise HTTPException(503, "Генератор занят", headers={"Retry-After": "2"}) from None

    try:
        if await request.is_disconnected():
            return Response(status_code=204)
        audio = await run_in_threadpool(generator.generate, genre)
    except Exception:
        logger.exception("Music generation failed for %s", genre.value)
        raise HTTPException(503, "Не удалось сгенерировать трек") from None
    finally:
        generation_slot.release()

    return Response(audio, media_type="audio/wav", headers={"Cache-Control": "no-store"})

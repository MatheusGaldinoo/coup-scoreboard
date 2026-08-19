from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.routers import tables, players, leaderboard, matches, actions
from app.core.exceptions import GameRuleError

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicialização (se precisarmos de conexões ou setups específicos)
    yield
    # Limpeza

app = FastAPI(title="Coup Scoreboard API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Para desenvolvimento
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(GameRuleError)
async def game_rule_exception_handler(request: Request, exc: GameRuleError):
    return JSONResponse(
        status_code=400,
        content={"detail": exc.message},
    )

@app.get("/health")
async def health_check():
    return {"status": "ok"}

app.include_router(tables.router)
app.include_router(players.router)
app.include_router(leaderboard.router)
app.include_router(matches.router)
app.include_router(actions.router)

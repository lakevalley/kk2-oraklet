from pydantic import BaseModel


# ─── /data/upload ───────────────────────────
class UploadResponse(BaseModel):
    rows: int
    columns: list[str]
    dtypes: dict[str, str]


# ─── /ai/ask ────────────────────────────────
class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    question: str
    answer: str
    model: str
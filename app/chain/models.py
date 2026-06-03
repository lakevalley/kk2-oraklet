from pydantic import BaseModel

# ─── Pydantic-modeller för varje stegs in- och utdata ───────────────────────

class PromptBuilderInput(BaseModel):
    question: str
    stats: str


class PromptBuilderOutput(BaseModel):
    prompt: str


class LLMRunnerOutput(BaseModel):
    raw_answer: str


class ResponseParserOutput(BaseModel):
    question: str
    answer: str
    model: str
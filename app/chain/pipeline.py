from app.chain.steps import PromptBuilder, LLMRunner, ResponseParser, PromptBuilderInput
from app.chain.models import ResponseParserOutput


def build_pipeline(question: str, stats: str, model_name: str) -> ResponseParserOutput:
    """Bygger och kör kedjan för en given fråga och statistik."""

    pipeline = (
        PromptBuilder()
        | LLMRunner()
        | ResponseParser(question=question, model_name=model_name)
    )

    return pipeline.invoke(PromptBuilderInput(question=question, stats=stats))
from app.chain.steps import PromptBuilder, LLMRunner, ResponseParser, PromptBuilderInput


def build_pipeline(question: str, stats: str, model_name: str):
    """Bygger och kör kedjan för en given fråga och statistik."""

    pipeline = (
        PromptBuilder()
        | LLMRunner()
        | ResponseParser(question=question, model_name=model_name)
    )

    return pipeline.invoke(PromptBuilderInput(question=question, stats=stats))
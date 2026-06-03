from app.chain.steps import PromptBuilder, PromptBuilderInput


def test_prompt_builder_contains_question():
    builder = PromptBuilder()
    result = builder.invoke(PromptBuilderInput(question="Vilken stad är varmast?", stats="..."))
    assert "Vilken stad är varmast?" in result.prompt


def test_prompt_builder_contains_stats():
    builder = PromptBuilder()
    result = builder.invoke(PromptBuilderInput(question="?", stats="min: 5, max: 20"))
    assert "min: 5, max: 20" in result.prompt
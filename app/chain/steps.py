from app.chain.runnable import Runnable
from transformers import pipeline as hf_pipeline
from app.chain.models import (
    PromptBuilderInput,
    PromptBuilderOutput,
    LLMRunnerOutput,
    ResponseParserOutput,
)


# ─── Steg 1: Bygger prompten ─────────────────────────────────────────────────

class PromptBuilder(Runnable[PromptBuilderInput, PromptBuilderOutput]):
    name: str = "prompt_builder"

    def invoke(self, data: PromptBuilderInput) -> PromptBuilderOutput:
        prompt = (
            f"Du är en dataanalytiker. Här är statistik om datasetet:\n\n"
            f"{data.stats}\n\n"
            f"Svara på följande fråga baserat på statistiken:\n{data.question}"
        )
        return PromptBuilderOutput(prompt=prompt)

# ─── Steg 2: Anropar LLM-modellen ────────────────────────────────────────────

class LLMRunner(Runnable[PromptBuilderOutput, LLMRunnerOutput]):
    name: str = "llm_runner"

    def invoke(self, data: PromptBuilderOutput) -> LLMRunnerOutput:
        generator = hf_pipeline(
            "text-generation",
            model="HuggingFaceTB/SmolLM2-135M-Instruct"
        )

        result = generator(data.prompt, max_new_tokens=200)
        raw = result[0]["generated_text"]
        print("RAW OUTPUT:", raw)
        return LLMRunnerOutput(raw_answer=raw)


# ─── Steg 3: Tolkar modellens råoutput ───────────────────────────────────────

class ResponseParser(Runnable[LLMRunnerOutput, ResponseParserOutput]):
    name: str = "response_parser"
    question: str
    model_name: str

    def invoke(self, data: LLMRunnerOutput) -> ResponseParserOutput:
        raw = data.raw_answer
        if self.question in raw:
            answer = raw.split(self.question)[-1].strip().split("\n")[0].strip()
        else:
            answer = raw.strip().split("\n")[-1].strip()

        if not answer:
            answer = "Modellen kunde inte generera ett svar."

        return ResponseParserOutput(
            question=self.question,
            answer=answer,
            model=self.model_name,
        )
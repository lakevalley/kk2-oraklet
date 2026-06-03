from app.chain.runnable import Runnable
from transformers import pipeline as hf_pipeline
from app.chain.models import (
    PromptBuilderInput,
    PromptBuilderOutput,
    LLMRunnerOutput,
    ResponseParserOutput,
)
import threading

class ModelError(Exception):
    pass


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
        result_container = []
        error_container = []

        def run_model():
            try:
                generator = hf_pipeline(
                    "text-generation",
                    model="HuggingFaceTB/SmolLM2-135M-Instruct"
                )
                result = generator(data.prompt, max_new_tokens=200)
                result_container.append(result[0]["generated_text"])
            except Exception as e:
                error_container.append(str(e))

        thread = threading.Thread(target=run_model)
        thread.start()
        thread.join(timeout=30)  # 30 sekunder

        if thread.is_alive():
            raise ModelError("Modellen tog för lång tid att svara.")
        if error_container:
            raise ModelError(f"Modellfel: {error_container[0]}")

        return LLMRunnerOutput(raw_answer=result_container[0])


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
# ─────────────────────────────────────────────
#  IMPORTS
# ─────────────────────────────────────────────
from pydantic import BaseModel, ConfigDict, SerializeAsAny  # Typsäkerhet & serialisering
from typing import Any, Callable, Generic, TypeVar          # Verktyg för generics & typer


# ─────────────────────────────────────────────
#  TYPVARIABLER – platshållare för generics
# ─────────────────────────────────────────────
I = TypeVar("I")   # Input-typ
O = TypeVar("O")   # Output-typ
M = TypeVar("M")   # Mellanliggande typ (Middle) – används i RunnableSequence


# ─────────────────────────────────────────────
#  RUNNABLE – basklass för alla pipeline-steg
# ─────────────────────────────────────────────
class Runnable(BaseModel, Generic[I, O]):
    # Ärver från BaseModel (Pydantic) och Generic[I, O] (generics)
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    # Pydantic tillåter normalt inte godtyckliga typer (t.ex. Callable),
    # arbitrary_types_allowed=True stänger av den begränsningen
    
    name: str | None = None  # Valfritt namn på steget, används vid felsökning

    def invoke(self, data: I) -> O:
        # Abstrakt metod – alla subklasser MÅSTE implementera denna
        # Tar emot data av typ I, returnerar data av typ O
        raise NotImplementedError("Subclasses must implement invoke()")

    def __or__(self, other: Any) -> 'RunnableSequence':
        # Definierar vad | gör när ett Runnable-objekt är på VÄNSTER sida
        # t.ex.: SentimentAnalyser() | TicketParser()

        if isinstance(other, Runnable):
            # Om höger sida är ett Runnable – koppla ihop direkt
            return RunnableSequence.model_construct(
                first=self,
                second=other,
            )

        if callable(other):
            # Om höger sida är en vanlig funktion – wrappa den i RunnableLambda först
            return RunnableSequence.model_construct(
                first=self,
                second=RunnableLambda.model_construct(func=other, name=other.__name__),
                name=other.__name__,
            )

        return NotImplemented  # Python provar då __ror__ på other istället

    def __ror__(self, other: Any) -> Any:
        # Definierar vad | gör när ett Runnable-objekt är på HÖGER sida
        # Används när en vanlig funktion är på VÄNSTER sida
        # t.ex.: min_funktion | TicketParser()

        if callable(other):
            return RunnableSequence.model_construct(
                first=RunnableLambda.model_construct(func=other),
                second=self,
                name=other.__name__,
            )

        return NotImplemented


# ─────────────────────────────────────────────
#  RUNNABLELAMBDA – wrapper för vanliga funktioner
# ─────────────────────────────────────────────
class RunnableLambda(Runnable[I, O]):
    # Gör en vanlig funktion till ett Runnable-objekt
    # så att den kan användas i en pipeline med |

    func: Callable[[I], O]  # Håller referensen till den inlindade funktionen

    def invoke(self, data: I) -> O:
        # Anropar bara den sparade funktionen med inkommande data
        return self.func(data)


# ─────────────────────────────────────────────
#  RUNNABLESEQUENCE – kedjar ihop två steg
# ─────────────────────────────────────────────
class RunnableSequence(Runnable[I, O], Generic[I, M, O]):
    # Håller ihop två steg: first och second
    # Output från first måste matcha input till second (därav M som länk)

    first: SerializeAsAny[Runnable[I, M]]   # Första steget:  I → M
    second: SerializeAsAny[Runnable[M, O]]  # Andra steget:   M → O
    # SerializeAsAny behövs för att Pydantic ska serialisera subklasser korrekt

    def invoke(self, data: I) -> O:
        # Kör first med data, skickar resultatet vidare till second
        return self.second.invoke(self.first.invoke(data))

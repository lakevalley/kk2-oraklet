Installationsinstruktioner

1. Klona repot
2. Kör `uv sync` för att installera alla beroenden från `pyproject.toml`
3. Starta servern med `uv run uvicorn app.main:app --reload`

Vid start läses en default csv-fil in, ladda gärna upp en egen.

## Exempelanrop

### Ladda upp ett dataset
```bash
curl -X POST http://127.0.0.1:8000/data/upload -F "file=@testdata.csv"
```

### Visa statistik
```bash
curl http://127.0.0.1:8000/data/stats
```

### Ställ en fråga
```bash
curl -X POST http://127.0.0.1:8000/ai/ask -H "Content-Type: application/json" -d "{\"question\": \"Which city has the highest temperature?\"}"
```

Eller använd Swagger på `http://127.0.0.1:8000/docs`.
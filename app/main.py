from fastapi import FastAPI, UploadFile, HTTPException
import pandas as pd
import io
from app.data import save_dataset, get_dataset
from app.schemas import UploadResponse, AskRequest, AskResponse
from app.chain.pipeline import build_pipeline
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Oraklet")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/data/upload")
def upload_data(file: UploadFile):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Filen måste vara en CSV")
    
    contents = file.file.read()

    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="Filen är tom")
    
    if len(contents) > 5 * 1024 * 1024:  # 5 MB
        raise HTTPException(status_code=400, detail="Filen är för stor, max 5 MB")

    try:
        df = pd.read_csv(io.BytesIO(contents), encoding="utf-8", encoding_errors="strict")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Filen har fel teckenkodning, använd UTF-8")
    except Exception:
        raise HTTPException(status_code=400, detail="Filen kunde inte läsas som CSV")

    save_dataset(df)
    logger.info(f"Dataset uppladdat: {len(df)} rader, {len(df.columns)} kolumner")    

    return UploadResponse(
        rows=len(df),
        columns=df.columns.tolist(),
        dtypes={col: str(dtype) for col, dtype in df.dtypes.items()}
    )


@app.get("/data/stats")
def get_stats():
    df = get_dataset()
    
    if df is None:
        raise HTTPException(status_code=404, detail="Inget dataset uppladdat")
    
    return df.describe().to_dict()


from app.chain.steps import ModelError

@app.post("/ai/ask")
def ask(request: AskRequest):
    df = get_dataset()
    
    if df is None:
        raise HTTPException(status_code=400, detail="Inget dataset uppladdat")
    
    logger.info(f"Fråga mottagen: {request.question}")
    
    stats = df.to_string() + "\n\n" + df.describe().to_string()
    
    try:
        result = build_pipeline(
            question=request.question,
            stats=stats,
            model_name="HuggingFaceTB/SmolLM2-135M-Instruct"
        )
    except ModelError as e:
        logger.error(f"Modellfel: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
    return AskResponse(
        question=result.question,
        answer=result.answer,
        model=result.model
    )
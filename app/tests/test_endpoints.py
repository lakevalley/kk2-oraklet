from fastapi.testclient import TestClient
from app.main import app
import app.data as data_module
from app.chain.models import ResponseParserOutput

def setup_function():
    data_module.current_df = None

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_stats_without_dataset_returns_404():
    response = client.get("/data/stats")
    assert response.status_code == 404
    
def test_upload_valid_csv():
    csv_content = b"city,temp_c\nMalmo,8.3\nStockholm,6.6\n"
    response = client.post(
        "/data/upload",
        files={"file": ("testdata.csv", csv_content, "text/csv")}
    )
    assert response.status_code == 200
    assert response.json()["rows"] == 2
    assert "city" in response.json()["columns"]

def test_ask_returns_answer(monkeypatch):
    # Laddar upp ett dataset först
    csv_content = b"city,temp_c\nMalmo,8.3\nStockholm,6.6\n"
    client.post(
        "/data/upload",
        files={"file": ("testdata.csv", csv_content, "text/csv")}
    )
    
    # Mocka build_pipeline så vi slipper köra modellen
    def mock_pipeline(question, stats, model_name):
        return ResponseParserOutput(
            question=question,
            answer="Malmo",
            model=model_name
        )
    
    monkeypatch.setattr("app.main.build_pipeline", mock_pipeline)
    
    response = client.post(
        "/ai/ask",
        json={"question": "Which city has the highest temperature?"}
    )
    
    assert response.status_code == 200
    assert response.json()["answer"] == "Malmo"
    assert response.json()["question"] == "Which city has the highest temperature?"
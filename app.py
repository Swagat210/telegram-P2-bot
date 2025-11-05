from uvicorn import run
from src.main import app   # adjust import to your app object

if __name__ == "__main__":
    run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))

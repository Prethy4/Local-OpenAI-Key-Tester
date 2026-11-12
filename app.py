import uvicorn
from api.index import app

if __name__ == "__main__":
    print("\n" + "=" * 50)
    print(" OpenAI Key Credit Tester Web App")
    print(" Running on: http://localhost:8000")
    print("=" * 50 + "\n")
    uvicorn.run("api.index:app", host="127.0.0.1", port=8000, reload=False)

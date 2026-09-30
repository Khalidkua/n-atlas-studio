from fastapi import FastAPI

app = FastAPI(
    title="N-ATLAS Studio",
    description="Developer and evaluation platform for N-ATLaS",
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "name": "N-ATLAS Studio",
        "version": "0.1.0",
        "status": "running",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model": "N-ATLaS",
    }

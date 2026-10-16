from fastapi import FastAPI
from fastapi.responses import FileResponse

from backend.api.content import router

app = FastAPI(title="Rượu Thời Đại AI Content Factory")
app.include_router(router)


@app.get("/")
def index():
    import os
    return FileResponse(os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html"))

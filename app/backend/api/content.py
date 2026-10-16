from typing import Optional

from fastapi import APIRouter, File, Form, UploadFile

from backend.agents import pipeline, rag

router = APIRouter(prefix="/api")


@router.post("/ingest")
def ingest():
    return {"chunks": rag.ingest()}


@router.post("/content")
async def content(
    image: Optional[UploadFile] = File(None),
    product_name: Optional[str] = Form(None),
    n: int = Form(3),
):
    data = await image.read() if image else None
    return pipeline.run(data, product_name, max(1, min(n, 5)))

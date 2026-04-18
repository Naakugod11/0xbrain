from fastapi import APIRouter, HTTPException, UploadFile, File
from core.models import(
    IngestResponse, QueryRequest, QueryResponse, DocumentInfo
)
from services.chunking import chunk_text
from services.vector_store import add_chunks, list_documents
from services.query import ask
from pypdf import PdfReader
import io

router = APIRouter(tags=["0xbrain"])

@router.post("/ingest", response_model=IngestResponse)
async def ingest_pdf(
    file: UploadFile = File(...),
    title: str = "untitled",
    category: str = "general",
):
    """Upload a PDF and add it to the knowledge base."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files supported")
    
    try:
        # Read PDF content
        content = await file.read()
        reader = PdfReader(io.BytesIO(content))
        text = "\n".join([
            page.extract_text() or "" for page in reader.pages
        ])

        if not text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from PDF")
        
        # Chunk and store
        chunks = chunk_text(text, source=file.filename)
        add_chunks(chunks, title=title, category=category)

        return IngestResponse(
            title=title,
            chunks_created=len(chunks),
            status="ingested",
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")
    
@router.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """Ask a question - 0xbrain finds the answer in the knowledge base."""
    try:
        return ask(
            question=request.question,
            top_k=request.top_k,
            category_filter=request.category_filter,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")
    
@router.get("/documents", response_model=list[DocumentInfo])
async def documents():
    """List all documents in the knowledge base."""
    docs = list_documents()
    return [DocumentInfo(**doc) for doc in docs]

@router.post("/ingest/batch")
async def batch_ingest():
    """Trigger batch ingestion of all whitepapers."""
    try:
        from ingestion.batch_ingest import run
        run()
        return {"status": "complete", "documents": list_documents()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

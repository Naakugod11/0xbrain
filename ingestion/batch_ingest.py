"""
Batch ingestion script for 0xbrain knowledge base.
Downloads and ingests crypto whitepapers and protocol documentation.
 
Usage: python -m ingestion.batch_ingest
"""
 
import os
import httpx
import time
from pypdf import PdfReader
import io
from services.chunking import chunk_text
from services.vector_store import add_chunks
 
# All sources to ingest
# Format: (url, title, category)
SOURCES = [
    # === Core Protocols ===
    (
        "https://bitcoin.org/bitcoin.pdf",
        "Bitcoin Whitepaper",
        "btc",
    ),
    (
        "https://ethereum.org/content/whitepaper/whitepaper-pdf/Ethereum_Whitepaper_-_Buterin_2014.pdf",
        "Ethereum Whitepaper",
        "eth",
    ),

    # === DeFi Protocols ===
    (
        "https://uniswap.org/whitepaper.pdf",
        "Uniswap V2 Whitepaper",
        "defi",
    ),
    (
        "https://uniswap.org/whitepaper-v3.pdf",
        "Uniswap V3 Whitepaper",
        "defi",
    ),
    (
        "https://raw.githubusercontent.com/aave/aave-v3-core/master/techpaper/Aave_V3_Technical_Paper.pdf",
        "Aave V3 Technical Paper",
        "defi",
    ),
    (
        "https://compound.finance/documents/Compound.Whitepaper.pdf",
        "Compound Whitepaper",
        "defi",
    ),

    # === Oracles ===
    (
        "https://research.chain.link/whitepaper-v2.pdf",
        "Chainlink 2.0 Whitepaper",
        "oracle",
    ),

    # === Liquid Staking ===
    (
        "https://lido.fi/static/Lido:Ethereum-Liquid-Staking.pdf",
        "Lido Liquid Staking",
        "staking",
    ),
    (
        "https://docs.lido.fi/Lido_V3_Whitepaper.pdf",
        "Lido V3 Whitepaper",
        "staking",
    ),
]
 
def download_pdf(url: str) -> bytes | None:
    """Download a PDF from URL. Returns bytes or None on failure."""
    try:
        # Some URLs are HTML pages, not direct PDFs
        response = httpx.get(url, follow_redirects=True, timeout=30)
        if response.status_code == 200:
            content_type = response.headers.get("content-type", "")
            if "pdf" in content_type or url.endswith(".pdf"):
                return response.content
            else:
                print(f"  ⚠ Not a PDF ({content_type}), skipping")
                return None
        else:
            print(f"  ⚠ HTTP {response.status_code}, skipping")
            return None
    except Exception as e:
        print(f"  ⚠ Download failed: {e}")
        return None
 
 
def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract text from PDF bytes."""
    reader = PdfReader(io.BytesIO(pdf_bytes))
    text = "\n".join([
        page.extract_text() or "" for page in reader.pages
    ])
    return text
 
 
def ingest_source(url: str, title: str, category: str) -> bool:
    """Download, chunk, and ingest a single source."""
    print(f"\n📥 Ingesting: {title}")
    print(f"   URL: {url}")
 
    # Download
    pdf_bytes = download_pdf(url)
    if not pdf_bytes:
        return False
 
    # Extract text
    text = extract_text_from_pdf(pdf_bytes)
    if not text.strip():
        print(f"  ⚠ No text extracted, skipping")
        return False
 
    # Chunk
    chunks = chunk_text(text, source=url)
    print(f"   📄 Extracted {len(chunks)} chunks")
 
    # Store in vector DB
    add_chunks(chunks, title=title, category=category)
    print(f"   ✅ Stored in knowledge base")
 
    return True
 
 
def run():
    """Run batch ingestion of all sources."""
    print("=" * 60)
    print("🧠 0xbrain — Batch Ingestion")
    print("=" * 60)
 
    success = 0
    failed = 0
 
    for url, title, category in SOURCES:
        try:
            if ingest_source(url, title, category):
                success += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  ❌ Error: {e}")
            failed += 1
 
        # Be nice to servers
        time.sleep(1)
 
    print("\n" + "=" * 60)
    print(f"🧠 Ingestion complete: {success} success, {failed} failed")
    print("=" * 60)
 
 
if __name__ == "__main__":
    run()

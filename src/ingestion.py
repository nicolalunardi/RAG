from utils import ingestion_pipeline
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    docs_dir = os.path.join(BASE_DIR, "docs")
    pdf_files = [os.path.join(docs_dir, f) for f in os.listdir(docs_dir) if f.endswith(".pdf")]
    ingestion_pipeline(pdf_files)
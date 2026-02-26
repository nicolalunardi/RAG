from utils import ingestion_pipeline
import os

if __name__ == "__main__":
    pdf_files = [f"docs/{file}" for file in os.listdir("docs") if file.endswith(".pdf")]
    ingestion_pipeline(pdf_files)
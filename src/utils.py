from unstructured.partition.pdf import partition_pdf
from unstructured.chunking.title import chunk_by_title

def partition_pdf(file_path: str):
    elements = partition_pdf(
        filename=file_path,
        strategy="hi_res",
        infer_table_structure=True,
        extract_image_block_types=["Image"],
        extract_image_block_to_payload=True,
    )
    return elements

def chunk_by_title(elements):
    chunks = chunk_by_title(
        elements=elements, 
        max_characters=3000, 
        combine_under_n_chars=500
    )
    return chunks

    
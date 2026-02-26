from unstructured.partition.pdf import partition_pdf
from unstructured.chunking.title import chunk_by_title
from langchain_openai import ChatOpenAI
from typing import List
import json
from langchain.schema import Document, HumanMessage, SystemMessage

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

def separate_content_types(chunk):
    content_data = {
        'text': chunk.text,
        'tables': [],
        'images': [],
    }
    
    # Check for tables and images in original elements
    if hasattr(chunk, 'metadata') and hasattr(chunk.metadata, 'orig_elements'):
        for element in chunk.metadata.orig_elements:
            element_type = type(element).__name__
            
            # Handle tables
            if element_type == 'Table':
                table_html = getattr(element.metadata, 'text_as_html', element.text)
                content_data['tables'].append(table_html)
            
            # Handle images
            elif element_type == 'Image':
                if hasattr(element, 'metadata') and hasattr(element.metadata, 'image_base64'):
                    content_data['images'].append(element.metadata.image_base64)
    
    return content_data

def create_summary(text: str, tables: List[str], images: List[str]) -> str:
    
    try:
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        
        system = SystemMessage(content="""YOUR TASK:
            Generate a comprehensive, searchable description that covers:

            1. Key facts, numbers, and data points from text and tables
            2. Main topics and concepts discussed  
            3. Questions this content could answer
            4. Visual content analysis (charts, diagrams, patterns in images)
            5. Alternative search terms users might use

            Make it detailed and searchable - prioritize findability over brevity.

            SEARCHABLE DESCRIPTION:""")

        prompt_text = f"""You are creating a searchable description for document content retrieval.

        CONTENT TO ANALYZE:
        TEXT CONTENT:
        {text}
        """
        if tables:
            prompt_text += "TABLES:\n"
            for i, table in enumerate(tables):
                prompt_text += f"Table {i+1}:\n{table}\n\n"

        message_content = [{"type": "text", "text": prompt_text}]

        for image_base64 in images:
            message_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
            })
        
        message = HumanMessage(content=message_content)
        response = llm.invoke([system, message])  
        
        return response.content
    except Exception as e:
        print(f"Error creating summary: {str(e)}")
        return text


def create_summarized_documents(chunks: List[Chunk]):

    langchain_docs = []
     
    for chunk in chunks:
        
        content_data = separate_content_types(chunk)
        
        if content_data['tables'] or content_data['images']:
            enhanced_content = create_ai_enhanced_summary(
                content_data['text'],
                content_data['tables'],
                content_data['images']
            )
        else:
            enhanced_content = content_data['text']

        doc = Document(
            page_content=enhanced_content,
            metadata = {
                "original_content": json.dumps({
                    "raw_text": content_data['text'],
                    "tables_html": content_data['tables'],
                    "images_base64": content_data['images']
                })
            }
        )
        langchain_docs.append(doc)
    
    return langchain_docs

def create_vector_db(docs: List[Document], db_path: str = "db/chroma_db"):

    embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")

    vector_db = Chroma.from_documents(
        docs, 
        embedding=embedding_model,
        persist_directory=db_path, 
        collection_metadata={"hnsw:space": "cosine"})
    
    return vector_db
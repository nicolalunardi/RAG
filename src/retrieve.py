from utils import retrieve_documents, generate_response

if __name__ == "__main__":
    query = input("Enter your query: ")
    retrieved_docs = retrieve_documents(query, k=5, verbose=True)
    response = generate_response(query, retrieved_docs)
    print(f"\nAnswer:\n{response}")

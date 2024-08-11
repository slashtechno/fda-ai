from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from langchain_community.embeddings.ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from pathlib import Path
CHROMA_PATH = "chroma"
DATA_PATH = "data"


def load_documents():
    document_loader = PyPDFDirectoryLoader(DATA_PATH)
    return document_loader.load()


def split_documents(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        # Each chunk wiill be n characters long
        # Originally 800
        chunk_size=2000,
        # Each chunk will overlap with the previous by n characters
        # Originally 80
        chunk_overlap=200,
        # The function used to calculate the length of the text
        length_function=len,
        # Don't treat the default (`self._separators = separators or ["\n\n", "\n", " ", ""]`) as regex
        is_separator_regex=False,
    )
    return text_splitter.split_documents(documents)


def get_embedding_function():
    # https://ollama.com/library/nomic-embed-text
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    return embeddings


def add_to_chroma(chunks: list[Document]):
    # db = Chroma.from_documents(
    #         new_chunks,
    #         embedding=get_embedding_function(),
    #         persist_directory=CHROMA_PATH,
    #     )
    db = Chroma(
        persist_directory=CHROMA_PATH, embedding_function=get_embedding_function()
    )

    chunks_with_ids = calculate_chunk_ids(chunks)

    # IDs are always included
    existing_ids = db.get(include=[])
    # Sets are faster for lookups since it's a hash table, it seems
    existing_ids = set(existing_ids["ids"])

    # Only add documents that are not already in the database
    new_chunks = []
    for chunk in chunks_with_ids:
        if chunk.metadata["id"] not in existing_ids:
            new_chunks.append(chunk)

    if len(new_chunks):
        # print(f"Existing: {existing_ids}")
        print(f"Adding new documents {len(new_chunks)}")
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        db.add_documents(new_chunks, ids=new_chunk_ids)
    else:
        print("No new documents to add")


def calculate_chunk_ids(chunks: list[Document]):
    last_page_id = None
    current_chunk_index = 0
    for chunk in chunks:
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page")
        current_page_id = f"{source}:{page}"
        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0

        chunk_id = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id
        chunk.metadata["id"] = chunk_id
    return chunks


def main():
    documents = load_documents()
    chunks = split_documents(documents)
    # print(chunks[0])
    add_to_chroma(chunks)

def remove_chunks_by_filename(filename: str):
    # Normalize the filename to use the correct path separator
    normalized_filename = Path(filename).resolve()
    
    db = Chroma(
        persist_directory=CHROMA_PATH, embedding_function=get_embedding_function()
    )

    # Generate IDs for the chunks of the specified file
    existing_ids = db.get(include=[])
    existing_ids = set(existing_ids["ids"])

    ids_to_remove = []
    for doc_id in existing_ids:
        # Extract the path part of the doc_id
        doc_id_path = Path(doc_id.split(':')[0]).resolve()
        if doc_id_path == normalized_filename:
            ids_to_remove.append(doc_id)

    if ids_to_remove:
        db.delete(ids=ids_to_remove)
        print(f"Removed {len(ids_to_remove)} chunks from file {filename}.")
    else:
        print(f"No chunks found for file {filename}.")

if __name__ == "__main__":
    main()

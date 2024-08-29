from langchain_community.document_loaders import PyPDFDirectoryLoader
from unstructured.partition.pdf import partition_pdf
from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema.document import Document as DocumentSchema
from langchain_core.documents import Document
from langchain_community.embeddings.ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from pathlib import Path
from unstructured.chunking.title import chunk_by_title

from langchain_community.vectorstores.utils import filter_complex_metadata
CHROMA_PATH = "chroma"
DATA_PATH = "data"

skip = ["210951Orig1s000MultidisciplineR.pdf"]

# https://python.langchain.com/v0.2/docs/integrations/providers/unstructured/
# https://python.langchain.com/v0.2/docs/integrations/document_loaders/unstructured_file/
# https://docs.unstructured.io/open-source/core-functionality/chunking
def load_documents():
    # return UnstructuredLoader(file_path=files, chunking_strategy="by_title", max_characters=2200, new_after_n_chars=1000, overlap=300).load()
    docs = []
    for file in Path(DATA_PATH).rglob("*.pdf"):
        if file.name in skip:
            continue
        print(f"Loading {file}")
        # doc_loader = UnstructuredPDFLoader(file_path=file, mode="single", infer_table_structure=True,  strategy="hi_res", show_progress_bar=True) 
        # docs.extend(doc_loader.load())
        docs.extend(partition_pdf(filename=file, infer_table_structure=True,  strategy="hi_res", show_progress_bar=True))
    return docs

    # document_loader = PyPDFDirectoryLoader(DATA_PATH)
    # return document_loader.load()


def split_documents(documents: list[DocumentSchema]):
    text_splitter = RecursiveCharacterTextSplitter(
        # Don't split by any separators
        separators=[],
        # Each chunk wiill be n characters long
        # Originally 800
        chunk_size=2000,
        # Each chunk will overlap with the previous by n characters
        # Originally 80
        chunk_overlap=80,
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


def add_to_chroma(chunks: list[DocumentSchema]):
    # db = Chroma.from_documents(
    #         new_chunks,
    #         embedding=get_embedding_function(),
    #         persist_directory=CHROMA_PATH,
    #     )
    db = Chroma(
        persist_directory=CHROMA_PATH, embedding_function=get_embedding_function()
    )

    # TODO: Edit calculate_chunk_ids to use metadata from Unstructured
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
        total_chunks = len(new_chunks)
        for index, (chunk, chunk_id) in enumerate(zip(new_chunks, new_chunk_ids), start=1):
            no_complex_metadata = filter_complex_metadata([chunk])
            db.add_documents(no_complex_metadata, ids=[chunk_id])
            print(f"Added chunk {index}/{total_chunks} with id {chunk_id}")
    else:
        print("No new documents to add")


def calculate_chunk_ids(chunks: list[DocumentSchema]):
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


def chunk_pdf(documents: list[DocumentSchema]):
    # https://colab.research.google.com/drive/1ieDJ4LoxARrHFqxXWif8Lv8e8aZTgmtH#scrollTo=f5a68771a12d16e6
    chunked_elements = chunk_by_title(documents, max_characters=3000, new_after_n_chars=2000, overlap=300)
    documents = []
    for element in chunked_elements:
        metadata = element.metadata.to_dict()
        documents.append(
            Document(
                page_content=element.text,
                metadata=metadata,
            )
        )
    return documents    


def main():
    documents = load_documents()
    chunks = chunk_pdf(documents)
    # chunks = documents # Unstructured can split the documents at load time
    # chunks = split_documents(documents)
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
        doc_id_path = Path(doc_id.split(":")[0]).resolve()
        if doc_id_path == normalized_filename:
            ids_to_remove.append(doc_id)

    if ids_to_remove:
        db.delete(ids=ids_to_remove)
        print(f"Removed {len(ids_to_remove)} chunks from file {filename}.")
    else:
        print(f"No chunks found for file {filename}.")


if __name__ == "__main__":
    main()

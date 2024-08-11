from langchain.prompts import ChatPromptTemplate
from langchain_chroma import Chroma
from rag_testing.load import get_embedding_function, CHROMA_PATH
from langchain_community.llms.ollama import Ollama

PROMPT_TEMPLATE = """Answer the following question based only on the following context:
{context}

---
Answer the question based on the above context. Only provide verbatim. Answer the question fully and use the information from the context: {question}
"""

def query_rag(query_text: str): 
    embedding_function = get_embedding_function()
    db = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embedding_function,
    )

    # `k` is the number of results to return 5/4 default?
    # results = db.similarity_search_with_score(query_text, k=5)
    results = db.similarity_search_with_score(query_text, k=20)
    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)
    print(prompt)
    print("\n\n-------\n")
    model = Ollama(model="llama3.1:8b")
    # model = Ollama(model="gemma2:27b-instruct-q5_K_M")
    response_text = model.invoke(prompt)
    sources = [doc.metadata.get("id", None) for doc, _score in results]
    formatted_response = f"Response: {response_text}\nSources: {sources}"
    print(formatted_response)
    return response_text

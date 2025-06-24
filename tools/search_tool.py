from tools.llm_interface import query_llm

def perform_search(query: str) -> str:
    prompt = f"""
    Act like a real-time travel search assistant.

    Simulate searching for: "{query}".
    Provide useful, factual information as if pulled from the web.
    Be concise and informative. Don't make up data; clearly indicate if unsure.
    """
    return query_llm(prompt)
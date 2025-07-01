from google.adk.tools.tool_context import ToolContext
from tools.llm_interface import query_llm

async def perform_search(tool_context: ToolContext, query: str):
    prompt = f"""
    You are a search help assistant helping with accommodation/travel/sightseeing related queries.

    Simulate a search for: "{query}".
    Return useful, factual-like results for a user (e.g., hotels in Paris, train names from A to B, best places in Delhi to visit, etc.).
    If information can't be retrieved, say so.
    """
    result = await query_llm(prompt)
    return {"output": result}
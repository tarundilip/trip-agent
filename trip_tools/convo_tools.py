from google.adk.tools.tool_context import ToolContext
from tools.search_tool import perform_search

async def handle_convo(query: str, tool_context: ToolContext) -> dict:
    """
    Handle general knowledge queries using Google Search.
    Store the result back for access by the calling agent.
    """
    if not query or query.strip() == "":
        return {
            "action": "handle_convo",
            "status": "error",
            "message": "Please provide a valid query."
        }

    print(f"Running simulated travel search for query: {query}")
    result = await perform_search(tool_context, query)

    tool_context.state["conversation_result"] = result["output"]

    return {
        "action": "handle_convo",
        "status": "success",
        "message": "Search result retrieved.",
        "result": result["output"]
    }
from google.adk.tools.tool_context import ToolContext
from tools.search_tool import perform_search

async def search_and_store(query: str, tool_context: ToolContext) -> dict:
    if not query or query.strip() == "":
        return {
            "action": "search_and_store",
            "status": "error",
            "message": "Please provide a valid query to search."
        }

    result = await perform_search(tool_context, query)

    tool_context.state["conversation_result"] = result["output"]

    return {
        "action": "search_and_store",
        "status": "success",
        "message": f"Here’s what I found based on your query:\n\n{result['output']}",
        "result": result["output"]
    }
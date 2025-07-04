from google.adk.agents import Agent
from google.adk.tools import google_search
from google.adk.tools.tool_context import ToolContext
from tools.llm_interface import query_llm  

search_agent = Agent(
    name="search_agent",
    model="gemini-2.0-flash",
    description="Search agent using google_search tool for real-time info",
    instruction="Use the 'google_search' tool only to find real-time info about hotels, travel, or sightseeing.",
    tools=[google_search]
)

async def perform_search(tool_context: ToolContext, query: str):
    try:
        result = await search_agent.run(input=query, tool_context=tool_context)
        return {"output": result}
    except Exception as e:
        print(f"[Search Tool] Failed: {e}. Falling back to LLM...")
        llm_result = await query_llm(f"Try to simulate a helpful web result for: {query}")
        return {"output": f"[Fallback] {llm_result}"}
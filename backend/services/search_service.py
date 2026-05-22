from langchain_community.tools.tavily_search import TavilySearchResults
from config import TAVILY_API_KEY
import os

os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY

search_tool = TavilySearchResults(
    max_results=5,
    search_depth="advanced",
    include_answer=True
)

def search_web(topic: str) -> str:
    try:
        results = search_tool.invoke(
            f"college lab worksheet {topic} theory algorithm python code"
        )

        combined = ""
        for result in results:
            title = result.get("title", "")
            content = result.get("content", "")
            combined += f"\n\nSource: {title}\n{content}"

        return combined.strip()

    except Exception as e:
        return f"Web search failed: {str(e)}"
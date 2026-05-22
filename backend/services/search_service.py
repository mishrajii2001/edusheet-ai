from tavily import TavilyClient
from config import TAVILY_API_KEY

client = TavilyClient(api_key=TAVILY_API_KEY)

def search_web(topic: str) -> str:
    try:
        response = client.search(
            query=f"college lab worksheet {topic} theory algorithm",
            max_results=5,
            search_depth="advanced"
        )

        results = response.get("results", [])

        combined_content = ""
        for result in results:
            title = result.get("title", "")
            content = result.get("content", "")
            combined_content += f"\n\nSource: {title}\n{content}"

        return combined_content.strip()

    except Exception as e:
        return f"Web search failed: {str(e)}"
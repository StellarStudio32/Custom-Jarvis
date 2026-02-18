"""
Web Search Action Module
Searches the web and summarizes results using DuckDuckGo.
"""

import requests


def web_search(query: str) -> str:
    """
    Search the web using DuckDuckGo and return a summary.
    Summarizes result to 1-2 sentences.
    
    Args:
        query: Search query string
        
    Returns:
        Summary of search result (1-2 sentences)
    """
    try:
        # DuckDuckGo API endpoint
        url = "https://api.duckduckgo.com"
        params = {
            "q": query,
            "format": "json",
            "no_redirect": 1
        }
        
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        # Extract summary (Abstract) or first result
        if data.get("AbstractText"):
            result = data["AbstractText"]
        elif data.get("Results") and len(data["Results"]) > 0:
            result = data["Results"][0].get("Text", "No summary available")
        else:
            result = "No results found"
        
        # Truncate to 1-2 sentences (roughly 200 chars)
        if len(result) > 200:
            result = result[:200].rsplit(" ", 1)[0] + "..."
        
        return result
    except Exception as e:
        print(f"Error during web search: {e}")
        return f"Search failed: {str(e)}"

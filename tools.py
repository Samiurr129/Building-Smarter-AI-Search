"""Tools the research agent can call, plus plain functions used by the fallback mode."""
from datetime import datetime
from pathlib import Path

from langchain_community.tools import DuckDuckGoSearchRun, WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_core.tools import Tool

OUTPUT_FILE = Path("research_output.txt")


def save_to_txt(data: str, filename: Path = OUTPUT_FILE) -> str:
    """Append a timestamped research note to a text file."""
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"--- Research output ({stamp}) ---\n{data}\n\n"
    with open(filename, "a", encoding="utf-8") as f:
        f.write(entry)
    return f"Saved to {filename}"


search_tool = Tool(
    name="web_search",
    func=DuckDuckGoSearchRun().run,
    description="Search the web for current information. Input: a search query.",
)

wiki_tool = WikipediaQueryRun(
    api_wrapper=WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=1000)
)

save_tool = Tool(
    name="save_text_to_file",
    func=save_to_txt,
    description="Save the final research summary to a text file. Input: the text to save.",
)

TOOLS = [search_tool, wiki_tool, save_tool]

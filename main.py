"""Resilient research assistant.

With ANTHROPIC_API_KEY set: a LangChain tool-calling agent (Claude) searches the web and
Wikipedia, then returns a structured summary with sources.
Without a key: a fallback menu still lets you research, using DuckDuckGo results in the
terminal or opening Google or Wikipedia in your browser.
"""
import logging
import os
import urllib.parse
import webbrowser

from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
log = logging.getLogger("ai-search")

DEFAULT_MODEL = "claude-sonnet-5-5"


class ResearchResponse(BaseModel):
    topic: str
    summary: str
    sources: list[str] = Field(default_factory=list)
    tools_used: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------- AI mode
def build_agent():
    """Create the Claude tool-calling agent. Imported lazily so fallback mode needs no key."""
    from langchain.agents import AgentExecutor, create_tool_calling_agent
    from langchain_anthropic import ChatAnthropic
    from langchain_core.output_parsers import PydanticOutputParser
    from langchain_core.prompts import ChatPromptTemplate

    from tools import TOOLS

    llm = ChatAnthropic(model=os.getenv("ANTHROPIC_MODEL", DEFAULT_MODEL), temperature=0)
    parser = PydanticOutputParser(pydantic_object=ResearchResponse)
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are a research assistant. Use the tools to answer the user's query, "
         "then reply only in this format, with no other text:\n{format_instructions}"),
        ("placeholder", "{chat_history}"),
        ("human", "{query}"),
        ("placeholder", "{agent_scratchpad}"),
    ]).partial(format_instructions=parser.get_format_instructions())

    agent = create_tool_calling_agent(llm=llm, prompt=prompt, tools=TOOLS)
    return AgentExecutor(agent=agent, tools=TOOLS, verbose=False), parser


def output_text(raw) -> str:
    """Claude can return a list of content blocks; join their text."""
    if isinstance(raw, list):
        return "".join(b.get("text", "") if isinstance(b, dict) else str(b) for b in raw)
    return str(raw)


def ai_mode() -> None:
    executor, parser = build_agent()
    while True:
        query = input("\nWhat can I help you research? (type 'exit' to quit): ").strip()
        if query.lower() == "exit":
            break
        if not query:
            continue
        try:
            raw = executor.invoke({"query": query})
            result = parser.parse(output_text(raw.get("output")))
            print(f"\nTopic: {result.topic}\n\n{result.summary}\n")
            if result.sources:
                print("Sources:\n" + "\n".join(f"- {s}" for s in result.sources))
        except Exception as exc:  # network, API or parsing errors
            log.error("AI search failed: %s", exc)
            print("The AI search failed. Switching to the fallback menu for this query.")
            fallback_once(query)


# ---------------------------------------------------------------- fallback mode
def open_google(query: str) -> None:
    url = "https://www.google.com/search?q=" + urllib.parse.quote_plus(query)
    webbrowser.open(url)
    print(f"Opened in your browser: {url}")


def open_wikipedia(query: str) -> None:
    url = "https://en.wikipedia.org/w/index.php?search=" + urllib.parse.quote_plus(query)
    webbrowser.open(url)
    print(f"Opened in your browser: {url}")


def duckduckgo_in_terminal(query: str, n: int = 5) -> None:
    from ddgs import DDGS

    results = DDGS().text(query, max_results=n)
    if not results:
        print("No results found.")
    for i, r in enumerate(results, 1):
        print(f"\n{i}. {r['title']}\n   {r['href']}\n   {r['body']}")


FALLBACKS = {"1": ("DuckDuckGo results in this terminal", duckduckgo_in_terminal),
             "2": ("Google in your browser", open_google),
             "3": ("Wikipedia in your browser", open_wikipedia)}


def fallback_once(query: str) -> None:
    for key, (label, _) in FALLBACKS.items():
        print(f"  {key}. {label}")
    choice = input("Choose a search method: ").strip()
    if choice not in FALLBACKS:
        log.warning("Invalid choice. Please select 1, 2 or 3.")
        return
    try:
        FALLBACKS[choice][1](query)
    except Exception as exc:
        log.error("Search failed: %s", exc)


def fallback_mode() -> None:
    while True:
        query = input("\nWhat can I help you research? (type 'exit' to quit): ").strip()
        if query.lower() == "exit":
            break
        if query:
            fallback_once(query)


def main() -> None:
    if os.getenv("ANTHROPIC_API_KEY"):
        log.info("ANTHROPIC_API_KEY found. Starting AI research mode.")
        ai_mode()
    else:
        log.warning("ANTHROPIC_API_KEY is not set. Starting fallback search mode.")
        fallback_mode()
    log.info("Goodbye!")


if __name__ == "__main__":
    main()

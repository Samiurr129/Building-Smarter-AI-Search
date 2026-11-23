# Building smarter AI search

A command-line research assistant that keeps working when the AI service doesn't.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-0.3-1c3c3c)
![Licence](https://img.shields.io/badge/licence-MIT-green)

## How it works

**AI mode** (when `ANTHROPIC_API_KEY` is set)

- A LangChain tool-calling agent, powered by Anthropic Claude, answers your query.
- It can call three tools: DuckDuckGo web search, Wikipedia, and a tool that saves the summary to `research_output.txt`.
- The answer is parsed into a Pydantic model (`topic`, `summary`, `sources`, `tools_used`), so the output is always structured.
- If a call fails (network, API or parsing error), the app logs the error and offers the fallback menu for that query.

**Fallback mode** (no key)

1. DuckDuckGo results printed in the terminal
2. Google search opened in your browser
3. Wikipedia search opened in your browser

## Setup

```bash
git clone https://github.com/Samiurr129/Building-Smarter-AI-Search.git
cd Building-Smarter-AI-Search
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp sample.env .env          # then add your Anthropic API key to .env
python main.py
```

Without a key, `python main.py` starts in fallback mode.

By default it uses `claude-sonnet-5-5`. Set `ANTHROPIC_MODEL` in `.env` to use another Claude model.

## Example

```
What can I help you research? (type 'exit' to quit): hydrogen HGV refuelling in the UK

Topic: Hydrogen HGV refuelling in the UK
<summary written by the agent>

Sources:
- <links returned by the search tools>
```

## Files

| File | Purpose |
| --- | --- |
| `main.py` | Mode selection, the LangChain agent, structured output and fallback menu |
| `tools.py` | Web search, Wikipedia and save-to-file tools |
| `sample.env` | Template for your `.env` file. Never commit `.env` |

## Tech

Python, LangChain 0.3, Anthropic Claude, Pydantic, DuckDuckGo search (`ddgs`), Wikipedia API, `logging`.

## Author

**Samiur Rahman**, Bradford, UK. [LinkedIn](https://www.linkedin.com/in/samiur-rahman29/) · [GitHub](https://github.com/Samiurr129)

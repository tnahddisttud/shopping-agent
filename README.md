# AI Shopping Agent

Chat to search a grocery catalog ("find me organic honey under $20 with 4.5+ rating") and place orders. Built with LangChain, Streamlit, and `openai/gpt-oss-120b` on GroqCloud.

## Run

1. Copy `.env.example` to `.env` and add your `GROQ_API_KEY`.
2. `uv sync`
3. `uv run streamlit run app.py`

The SQLite database (`resources/store.db`) is created automatically on first run, or manually with `uv run python -m src.setup_db`. Orders are inserted into the `orders` table.

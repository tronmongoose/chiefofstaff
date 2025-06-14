# Personal AI Agent — Phase 1 Starter

Welcome to your LangChain + LangGraph starter project, built inside Cursor IDE.

This README documents the work completed so far in Phase 1: successful setup of the foundational agent orchestration framework.

---

## ✅ Project Goals

- Build a personal AI assistant with true agentic capabilities.
- Use modern orchestration frameworks: **LangChain** + **LangGraph**.
- Develop entirely inside Cursor IDE for AI-powered coding assistance.
- Prepare foundation for multi-agent pipelines, memory, retrieval, and future SaaS-grade expansion.

---

## ✅ Stack Summary

| Component           | Version  | Purpose                  |
|---------------------|----------|--------------------------|
| Python              | 3.11+    | Core language            |
| Cursor IDE          | latest   | AI-powered coding        |
| LangChain           | 0.1.15+  | LLM orchestration        |
| LangGraph           | 0.0.33+  | Agent state graph        |
| langchain-openai    | 0.0.8+   | OpenAI LLM integration   |
| openai              | 1.30.1+  | Direct OpenAI SDK        |
| python-dotenv       | 1.0.1+   | API key management       |
| langchain-chroma    | 0.2.4+   | Chroma vectorstore       |

---

## ✅ What Works So Far

- ✅ Local dev environment fully operational inside Cursor.
- ✅ Python virtual environment initialized.
- ✅ All required packages installed via `requirements.txt`.
- ✅ `.env` file securely storing OpenAI API Key.
- ✅ LangGraph orchestration successfully built & tested.
- ✅ LLM calls integrated via LangChain's `ChatOpenAI`.
- ✅ Retrieval-Augmented Generation (RAG) using `knowledge.txt` and Chroma vectorstore.
- ✅ Test run returns model-generated response via graph execution.

---

## ✅ File Structure

```bash
my-langgraph-project/
│
├── main.py          # Main LangGraph agent code
├── retrieval.py     # RAG logic: vectorstore, chunking, retrieval
├── memory.py        # (Optional) Memory system (may show deprecation warnings)
├── tools.py         # (Optional) Tool definitions for agent
├── knowledge.txt    # Your personal knowledge base (used for RAG)
├── chroma_db/       # Chroma vectorstore persistence (auto-generated, can be ignored in git)
├── .env             # API keys (not committed to version control)
├── requirements.txt # All Python dependencies
└── README.md        # Current documentation (this file)
```

---

## 🚀 How to Run

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Set up your OpenAI API key:**
   - Create a `.env` file with:
     ```
     OPENAI_API_KEY=sk-...
     ```
3. **Add your knowledge:**
   - Edit `knowledge.txt` with facts, goals, or any info you want your agent to use.
4. **Run the agent:**
   ```bash
   python3 main.py
   ```
   - The agent will use RAG to answer based on your `knowledge.txt`.

---

## 📚 Retrieval-Augmented Generation (RAG)
- The agent uses Chroma vectorstore to retrieve relevant information from `knowledge.txt` for each user query.
- The vectorstore is persisted in `chroma_db/` (auto-generated).
- You can update `knowledge.txt` and re-run the agent to refresh the knowledge base.

---

## 📝 Version Control & GitHub
- **Do NOT commit your `.env` file or `chroma_db/` directory.**
- Add these lines to your `.gitignore`:
  ```
  .env
  chroma_db/
  __pycache__/
  ```
- To push your project to GitHub:
  ```bash
  git init
  git add .
  git commit -m "Initial commit: working LangGraph RAG agent"
  git remote add origin <your-repo-url>
  git push -u origin main
  ```

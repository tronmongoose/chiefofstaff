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
| LangChain           | 0.3.25+  | LLM orchestration        |
| LangGraph           | 0.0.33+  | Agent state graph        |
| langchain-openai    | 0.3.23+  | OpenAI LLM integration   |
| openai              | 1.86.0+  | Direct OpenAI SDK        |
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
- ✅ Multi-node workflow: memory, retrieval, and reasoning nodes.
- ✅ Tool usage: agent can reference weather and todo list tools.
- ✅ Test run returns model-generated response via graph execution.

---

## ✅ File Structure

```bash
my-langgraph-project/
│
├── main.py          # Main LangGraph agent code (multi-node workflow)
├── retrieval.py     # RAG logic: vectorstore, chunking, retrieval
├── memory.py        # Conversation memory system
├── tools.py         # Tool definitions for agent (e.g., weather, todo)
├── state.py         # Shared AgentState type for LangGraph
├── knowledge.txt    # Your personal knowledge base (used for RAG)
├── chroma_db/       # Chroma vectorstore persistence (auto-generated, can be ignored in git)
├── .env             # API keys (not committed to version control)
├── requirements.txt # All Python dependencies
└── README.md        # Current documentation (this file)
```

---

## 🧠 Workflow Overview

The agent's workflow is built as a **LangGraph** with three main nodes:

1. **Memory Node:** Loads chat history from memory.
2. **Retrieval Node:** Retrieves relevant knowledge from `knowledge.txt` using Chroma vectorstore (with chunking).
3. **Reasoning Node:** Uses the LLM to generate a response, referencing chat history, retrieved knowledge, and available tools.

The workflow is extensible—add more nodes for tools, actions, or multi-agent logic as needed.

---

## 🛠️ Tools

- Tools are defined in `tools.py` using the `@tool` decorator.
- Example tools: `get_weather`, `get_todo_list`.
- To add your own, define a new function with `@tool` and add it to the `tools` list.
- The agent is prompted to use tools when appropriate.

---

## 📚 Retrieval-Augmented Generation (RAG)
- The agent uses Chroma vectorstore to retrieve relevant information from `knowledge.txt` for each user query.
- Documents are automatically chunked for better retrieval.
- The vectorstore is persisted in `chroma_db/` (auto-generated).
- **If you update `knowledge.txt`, re-run the following to refresh the vectorstore:**
  ```bash
  python3 -c "from retrieval import create_vectorstore, add_documents; vs = create_vectorstore(); add_documents(vs)"
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
4. **(Re)build the vectorstore:**
   - If you change `knowledge.txt`, run:
     ```bash
     python3 -c "from retrieval import create_vectorstore, add_documents; vs = create_vectorstore(); add_documents(vs)"
     ```
5. **Run the agent:**
   ```bash
   python3 main.py
   ```
   - The agent will use RAG, memory, and tools to answer based on your `knowledge.txt`.

---

## 💬 Sample Chat Session

```
You: What are you building?
AI: Erik Huckle is building a personal AI agent. He wants it to serve as a Chief of Staff. He uses LangGraph and Cursor IDE.

You: What's the weather in Paris?
AI: The weather in Paris is 72°F and sunny.

You: What's on my todo list?
AI: Erik Huckle's todo list: 1) Build AI agent. 2) Test LangGraph. 3) Celebrate progress.
```

---

## ⚠️ Deprecation Warnings
- You may see warnings about the memory system. This is due to ongoing changes in LangChain. For the latest, see the [LangChain Memory Migration Guide](https://python.langchain.com/docs/versions/migrating_memory/).
- The retrieval system uses the latest `langchain-chroma` package as recommended.

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

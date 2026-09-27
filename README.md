# Support Agent Demo

A customer-support agent for a small online store. It is built with **Google ADK** (Agent Development Kit), runs on a **Gemini** model, and gets its tools from several **MCP** (Model Context Protocol) servers:

| Toolset | Kind | Transport | What it gives the agent |
|---|---|---|---|
| `ecommerce_mcp_server` (this repo) | Private | stdio (ADK launches it for you) | Order status, order details, product search, product details |
| `@modelcontextprotocol/server-filesystem` | Public (npm) | stdio via `npx` | Read access to the store policies in [docs/](docs/) |
| `duckduckgo-mcp-server` | Public (PyPI) | stdio via `uvx` | Web search for general questions not about the store |

The agent's rules (in [support_agent/agent.py](support_agent/agent.py)) tell it to use the store tools for orders and products, read the policy files for refund and shipping questions, and use web search only for questions that have nothing to do with the store.

---

## Project structure

```
support-agent-demo/
├── .env.example                # Template for .env
├── .env                        # GOOGLE_API_KEY and GEMINI_MODEL (copy from .env.example)
├── .gitignore
├── requirements.txt            # mcp, google-adk
├── docs/
│   ├── refund_policy.md        # Read by the filesystem MCP server
│   └── shipping_policy.md
├── ecommerce_mcp_server/
│   ├── server.py               # Private MCP server (4 tools)
│   └── data.py                 # Mock products and orders
└── support_agent/
    ├── __init__.py
    └── agent.py                # ADK root_agent + MCP toolsets
```

---

## Prerequisites

| Requirement | Why | Check |
|---|---|---|
| Python 3.10+ | ADK, MCP server | `python --version` |
| Node.js 18+ (includes `npx`) | Filesystem MCP server, MCP Inspector | `node --version` |
| [uv](https://docs.astral.sh/uv/) (includes `uvx`) | DuckDuckGo MCP server | `uvx --version` |
| Gemini API key | The agent's model | Get one free at <https://aistudio.google.com/apikey> |

Install uv if you don't have it:

```powershell
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

## Setup

### 1. Create a virtual environment and install dependencies

Run these from the project root (`support-agent-demo/`).

**Windows (PowerShell)**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment variables

Copy the template and fill in your key:

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

`.env` should contain:

```dotenv
GOOGLE_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-3.5-flash-lite
```

- `GOOGLE_API_KEY`: required. ADK uses it to call Gemini.
- `GEMINI_MODEL`: optional. It defaults to `gemini-3.5-flash-lite`.

`.gitignore` already excludes `.env`, so your key won't be committed.

### 3. (Optional) Pre-fetch the public MCP servers

The agent downloads these the first time it starts. Fetching them ahead of time avoids a slow first start or a timeout:

```bash
npx -y @modelcontextprotocol/server-filesystem --help
uvx duckduckgo-mcp-server --help
```

---

## Running the solution

All three MCP servers use **stdio**. When the agent starts, ADK launches each one as a subprocess, so you don't need to start any server yourself.

With the venv activated, from the project root:

```bash
adk web
```

Open <http://localhost:8000>, choose **support_agent** from the dropdown, and start chatting. See [Testing the agent with Google ADK](#testing-the-agent-with-google-adk) for other ways to run it.

---

## Testing the MCP server

Test the MCP server by itself before testing the agent. That way, if something breaks, you know whether the problem is in the tools or in the agent.

### Option A: MCP Inspector (recommended)

The [MCP Inspector](https://github.com/modelcontextprotocol/inspector) is a browser UI for calling MCP tools by hand. It launches the server over stdio, the same way the agent does.

1. With the venv activated, from the project root, start the Inspector and have it launch the server:

   ```bash
   # Windows
   npx @modelcontextprotocol/inspector python ecommerce_mcp_server\server.py

   # macOS / Linux
   npx @modelcontextprotocol/inspector python ecommerce_mcp_server/server.py
   ```

   If the Inspector picks up the wrong Python, pass the full path to `.venv\Scripts\python.exe` (Windows) or `.venv/bin/python` (macOS/Linux).

2. In the Inspector page that opens (usually <http://localhost:6274>), make sure these fields are set:
   - **Transport Type:** `STDIO`
   - **Command:** `python`
   - **Arguments:** `ecommerce_mcp_server/server.py`
   - Click **Connect**, open the **Tools** tab, then click **List Tools**.

3. Call each tool with these inputs and check the results:

| Tool | Input | Expected result |
|---|---|---|
| `get_order_status` | `order_id = O-5001` | `Order O-5001 is currently: packed for delivery. Estimated delivery: 2026-09-17.` |
| `get_order_status` | `order_id = O-9999` | `No order found with id O-9999.` |
| `get_order_details` | `order_id = O-5003` | JSON for the order: `P-1005`, quantity 2, `delivered` |
| `search_products` | `category = outdoor` | `P-1003` (green) and `P-1004` (blue) |
| `search_products` | `color = blue` | `P-1002` and `P-1004` |
| `search_products` | *(no arguments)* | All 5 products |
| `get_product_details` | `product_id = P-1004` | Trail Runner Backpack, blue, `stock: 0` |
| `get_product_details` | `product_id = P-0000` | `{"error": "No product found with id P-0000."}` |

#### Testing over Streamable HTTP instead

The server can also run as a standalone HTTP service:

1. In [ecommerce_mcp_server/server.py](ecommerce_mcp_server/server.py), switch the `__main__` block to HTTP:

   ```python
   if __name__ == "__main__":
       # mcp.run(transport="stdio")
       mcp.run(transport="streamable-http", host="127.0.0.1", port=8010)
   ```

2. Run `python ecommerce_mcp_server/server.py` and leave it running. Then run `npx @modelcontextprotocol/inspector`, set **Transport Type** to `Streamable HTTP` and **URL** to `http://127.0.0.1:8010/mcp`, and click **Connect**.

3. To connect another MCP client while the server is running, for example Claude Code:

   ```bash
   claude mcp add --transport http ecommerce http://127.0.0.1:8010/mcp
   ```

Switch the `__main__` block back to stdio before you run the agent. The agent launches `server.py` over stdio and won't work if the script starts an HTTP server.

### Option B: Test the public MCP servers

You can inspect the public servers the same way. The Inspector launches each one over stdio:

```bash
# Filesystem server scoped to the policy docs
npx @modelcontextprotocol/inspector npx -y @modelcontextprotocol/server-filesystem ./docs

# DuckDuckGo web search
npx @modelcontextprotocol/inspector uvx duckduckgo-mcp-server
```

For the filesystem server, try `list_directory` and `read_file` on `refund_policy.md`. For DuckDuckGo, try `search` with any query.

---

## Testing the agent with Google ADK

Run every `adk` command from the **project root**, the folder that *contains* `support_agent/`. ADK looks for agents in the subfolders of the directory you run it from.

### Option A: Dev web UI (`adk web`)

```bash
adk web
```

- Open <http://localhost:8000> and select **support_agent**.
- The **Events** / **Trace** panel shows every tool call the agent makes, with its arguments and response. Use it to confirm the agent picked the right tool.
- Use a different port with `adk web --port 8080`.

### Option B: Terminal chat (`adk run`)

```bash
adk run support_agent
```

Type messages at the `[user]:` prompt. Type `exit` to quit.

### Option C: REST API (`adk api_server`)

```bash
adk api_server
```

Then, from another terminal, create a session and send a message:

```bash
# Create a session
curl -X POST http://localhost:8000/apps/support_agent/users/u1/sessions/s1 \
  -H "Content-Type: application/json" -d "{}"

# Send a message
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
        "app_name": "support_agent",
        "user_id": "u1",
        "session_id": "s1",
        "new_message": { "role": "user", "parts": [{ "text": "Where is my order O-5002?" }] }
      }'
```

> In PowerShell, use `curl.exe` instead of `curl`, and put the JSON body in a file (`-d "@body.json"`) to avoid quoting problems.

Interactive API docs are at <http://localhost:8000/docs>.

### Suggested test prompts

These prompts check that the agent sends each kind of question to the right tool:

| Prompt | Expected tool | Expected answer |
|---|---|---|
| "What's the status of order O-5001?" | `get_order_status` | Packed for delivery, ETA 2026-09-17 |
| "What did I buy in order O-5003?" | `get_order_details` (+ `get_product_details`) | 2 × Ceramic Pour-Over Kettle, delivered |
| "Do you have any blue products?" | `search_products(color="blue")` | Aria Headphones (blue), Trail Runner Backpack (blue) |
| "Is the blue Trail Runner Backpack in stock?" | `search_products` / `get_product_details` | Out of stock (0) |
| "Where is order O-9999?" | `get_order_status` | Can't find that order |
| "What is your refund policy?" | Filesystem: `list_directory` / `read_file` → `refund_policy.md` | 30 days from delivery, unused, 5–7 business days to credit |
| "Do you ship to Australia?" | Filesystem → `shipping_policy.md` | No. The store ships to the US, Canada, and the UK only |
| "Can I return a gift card?" | Filesystem → `refund_policy.md` | No, gift cards can't be refunded |
| "What is the capital of Japan?" | DuckDuckGo `search` | Tokyo |
| "Search the web for your shipping times" | Filesystem → `shipping_policy.md` (**not** web search) | 5–7 business days, from this store's policy file |

**What to check in the trace:**
- Order and product answers come from the e-commerce tools, not from the model's general knowledge.
- Policy answers come from `read_file` on a file in `docs/`.
- Web search is never used for questions about the store.

### Resetting sessions

`adk web` saves chat history in `support_agent/.adk/session.db`. To start with a clean history, stop ADK and delete that file.

---

## Troubleshooting

| Symptom | Likely cause / fix |
|---|---|
| The e-commerce toolset hangs or times out when the agent starts | `server.py`'s `__main__` block is set to `streamable-http`. The agent needs `mcp.run(transport="stdio")`. |
| `npx` / `npx.cmd` not found | Install Node.js and restart the terminal. |
| `uvx` not found | Install uv (see [Prerequisites](#prerequisites)) and restart the terminal. |
| `No agents found` in `adk web` | You ran it from the wrong folder. Run it from the project root, not from inside `support_agent/`. |
| `401` / `API key not valid` / missing key | Check `GOOGLE_API_KEY` in `.env`. |
| `404 model not found` | Set `GEMINI_MODEL` in `.env` to a model your key can use. |
| `ModuleNotFoundError: data` when starting the server | Start it as a script (`python ecommerce_mcp_server/server.py`), not with `python -m`. |
| Slow first start or timeouts on the filesystem or web search toolsets | `npx` / `uvx` are downloading packages. Pre-fetch them (see [Setup step 3](#3-optional-pre-fetch-the-public-mcp-servers)). |
| `.venv\Scripts\Activate.ps1 cannot be loaded` (Windows) | Run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once. |

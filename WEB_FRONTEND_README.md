# Web Frontend for LangChain + Ollama + MCP

A beautiful, interactive web interface for chatting with your AI agent powered by LangChain, Ollama, and MCP tools.

## Features

✅ **Modern Chat Interface**
- Beautiful gradient UI design
- Real-time message display
- Typing indicators
- Message timestamps
- Smooth animations

✅ **Tool Sidebar**
- See all 4 available tools
- Click to auto-fill example queries
- Tool descriptions and examples

✅ **Quick Actions**
- Pre-configured query buttons
- One-click testing
- Common use case examples

✅ **Session Management**
- Conversation history
- Clear conversation button
- Persistent sessions

✅ **User Experience**
- Loading states
- Error handling
- Responsive design
- Mobile-friendly

---

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- Flask (web framework)
- Flask-CORS (cross-origin support)
- All existing dependencies

### 2. Make Sure Ollama is Running

```bash
# Check if Ollama is running
ollama list

# If not, start it
ollama serve
```

### 3. Start the Web Server

```bash
python web_server.py
```

You should see:
```
======================================================================
LangChain + Ollama + MCP Web Interface
======================================================================

Starting Flask server...
Open your browser and go to: http://localhost:5000

Press Ctrl+C to stop the server
======================================================================
```

### 4. Open Your Browser

Navigate to: **http://localhost:5000**

---

## Usage

### Chat Interface

1. **Type your query** in the input box at the bottom
2. **Press Enter** or click **"Send 🚀"**
3. **Wait for response** (you'll see "AI is thinking...")
4. **See the answer** appear in the chat

### Quick Actions

Click any of the quick action buttons:
- 🔢 Calculate 25 × 4
- 🌤️ Weather in Paris
- 💰 Gold Price
- 📧 Send Email

### Tool Sidebar

Click any tool card to auto-fill an example query.

### Example Queries

**Calculator:**
```
What is 156 times 23?
Calculate 500 divided by 25
Add 100 and 50
```

**Weather:**
```
What's the weather in Tokyo?
Tell me the weather in New York in Fahrenheit
Weather forecast for London
```

**Gold Price:**
```
What is the current gold price?
Get gold price in EUR
Tell me the live gold price in Indian Rupees
```

**Email:**
```
Send an email to john@example.com with subject "Hello"
Email sarah@company.com about the meeting
```

**Combined:**
```
Get the gold price and email it to trader@example.com
Calculate 100 times 50, then tell me the weather in Paris
```

---

## API Endpoints

The Flask backend exposes these REST APIs:

### POST /api/initialize
Initialize a new client session

**Response:**
```json
{
  "status": "success",
  "session_id": "uuid-here",
  "message": "Client initialized successfully"
}
```

### POST /api/query
Send a query to the AI agent

**Request:**
```json
{
  "query": "What is the current gold price?"
}
```

**Response:**
```json
{
  "status": "success",
  "response": "The current gold price is $2,045.50...",
  "query": "What is the current gold price?"
}
```

### GET /api/conversation
Get conversation history

**Response:**
```json
{
  "status": "success",
  "conversation": [
    {
      "type": "user",
      "message": "What is 25 times 4?",
      "timestamp": "2025-11-14T10:30:00"
    },
    {
      "type": "assistant",
      "message": "The result is 100.",
      "timestamp": "2025-11-14T10:30:05"
    }
  ]
}
```

### POST /api/clear
Clear conversation history

**Response:**
```json
{
  "status": "success",
  "message": "Conversation cleared"
}
```

### GET /api/tools
Get available tools

**Response:**
```json
{
  "status": "success",
  "tools": [
    {
      "name": "calculator",
      "description": "Perform arithmetic operations",
      "example": "What is 25 times 4?"
    },
    ...
  ]
}
```

---

## Architecture

```
┌─────────────┐
│   Browser   │ ← User interface (HTML/CSS/JavaScript)
│  (Client)   │
└──────┬──────┘
       │ HTTP/REST API
       ↓
┌─────────────────┐
│  Flask Server   │ ← web_server.py
│   (Backend)     │
└──────┬──────────┘
       │ Python calls
       ↓
┌─────────────────────────┐
│ LangChain MCP Client    │ ← langchain_mcp_client.py
│                         │
│  ┌──────────────────┐   │
│  │  Ollama (LLM)    │   │
│  └──────────────────┘   │
│           ↕              │
│  ┌──────────────────┐   │
│  │   MCP Server     │   │ ← mcp_server.py
│  │  (4 Tools)       │   │
│  └──────────────────┘   │
└─────────────────────────┘
```

---

## File Structure

```
MCP_Server_Mahendran/
├── web_server.py              ← Flask backend (NEW!)
├── templates/
│   └── index.html             ← Web UI (NEW!)
├── langchain_mcp_client.py    ← MCP client
├── mcp_server.py              ← MCP server with tools
├── requirements.txt           ← Updated with Flask
└── WEB_FRONTEND_README.md     ← This file
```

---

## Customization

### Change Port

In `web_server.py`:
```python
app.run(debug=True, host='0.0.0.0', port=8080)  # Change to 8080
```

### Change Model

In `web_server.py`, update:
```python
client = LangChainMCPClient(model_name="llama3.1")  # Change model
```

### Add Custom Styling

Edit `templates/index.html` CSS section to customize:
- Colors
- Fonts
- Layout
- Animations

### Add More Quick Actions

In `templates/index.html`, add more buttons:
```html
<button class="quick-action-btn" onclick="sendQuickQuery('Your query here')">
    🎯 Your Label
</button>
```

---

## Troubleshooting

### Issue: "Connection refused"

**Solution:**
1. Make sure Flask server is running
2. Check if port 5000 is available
3. Try accessing: http://127.0.0.1:5000

### Issue: "Client not initialized"

**Solution:**
1. Wait a few seconds for initialization
2. Refresh the page
3. Check console for errors

### Issue: "Ollama not found"

**Solution:**
```bash
# Start Ollama
ollama serve

# In another terminal, verify
ollama list
```

### Issue: "Module not found"

**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Issue: Slow responses

**Solution:**
1. Check if Ollama is running locally
2. Try a smaller model (llama3.2 instead of llama3.1:70b)
3. Check CPU/RAM usage

---

## Advanced Features

### Running on Network

To access from other devices:

```bash
# Find your IP address
# On Linux/Mac:
ifconfig | grep "inet "

# On Windows:
ipconfig
```

Then access: `http://YOUR_IP:5000`

### Production Deployment

For production, use a production WSGI server:

```bash
pip install gunicorn

gunicorn -w 4 -b 0.0.0.0:5000 web_server:app
```

### HTTPS/SSL

For HTTPS:
```bash
pip install pyopenssl

# In web_server.py, change last line to:
app.run(debug=False, host='0.0.0.0', port=5000, ssl_context='adhoc')
```

### Session Storage

Currently uses Flask sessions (in-memory). For persistent storage:

```python
# Install Redis
pip install redis flask-session

# Add to web_server.py:
from flask_session import Session
app.config['SESSION_TYPE'] = 'redis'
Session(app)
```

---

## Screenshots

### Chat Interface
```
┌────────────────────────────────────────────────┐
│ 🤖 LangChain + Ollama + MCP   [🗑️ Clear] [📊]│
├──────────────┬─────────────────────────────────┤
│              │                                 │
│ 🛠️ Tools    │  👤 You: What is 25 × 4?      │
│ ─────────    │  🤖 AI: The result is 100.     │
│ Calculator   │                                 │
│ Weather      │  👤 You: Gold price?           │
│ Gold Price   │  🤖 AI: $2,045.50 per ounce   │
│ Email        │                                 │
│              │  [Type your message... ] [Send]│
└──────────────┴─────────────────────────────────┘
```

---

## Security Notes

⚠️ **Important for Production:**

1. **Change secret key** in `web_server.py`:
```python
app.secret_key = 'use-a-real-secret-key-here'
```

2. **Disable debug mode**:
```python
app.run(debug=False, ...)
```

3. **Add authentication** for multi-user scenarios

4. **Validate all inputs** before processing

5. **Use HTTPS** in production

6. **Rate limiting** to prevent abuse

---

## Performance Tips

1. **Use caching** for repeated queries
2. **Implement connection pooling** for MCP
3. **Add request timeouts** to prevent hanging
4. **Monitor memory usage** for long sessions
5. **Implement pagination** for long conversations

---

## Next Steps

- [ ] Add user authentication
- [ ] Implement conversation saving/loading
- [ ] Add file upload support
- [ ] Create admin panel
- [ ] Add usage analytics
- [ ] Implement rate limiting
- [ ] Add dark mode toggle
- [ ] Create mobile app version

---

## Support

If you encounter issues:

1. Check the console logs (F12 in browser)
2. Check Flask terminal output
3. Verify Ollama is running: `ollama list`
4. Try clearing browser cache
5. Restart Flask server

---

**Enjoy your AI agent web interface!** 🚀🤖

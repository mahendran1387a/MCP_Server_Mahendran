"""
Flask Web Server for LangChain + Ollama + MCP
Provides a REST API and web interface for interacting with the AI agent
"""
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import asyncio
import uuid
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from langchain_mcp_client import LangChainMCPClient

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'
CORS(app)

# Store active clients per session
active_clients = {}


def get_client(session_id):
    """Get or create a client for this session"""
    if session_id not in active_clients:
        active_clients[session_id] = {
            'client': None,
            'conversation': [],
            'created_at': datetime.now()
        }
    return active_clients[session_id]


@app.route('/')
def index():
    """Serve the main web interface"""
    return render_template('index.html')


@app.route('/api/initialize', methods=['POST'])
def initialize():
    """Initialize a new MCP client session"""
    try:
        # Generate session ID
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())

        session_id = session['session_id']
        client_data = get_client(session_id)

        # Initialize client if not already done
        if client_data['client'] is None:
            async def init_client():
                client = LangChainMCPClient(model_name="llama3.2")
                await client.initialize()
                return client

            client = asyncio.run(init_client())
            client_data['client'] = client

        return jsonify({
            'status': 'success',
            'session_id': session_id,
            'message': 'Client initialized successfully'
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/query', methods=['POST'])
def query():
    """Process a user query"""
    try:
        data = request.json
        user_query = data.get('query', '')

        if not user_query:
            return jsonify({
                'status': 'error',
                'message': 'No query provided'
            }), 400

        # Get session
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())

        session_id = session['session_id']
        client_data = get_client(session_id)

        # Initialize if needed
        if client_data['client'] is None:
            async def init_client():
                client = LangChainMCPClient(model_name="llama3.2")
                await client.initialize()
                return client

            client = asyncio.run(init_client())
            client_data['client'] = client

        # Process query
        async def process():
            return await client_data['client'].process_query(user_query)

        response = asyncio.run(process())

        # Store in conversation history
        client_data['conversation'].append({
            'type': 'user',
            'message': user_query,
            'timestamp': datetime.now().isoformat()
        })
        client_data['conversation'].append({
            'type': 'assistant',
            'message': response,
            'timestamp': datetime.now().isoformat()
        })

        return jsonify({
            'status': 'success',
            'response': response,
            'query': user_query
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/conversation', methods=['GET'])
def get_conversation():
    """Get conversation history"""
    try:
        if 'session_id' not in session:
            return jsonify({
                'status': 'success',
                'conversation': []
            })

        session_id = session['session_id']
        client_data = get_client(session_id)

        return jsonify({
            'status': 'success',
            'conversation': client_data['conversation']
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/clear', methods=['POST'])
def clear_conversation():
    """Clear conversation history"""
    try:
        if 'session_id' in session:
            session_id = session['session_id']
            if session_id in active_clients:
                active_clients[session_id]['conversation'] = []

        return jsonify({
            'status': 'success',
            'message': 'Conversation cleared'
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/tools', methods=['GET'])
def get_tools():
    """Get available tools"""
    return jsonify({
        'status': 'success',
        'tools': [
            {
                'name': 'calculator',
                'description': 'Perform arithmetic operations',
                'example': 'What is 25 times 4?'
            },
            {
                'name': 'weather',
                'description': 'Get weather information for a city',
                'example': 'What\'s the weather in Paris?'
            },
            {
                'name': 'gold_price',
                'description': 'Get live gold market prices',
                'example': 'What is the current gold price in USD?'
            },
            {
                'name': 'send_email',
                'description': 'Send emails to recipients',
                'example': 'Send an email to john@example.com'
            }
        ]
    })


if __name__ == '__main__':
    print("=" * 60)
    print("LangChain + Ollama + MCP Web Interface")
    print("=" * 60)
    print("\nStarting Flask server...")
    print("Open your browser and go to: http://localhost:5000")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60)

    app.run(debug=True, host='0.0.0.0', port=5000)

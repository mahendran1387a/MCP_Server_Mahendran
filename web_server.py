"""
Flask Web Server for LangChain + Ollama + MCP
Provides a REST API and web interface for interacting with the AI agent
"""
from flask import Flask, render_template, request, jsonify, session, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import asyncio
import uuid
from datetime import datetime
import sys
import os
import threading
from concurrent.futures import Future

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from langchain_mcp_client import LangChainMCPClient
from rag_system import get_rag_system, process_uploaded_file

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'
CORS(app)

# Configure file uploads
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx', 'json', 'md', 'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize RAG system
rag_system = get_rag_system()

# Store active clients per session
active_clients = {}

# Create a single event loop for all async operations
loop = None
loop_thread = None

def start_background_loop(loop):
    """Run event loop in background thread"""
    asyncio.set_event_loop(loop)
    loop.run_forever()

def get_or_create_event_loop():
    """Get or create the background event loop"""
    global loop, loop_thread
    if loop is None:
        loop = asyncio.new_event_loop()
        loop_thread = threading.Thread(target=start_background_loop, args=(loop,), daemon=True)
        loop_thread.start()
    return loop

def run_async(coro):
    """Run async function in the background loop"""
    loop = get_or_create_event_loop()
    future = asyncio.run_coroutine_threadsafe(coro, loop)
    return future.result()


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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

            client = run_async(init_client())
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
                try:
                    client = LangChainMCPClient(model_name="llama3.2")
                    await client.initialize()
                    return client
                except Exception as e:
                    error_msg = str(e)
                    if "Connection" in error_msg or "refused" in error_msg:
                        raise RuntimeError("❌ Ollama is not running. Please start Ollama first:\n\n1. Open a terminal\n2. Run: ollama serve\n3. Refresh this page")
                    elif "llama3.2" in error_msg or "model" in error_msg:
                        raise RuntimeError("❌ Model 'llama3.2' not found. Please install it:\n\n1. Open a terminal\n2. Run: ollama pull llama3.2\n3. Wait for download to complete\n4. Refresh this page")
                    else:
                        raise RuntimeError(f"❌ Initialization failed: {error_msg}")

            try:
                client = run_async(init_client())
                client_data['client'] = client
            except RuntimeError as e:
                return jsonify({
                    'status': 'error',
                    'message': str(e)
                }), 500

        # Process query
        async def process():
            try:
                return await client_data['client'].process_query(user_query)
            except Exception as e:
                error_msg = str(e)
                if "Connection closed" in error_msg or "Connection" in error_msg:
                    # Reset the client on connection error
                    client_data['client'] = None
                    raise RuntimeError("❌ Connection lost. Ollama may have stopped. Please:\n\n1. Check if Ollama is running: ollama serve\n2. Refresh the page\n3. Try your query again")
                raise

        try:
            response = run_async(process())
        except RuntimeError as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

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

    except ConnectionError as e:
        return jsonify({
            'status': 'error',
            'message': f"❌ Connection Error: {str(e)}\n\nPlease check:\n1. Ollama is running (ollama serve)\n2. Model is installed (ollama pull llama3.2)"
        }), 500
    except Exception as e:
        error_msg = str(e)
        # Provide helpful error messages
        if "Connection" in error_msg:
            error_msg = "❌ Cannot connect to Ollama. Please start Ollama:\n\nRun: ollama serve"
        elif "model" in error_msg.lower():
            error_msg = "❌ Model not found. Please install llama3.2:\n\nRun: ollama pull llama3.2"

        return jsonify({
            'status': 'error',
            'message': error_msg
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
            },
            {
                'name': 'rag_query',
                'description': 'Search uploaded documents for information',
                'example': 'What does the document say about AI?'
            }
        ]
    })


@app.route('/api/rag/upload', methods=['POST'])
def upload_document():
    """Upload a document to the RAG database"""
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({
                'status': 'error',
                'message': 'No file provided'
            }), 400

        file = request.files['file']

        # Check if file is selected
        if file.filename == '':
            return jsonify({
                'status': 'error',
                'message': 'No file selected'
            }), 400

        # Check if file is allowed
        if not allowed_file(file.filename):
            return jsonify({
                'status': 'error',
                'message': f'File type not allowed. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400

        # Save file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Process file and add to RAG
        try:
            chunks = process_uploaded_file(filepath, filename)

            # Add chunks to RAG database
            metadatas = [{'filename': filename, 'chunk_index': i} for i in range(len(chunks))]
            doc_ids = rag_system.add_documents_batch(chunks, metadatas)

            # Clean up uploaded file
            os.remove(filepath)

            return jsonify({
                'status': 'success',
                'message': f'Successfully uploaded and processed {filename}',
                'chunks_added': len(doc_ids),
                'filename': filename
            })

        except Exception as e:
            # Clean up file on error
            if os.path.exists(filepath):
                os.remove(filepath)
            raise e

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/rag/stats', methods=['GET'])
def get_rag_stats():
    """Get RAG database statistics"""
    try:
        stats = rag_system.get_stats()
        return jsonify({
            'status': 'success',
            'stats': stats
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/rag/documents', methods=['GET'])
def get_rag_documents():
    """Get all documents in RAG database"""
    try:
        docs = rag_system.get_all_documents()
        return jsonify({
            'status': 'success',
            'documents': {
                'count': docs['count'],
                'ids': docs['ids'],
                'metadatas': docs['metadatas']
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/rag/clear', methods=['POST'])
def clear_rag_database():
    """Clear all documents from RAG database"""
    try:
        success = rag_system.clear_database()
        if success:
            return jsonify({
                'status': 'success',
                'message': 'RAG database cleared successfully'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to clear RAG database'
            }), 500
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


if __name__ == '__main__':
    print("=" * 60)
    print("LangChain + Ollama + MCP Web Interface")
    print("=" * 60)
    print("\nStarting Flask server...")
    print("Open your browser and go to: http://localhost:5000")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60)

    app.run(debug=True, host='0.0.0.0', port=5000)

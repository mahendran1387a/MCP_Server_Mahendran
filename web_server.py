"""
Flask Web Server for LangChain + Ollama + MCP
Provides a REST API and web interface for interacting with the AI agent
"""
from flask import Flask, render_template, request, jsonify, session, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import uuid
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from async_client_manager import get_client_manager
from rag_system import get_rag_system, process_uploaded_file
import logging
import traceback

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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

# Initialize async client manager
client_manager = get_client_manager()

# Store conversation history per session
conversations = {}


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_conversation(session_id):
    """Get or create conversation history for session"""
    if session_id not in conversations:
        conversations[session_id] = []
    return conversations[session_id]


@app.route('/')
def index():
    """Serve the main web interface"""
    return render_template('index.html')


@app.route('/api/test/ollama', methods=['GET'])
def test_ollama():
    """Test Ollama connectivity"""
    import aiohttp
    import asyncio

    async def check_ollama():
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('http://localhost:11434/api/version', timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {'status': 'success', 'message': 'Ollama is running', 'version': data}
                    else:
                        return {'status': 'error', 'message': f'Ollama returned status {response.status}'}
        except aiohttp.ClientConnectorError as e:
            return {'status': 'error', 'message': f'Connection refused: {str(e)}'}
        except asyncio.TimeoutError:
            return {'status': 'error', 'message': 'Connection timeout'}
        except Exception as e:
            return {'status': 'error', 'message': f'Error: {str(e)}'}

    result = asyncio.run(check_ollama())
    return jsonify(result)


@app.route('/api/initialize', methods=['POST'])
def initialize():
    """Initialize a new MCP client session"""
    try:
        # Generate session ID
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())

        session_id = session['session_id']
        logger.info(f"Initializing client for session: {session_id}")

        # Initialize client if not already done
        if not client_manager.has_client(session_id):
            try:
                logger.info(f"Attempting to initialize client with model: llama3.2")
                client_manager.initialize_client(session_id, model_name="llama3.2")
                logger.info(f"Client initialized successfully for session: {session_id}")
            except Exception as e:
                error_msg = str(e)
                logger.error(f"Client initialization failed: {error_msg}")
                logger.error(f"Full traceback: {traceback.format_exc()}")

                if "Connection" in error_msg or "refused" in error_msg:
                    raise RuntimeError("❌ Ollama is not running. Please start Ollama first:\n\n1. Open a terminal\n2. Run: ollama serve\n3. Refresh this page")
                elif "llama3.2" in error_msg or "model" in error_msg:
                    raise RuntimeError("❌ Model 'llama3.2' not found. Please install it:\n\n1. Open a terminal\n2. Run: ollama pull llama3.2\n3. Wait for download to complete\n4. Refresh this page")
                else:
                    raise RuntimeError(f"❌ Initialization failed: {error_msg}")

        return jsonify({
            'status': 'success',
            'session_id': session_id,
            'message': 'Client initialized successfully'
        })

    except RuntimeError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f"❌ Initialization failed: {str(e)}"
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

        # Initialize if needed
        if not client_manager.has_client(session_id):
            try:
                client_manager.initialize_client(session_id, model_name="llama3.2")
            except Exception as e:
                error_msg = str(e)
                if "Connection" in error_msg or "refused" in error_msg:
                    return jsonify({
                        'status': 'error',
                        'message': "❌ Ollama is not running. Please start Ollama first:\n\n1. Open a terminal\n2. Run: ollama serve\n3. Refresh this page"
                    }), 500
                elif "llama3.2" in error_msg or "model" in error_msg:
                    return jsonify({
                        'status': 'error',
                        'message': "❌ Model 'llama3.2' not found. Please install it:\n\n1. Open a terminal\n2. Run: ollama pull llama3.2\n3. Wait for download to complete\n4. Refresh this page"
                    }), 500
                else:
                    return jsonify({
                        'status': 'error',
                        'message': f"❌ Initialization failed: {error_msg}"
                    }), 500

        # Process query using client manager
        try:
            response = client_manager.query(session_id, user_query)
        except Exception as e:
            error_msg = str(e)
            if "Connection closed" in error_msg or "Connection" in error_msg:
                # Cleanup failed client
                client_manager.cleanup_client(session_id)
                return jsonify({
                    'status': 'error',
                    'message': "❌ Connection lost. Ollama may have stopped. Please:\n\n1. Check if Ollama is running: ollama serve\n2. Refresh the page\n3. Try your query again"
                }), 500
            elif "Connection" in error_msg or "refused" in error_msg:
                return jsonify({
                    'status': 'error',
                    'message': "❌ Cannot connect to Ollama. Please start Ollama:\n\nRun: ollama serve"
                }), 500
            elif "model" in error_msg.lower():
                return jsonify({
                    'status': 'error',
                    'message': "❌ Model not found. Please install llama3.2:\n\nRun: ollama pull llama3.2"
                }), 500
            else:
                return jsonify({
                    'status': 'error',
                    'message': f"❌ Query failed: {error_msg}"
                }), 500

        # Store in conversation history
        conversation = get_conversation(session_id)
        conversation.append({
            'type': 'user',
            'message': user_query,
            'timestamp': datetime.now().isoformat()
        })
        conversation.append({
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
            'message': f"❌ Unexpected error: {str(e)}"
        }), 500


@app.route('/api/conversation', methods=['GET'])
def get_conversation_history():
    """Get conversation history"""
    try:
        if 'session_id' not in session:
            return jsonify({
                'status': 'success',
                'conversation': []
            })

        session_id = session['session_id']
        conversation = get_conversation(session_id)

        return jsonify({
            'status': 'success',
            'conversation': conversation
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
            if session_id in conversations:
                conversations[session_id] = []

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

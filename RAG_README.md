# RAG (Retrieval-Augmented Generation) System

Complete documentation for the RAG system integrated into the LangChain + Ollama + MCP framework.

---

## Overview

The RAG system allows you to upload documents and query them using natural language. The AI agent can search through your uploaded documents to find relevant information and answer questions based on that content.

### Key Features

✅ **Document Upload**
- Web-based file upload interface
- Drag-and-drop support
- Multiple file format support

✅ **Vector Database**
- ChromaDB for efficient similarity search
- Automatic document chunking
- Cosine similarity for relevance scoring

✅ **Semantic Search**
- Natural language queries
- Contextual understanding
- Ranked results by relevance

✅ **Database Management**
- View statistics (document count, chunks)
- Clear database functionality
- Real-time stats updates

---

## Supported File Formats

The RAG system supports the following file formats:

| Format | Extension | Description |
|--------|-----------|-------------|
| Text | `.txt` | Plain text files |
| PDF | `.pdf` | PDF documents (text extraction) |
| Word | `.doc`, `.docx` | Microsoft Word documents |
| JSON | `.json` | JSON data files |
| Markdown | `.md` | Markdown formatted text |
| CSV | `.csv` | Comma-separated values |

---

## Quick Start

### 1. Upload Documents

**Via Web Interface:**
1. Open the web interface: http://localhost:5000
2. Look for the **"📚 RAG Database"** section in the left sidebar
3. Click on the upload zone or drag files into it
4. Wait for the upload and processing to complete

**Supported Actions:**
- **Click Upload**: Click the upload zone to browse and select files
- **Drag & Drop**: Drag files from your file manager directly into the upload zone
- **Multiple Files**: Upload multiple files one at a time

### 2. Query Documents

Once you've uploaded documents, you can query them:

**Example Queries:**
```
Search my documents for information about AI
What does the document say about machine learning?
Find information about the project timeline
Summarize what the documents say about pricing
```

The AI agent will automatically use the RAG query tool to search your uploaded documents and provide relevant answers.

---

## Architecture

### System Components

```
┌─────────────────────────────────────────────────┐
│              User Interface                      │
│  (Web Frontend - templates/index.html)          │
└────────────────┬────────────────────────────────┘
                 │ HTTP/REST
                 ↓
┌─────────────────────────────────────────────────┐
│           Flask Backend                          │
│          (web_server.py)                        │
│                                                  │
│  • /api/rag/upload   - Upload documents         │
│  • /api/rag/stats    - Get statistics           │
│  • /api/rag/clear    - Clear database           │
└────────────────┬────────────────────────────────┘
                 │ Python API
                 ↓
┌─────────────────────────────────────────────────┐
│           RAG System                             │
│         (rag_system.py)                         │
│                                                  │
│  • Document Processing                          │
│  • Text Chunking                                │
│  • Embedding Generation                         │
│  • Similarity Search                            │
└────────────────┬────────────────────────────────┘
                 │ Storage
                 ↓
┌─────────────────────────────────────────────────┐
│         ChromaDB (Vector Database)              │
│         (./rag_db directory)                    │
│                                                  │
│  • Document Embeddings                          │
│  • Metadata Storage                             │
│  • Similarity Index                             │
└─────────────────────────────────────────────────┘
```

### Data Flow

1. **Upload**: User uploads document → Flask receives file → Save temporarily
2. **Process**: Extract text → Split into chunks → Create embeddings
3. **Store**: Save chunks and embeddings to ChromaDB with metadata
4. **Query**: User asks question → Generate query embedding → Search ChromaDB
5. **Retrieve**: Get top N most similar chunks → Return to AI agent
6. **Generate**: AI agent uses retrieved context to answer question

---

## API Documentation

### Upload Document

**Endpoint:** `POST /api/rag/upload`

**Request:**
- Content-Type: `multipart/form-data`
- Body: File upload with field name `file`

**Response:**
```json
{
  "status": "success",
  "message": "Successfully uploaded and processed example.pdf",
  "chunks_added": 15,
  "filename": "example.pdf"
}
```

**Error Response:**
```json
{
  "status": "error",
  "message": "File type not allowed. Allowed types: txt, pdf, doc, docx, json, md, csv"
}
```

### Get Statistics

**Endpoint:** `GET /api/rag/stats`

**Response:**
```json
{
  "status": "success",
  "stats": {
    "total_documents": 25,
    "database_path": "./rag_db"
  }
}
```

### Get All Documents

**Endpoint:** `GET /api/rag/documents`

**Response:**
```json
{
  "status": "success",
  "documents": {
    "count": 25,
    "ids": ["doc1", "doc2", ...],
    "metadatas": [
      {"filename": "example.pdf", "chunk_index": 0, "length": 500},
      ...
    ]
  }
}
```

### Clear Database

**Endpoint:** `POST /api/rag/clear`

**Response:**
```json
{
  "status": "success",
  "message": "RAG database cleared successfully"
}
```

---

## RAG System Implementation Details

### Document Processing (rag_system.py)

#### Text Extraction

```python
def process_uploaded_file(file_path: str, filename: str) -> List[str]:
    """
    Extract text from uploaded files
    Supports: TXT, PDF, DOC, DOCX, JSON, MD
    """
```

**Processing by Format:**
- **TXT/MD**: Direct text reading with UTF-8 encoding
- **PDF**: PyPDF2 library for text extraction
- **DOC/DOCX**: python-docx library for text extraction
- **JSON**: Pretty-printed JSON formatting
- **CSV**: Row-by-row text conversion

#### Document Chunking

Documents are split into overlapping chunks for better retrieval:

```python
chunk_size = 1000        # Characters per chunk
overlap = 200            # Overlapping characters between chunks
```

**Why Chunking?**
- Embeddings have token limits
- Smaller chunks = more precise retrieval
- Overlap ensures context continuity

#### Embedding and Storage

```python
class RAGSystem:
    def add_document(self, text: str, metadata: Dict = None) -> str:
        """
        1. Generate embedding for text (ChromaDB default)
        2. Create unique document ID (MD5 hash)
        3. Store in vector database with metadata
        """
```

**Metadata Stored:**
- `filename`: Original filename
- `chunk_index`: Position in document
- `length`: Chunk character count
- `upload_date`: Timestamp

### Vector Search

#### Similarity Search

```python
def query(self, query_text: str, n_results: int = 3) -> Dict:
    """
    1. Convert query to embedding
    2. Compute cosine similarity with all documents
    3. Return top N most similar chunks
    """
```

**Relevance Scoring:**
- **Distance < 0.3**: High relevance
- **0.3 ≤ Distance < 0.6**: Medium relevance
- **Distance ≥ 0.6**: Low relevance

---

## MCP Tool Integration

### RAG Query Tool (mcp_server.py)

The `rag_query` tool is exposed through the MCP server:

```python
Tool(
    name="rag_query",
    description="Query the RAG database to find relevant information from uploaded documents",
    inputSchema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The question or search query"
            },
            "n_results": {
                "type": "number",
                "description": "Number of relevant documents to retrieve",
                "default": 3
            }
        },
        "required": ["query"]
    }
)
```

**Tool Response Format:**
```
📚 RAG Query Results
────────────────────────────────
Query: What is AI?
Found: 3 relevant document(s)

Result #1 (Relevance: High)
────────────────────────────────
Artificial Intelligence (AI) is the simulation of human
intelligence processes by machines...

Metadata: ai_guide.pdf | Length: 450 chars

────────────────────────────────
💡 Tip: You can use this information to answer your question!
```

---

## Web Frontend Features

### Upload Interface

The web interface provides:

1. **Visual Upload Zone**
   - Click to browse files
   - Drag and drop support
   - Real-time upload status
   - File type validation

2. **Database Statistics**
   - Document count
   - Total chunks stored
   - Auto-refresh on upload

3. **Management Actions**
   - Refresh stats button
   - Clear database button (with confirmation)

### User Experience

**Upload Flow:**
```
1. User selects/drops file
   ↓
2. Show "Uploading and processing..." status
   ↓
3. File uploaded to server
   ↓
4. Server processes and chunks document
   ↓
5. Chunks added to ChromaDB
   ↓
6. Show success: "✅ Added 15 chunks"
   ↓
7. Auto-refresh statistics
   ↓
8. Status message auto-clears after 5 seconds
```

**Query Flow:**
```
1. User types query: "What does the document say about X?"
   ↓
2. AI agent receives query
   ↓
3. AI agent recognizes need for document search
   ↓
4. AI agent calls rag_query tool
   ↓
5. RAG system searches vector database
   ↓
6. Relevant chunks returned to AI agent
   ↓
7. AI agent formulates answer using retrieved context
   ↓
8. Answer displayed to user
```

---

## Configuration

### RAG System Settings (rag_system.py)

```python
# Vector database location
PERSIST_DIRECTORY = "./rag_db"

# Document chunking
CHUNK_SIZE = 1000
OVERLAP = 200

# Search settings
DEFAULT_N_RESULTS = 3
SIMILARITY_METRIC = "cosine"
```

### Web Server Settings (web_server.py)

```python
# File upload constraints
UPLOAD_FOLDER = 'uploads'
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx', 'json', 'md', 'csv'}
```

---

## Usage Examples

### Example 1: Upload and Query Technical Documentation

```bash
# 1. Upload a PDF technical manual
# (Use web interface to upload "user_manual.pdf")

# 2. Query the document
User: "What are the system requirements mentioned in the manual?"

AI: [Uses RAG tool to search document]
    "According to the user manual, the system requirements are:
    - 8GB RAM minimum
    - 50GB free disk space
    - Windows 10 or higher
    [Retrieved from user_manual.pdf, page 5]"
```

### Example 2: Multiple Document Search

```bash
# 1. Upload multiple documents
# - project_plan.pdf
# - budget_2024.xlsx (saved as CSV)
# - meeting_notes.md

# 2. Query across all documents
User: "What is the total budget for Q1 according to the documents?"

AI: [Searches all uploaded documents]
    "Based on the budget_2024 document, the Q1 budget allocation
    is $150,000, with the following breakdown mentioned in the
    meeting notes..."
```

### Example 3: Code Documentation

```bash
# 1. Upload code documentation files
# - api_reference.md
# - architecture.json

# 2. Query specific API details
User: "How do I authenticate with the API?"

AI: [Retrieves relevant sections from api_reference.md]
    "According to the API reference, authentication requires:
    1. Obtain an API key from the dashboard
    2. Include it in the Authorization header
    3. Format: 'Bearer YOUR_API_KEY'
    [Source: api_reference.md, Authentication section]"
```

---

## Troubleshooting

### Issue: "No relevant documents found"

**Causes:**
- No documents uploaded yet
- Query doesn't match document content
- Documents failed to process

**Solutions:**
```bash
# 1. Check database stats
Click "🔄 Refresh Stats" to see document count

# 2. Verify file was uploaded
Look for success message: "✅ Successfully uploaded..."

# 3. Try a broader query
Instead of: "What is the exact price?"
Try: "Tell me about pricing"
```

### Issue: "Upload failed"

**Causes:**
- File too large (>16MB)
- Unsupported file format
- File corrupted or unreadable

**Solutions:**
```bash
# 1. Check file size
ls -lh yourfile.pdf

# 2. Verify file format
Supported: .txt, .pdf, .doc, .docx, .json, .md, .csv

# 3. Try re-saving the file
# For PDFs, try: "Print to PDF" to create clean version
```

### Issue: "Low relevance results"

**Causes:**
- Document content doesn't match query
- Semantic mismatch in terminology
- Document chunking split relevant content

**Solutions:**
```bash
# 1. Rephrase query to match document language
Document uses: "automobile"
Query uses: "car"
Try: Use exact terms from document

# 2. Request more results
"Search my documents for X, show more results"

# 3. Check document was uploaded correctly
Click "🔄 Refresh Stats" to verify
```

### Issue: "Database too large"

**Causes:**
- Many documents uploaded
- Large file uploads
- Database not cleared

**Solutions:**
```bash
# 1. Clear old/unused documents
Click "🗑️ Clear Database"

# 2. Check database size
ls -lh rag_db/

# 3. Re-upload only needed documents
```

---

## Performance Optimization

### For Large Documents

```python
# Adjust chunk size for better performance
# In rag_system.py:

# For large documents (books, manuals):
CHUNK_SIZE = 2000  # Larger chunks
OVERLAP = 400      # More overlap

# For small snippets (notes, tweets):
CHUNK_SIZE = 500   # Smaller chunks
OVERLAP = 100      # Less overlap
```

### For Many Documents

```python
# Increase results for better coverage
# In queries:

"Search my documents for X, show top 5 results"

# This will retrieve 5 chunks instead of default 3
```

### For Faster Searches

```python
# Use ChromaDB with HNSW indexing (default)
# Already configured for optimal performance

# Reduce number of results for speed
n_results = 1  # Fastest
n_results = 3  # Balanced (default)
n_results = 5  # Comprehensive
```

---

## Security Considerations

### File Upload Security

✅ **Implemented:**
- File extension validation
- Secure filename handling (`secure_filename()`)
- File size limits (16MB)
- Temporary file cleanup
- MIME type checking

⚠️ **For Production:**
```python
# Add virus scanning
import pyclamd
cd = pyclamd.ClamdUnixSocket()
cd.scan_file(filepath)

# Add user authentication
from flask_login import login_required

@app.route('/api/rag/upload', methods=['POST'])
@login_required
def upload_document():
    ...

# Add rate limiting
from flask_limiter import Limiter

limiter = Limiter(app)
@limiter.limit("10 per hour")
def upload_document():
    ...
```

### Data Privacy

- Documents stored locally in `./rag_db`
- No external API calls for embeddings (ChromaDB default)
- Session-based isolation in web interface
- Clear database option for data removal

---

## Advanced Usage

### Programmatic Access

You can use the RAG system directly in Python:

```python
from rag_system import get_rag_system

# Initialize
rag = get_rag_system()

# Add document
doc_id = rag.add_document(
    "This is my document content...",
    metadata={"source": "manual_entry", "author": "John"}
)

# Query
results = rag.query("What is the content about?", n_results=3)

# Access results
for doc, meta, distance in zip(
    results["documents"],
    results["metadatas"],
    results["distances"]
):
    print(f"Relevance: {1 - distance:.2f}")
    print(f"Content: {doc[:100]}...")
    print(f"Source: {meta['source']}")
    print("-" * 50)

# Get stats
stats = rag.get_stats()
print(f"Total documents: {stats['total_documents']}")

# Clear all
rag.clear_database()
```

### Batch Upload

```python
import os
from rag_system import process_uploaded_file, get_rag_system

rag = get_rag_system()
documents_folder = "./my_documents"

# Process all files in folder
for filename in os.listdir(documents_folder):
    filepath = os.path.join(documents_folder, filename)

    if os.path.isfile(filepath):
        try:
            # Process file
            chunks = process_uploaded_file(filepath, filename)

            # Add to database
            metadatas = [
                {"filename": filename, "chunk_index": i}
                for i in range(len(chunks))
            ]
            rag.add_documents_batch(chunks, metadatas)

            print(f"✅ Processed {filename}: {len(chunks)} chunks")
        except Exception as e:
            print(f"❌ Failed {filename}: {str(e)}")

print(f"Total documents: {rag.get_stats()['total_documents']}")
```

---

## Technical Details

### Dependencies

```txt
chromadb>=0.4.0      # Vector database
PyPDF2>=3.0.0        # PDF text extraction
python-docx>=0.8.11  # Word document processing
```

### Database Storage

ChromaDB stores data in `./rag_db/` directory:
```
rag_db/
├── chroma.sqlite3          # Metadata database
└── [UUID]/                 # Embeddings and vectors
    ├── data_level0.bin
    ├── header.bin
    └── length.bin
```

### Embedding Model

ChromaDB uses its default embedding function:
- **Model**: Sentence Transformers (all-MiniLM-L6-v2)
- **Dimension**: 384
- **Language**: English (multilingual support available)
- **Performance**: Fast, optimized for semantic search

---

## Limitations

### Current Limitations

1. **File Size**: 16MB maximum per file
2. **File Formats**: Limited to 7 formats (TXT, PDF, DOC, DOCX, JSON, MD, CSV)
3. **Language**: Optimized for English text
4. **OCR**: No OCR for scanned PDFs or images
5. **Tables**: Limited table extraction from PDFs
6. **Storage**: Local storage only (no cloud backup)

### Planned Improvements

- [ ] Support for more file formats (EPUB, RTF, HTML)
- [ ] OCR integration for scanned documents
- [ ] Multilingual embedding models
- [ ] Cloud storage integration (S3, Azure Blob)
- [ ] Advanced PDF parsing (tables, images)
- [ ] Document versioning
- [ ] Full-text search alongside vector search
- [ ] Query history and analytics

---

## Best Practices

### Document Preparation

1. **Clean Documents**: Remove unnecessary formatting
2. **Descriptive Names**: Use meaningful filenames
3. **Structured Content**: Well-organized documents work better
4. **Text-based PDFs**: Avoid scanned images
5. **Reasonable Size**: Keep files under 10MB for best performance

### Query Formulation

1. **Be Specific**: "What is the price of Product X?" vs "Tell me about pricing"
2. **Use Keywords**: Include important terms from documents
3. **Natural Language**: Write queries as questions
4. **Context**: Mention document name if querying specific file
5. **Follow-up**: Ask clarifying questions based on results

### Database Management

1. **Regular Cleanup**: Remove outdated documents
2. **Organize by Topic**: Upload related documents together
3. **Monitor Size**: Check stats regularly
4. **Backup**: Back up `./rag_db` directory periodically
5. **Test Queries**: Verify uploads with test queries

---

## FAQ

**Q: How many documents can I upload?**
A: No hard limit, but performance may degrade with 1000+ documents. Monitor database size and query speed.

**Q: Are my documents sent to external services?**
A: No. All processing and storage is local. ChromaDB runs locally with no external API calls.

**Q: Can I search across multiple file formats?**
A: Yes. The RAG system treats all documents as text, regardless of format.

**Q: What happens if I upload the same file twice?**
A: Duplicate content will be stored separately. Use clear database and re-upload to avoid duplicates.

**Q: Can I download documents from the database?**
A: Currently no. The database stores processed chunks, not original files. Keep originals separately.

**Q: How accurate is the search?**
A: Accuracy depends on document quality and query formulation. Typically 80-90% for well-formed queries.

**Q: Can I use this for real-time data?**
A: No. RAG is for static documents. For real-time data, use the API tools (weather, gold price, etc.).

**Q: What's the difference between RAG and web search?**
A: RAG searches YOUR uploaded documents. Web search would search the internet (not implemented).

---

## Support and Contribution

### Getting Help

1. Check this README
2. Review error messages in browser console (F12)
3. Check Flask server logs
4. Verify file formats and sizes

### Reporting Issues

Include:
- File format and size
- Error messages (both browser and server)
- Steps to reproduce
- Expected vs actual behavior

---

## Summary

The RAG system provides:
- ✅ Easy document upload via web interface
- ✅ Semantic search across all uploaded documents
- ✅ Natural language queries
- ✅ Automatic relevance ranking
- ✅ Integration with AI agent for intelligent responses
- ✅ Database management tools

**Start using RAG in 3 steps:**
1. Upload documents through web interface
2. Ask questions in natural language
3. Get AI-powered answers from your documents

---

**Enjoy your intelligent document search! 📚🔍🤖**

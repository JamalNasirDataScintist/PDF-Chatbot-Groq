# 🧠 DocuMind AI — PDF Intelligence Platform

> **AppLab AI/ML Engineer Assessment**  
> Built by Jamal with ♥  
> Deadline: 15/02/2026  
> Contact: Khurram.r@applab.qa

**Powered by Groq AI** — Lightning-fast LLM inference using llama-3.3-70b-versatile

---

## ✨ Features

✅ **PDF Upload & Processing** — Drag-and-drop or click to upload  
✅ **Groq AI Integration** — Ultra-fast responses using llama-3.3-70b-versatile  
✅ **RAG Architecture** — Retrieval Augmented Generation for accurate answers  
✅ **Semantic Search** — Sentence transformers with cosine similarity  
✅ **Multi-Document Support** — Upload and query multiple PDFs  
✅ **Source Attribution** — See which document section answered your question  
✅ **Confidence Scoring** — High/Medium/Low confidence indicators  
✅ **Futuristic UI** — Stunning dark theme with animated elements  
✅ **Docker Ready** — One-command deployment  
✅ **Production Grade** — Error handling, logging, health checks

---

## 🏗️ Architecture

```
┌─────────────────┐
│  Web Interface  │  ← Futuristic dark UI with animations
└────────┬────────┘
         │
┌────────▼────────┐
│   Flask REST    │  ← /api/upload, /api/chat, /api/documents, /api/health
│      API        │
└────────┬────────┘
         │
    ┌────┴─────┐
    │          │
┌───▼──┐   ┌──▼─────┐
│ PDF  │   │Chatbot │
│Proc. │   │Service │
└──────┘   └───┬────┘
                │
         ┌──────┴────────┐
         │               │
    ┌────▼──────┐  ┌─────▼─────┐
    │ Sentence  │  │  Groq AI  │
    │Transformers│  │ llama-3.3 │
    │(Embedding)│  │ 70b-versa │
    └───────────┘  └───────────┘
          │              │
    ┌─────▼──────────────▼────┐
    │  In-Memory Vector Store │
    │   (chunks + embeddings) │
    └─────────────────────────┘
```

### RAG (Retrieval Augmented Generation) Pipeline

1. **Document Upload**
   - PDF text extracted using PyPDF2
   - Text split into 500-word chunks with 50-word overlap
   - Each chunk embedded using `all-MiniLM-L6-v2` (384-dim vectors)
   - Stored in memory with metadata

2. **Question Processing**
   - User question encoded into 384-dim vector
   - Cosine similarity computed against all chunk embeddings
   - Top-4 most relevant chunks retrieved

3. **Answer Generation**
   - Retrieved chunks + question sent to Groq AI
   - Model: `llama-3.3-70b-versatile` (lightning-fast!)
   - Returns intelligent, natural language answer
   - Sources and confidence level calculated

---

## 🚀 Quick Start

### Option 1: Windows (Easiest)
```batch
Double-click run.bat
```
Then open: http://localhost:5000

### Option 2: Manual
```bash
py -3.10 -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac

pip install -r requirements.txt
python app.py
```
Open: http://localhost:5000

### Option 3: Docker
```bash
docker-compose up -d
```
Open: http://localhost:5000

---

## 📡 API Documentation

### `POST /api/upload`
Upload a PDF document

**Request:**
```http
POST /api/upload
Content-Type: multipart/form-data

file: <PDF file>
```

**Response:**
```json
{
  "success": true,
  "message": "Successfully uploaded and indexed \"document.pdf\"",
  "document_id": "doc_0",
  "filename": "document.pdf",
  "pages": 5,
  "text_length": 8432
}
```

---

### `POST /api/chat`
Ask a question about uploaded documents

**Request:**
```json
{
  "question": "What are the main requirements?"
}
```

**Response:**
```json
{
  "success": true,
  "question": "What are the main requirements?",
  "answer": "Based on the document, the main requirements are...",
  "sources": [
    {
      "filename": "document.pdf",
      "chunk": 3,
      "snippet": "The requirements include...",
      "relevance": 87.4
    }
  ],
  "confidence": "high",
  "model": "llama-3.3-70b-versatile",
  "provider": "Groq"
}
```

---

### `GET /api/documents`
List all uploaded documents

**Response:**
```json
{
  "success": true,
  "documents": [
    {
      "id": "doc_0",
      "filename": "report.pdf",
      "chunks": 24
    }
  ],
  "count": 1
}
```

---

### `POST /api/clear`
Clear all documents from knowledge base

**Response:**
```json
{
  "success": true,
  "message": "All documents cleared successfully"
}
```

---

### `GET /api/health`
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "service": "DocuMind AI — PDF Intelligence Platform",
  "model": "llama-3.3-70b-versatile",
  "provider": "Groq",
  "documents_loaded": 2,
  "timestamp": "2026-02-15T10:30:00"
}
```

---

## ⚙️ Configuration

Edit `.env` file:

```env
# Groq AI
GROQ_API_KEY=your_key_here
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_MAX_TOKENS=1024
GROQ_TEMPERATURE=0.3

# Embedding (runs locally)
EMBEDDING_MODEL=all-MiniLM-L6-v2

# RAG Settings
CHUNK_SIZE=500
CHUNK_OVERLAP=50
TOP_K_CHUNKS=4
```

---

## 📁 Project Structure

```
pdf-chatbot/
├── app.py                  # Flask application & API routes
├── config.py               # Configuration management
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker container setup
├── docker-compose.yml      # Docker Compose config
├── run.bat                 # Windows one-click startup
├── .env                    # Environment variables (Groq API key)
├── README.md               # This file
├── services/
│   ├── __init__.py
│   ├── pdf_processor.py    # PDF text extraction (PyPDF2)
│   └── chatbot.py          # RAG + Groq AI engine
├── templates/
│   └── index.html          # Futuristic UI (animated, stunning)
└── uploads/                # Uploaded PDF files
```

---

## 🧪 Testing

```bash
# Test the upload endpoint
curl -X POST -F "file=@document.pdf" http://localhost:5000/api/upload

# Test the chat endpoint
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question":"What is this document about?"}'

# Test health check
curl http://localhost:5000/api/health
```

---

## 🔒 Security Features

- ✅ File type validation (PDF only)
- ✅ 32MB file size limit
- ✅ Secure filename handling
- ✅ API key in environment variables
- ✅ CORS configured
- ✅ Input validation and sanitization

---

## 🎯 Assessment Requirements Checklist

| Requirement | Status | Implementation |
|------------|--------|----------------|
| Document Upload API | ✅ | POST /api/upload with PDF validation |
| Text Extraction | ✅ | PyPDF2 with preprocessing |
| Chatbot API | ✅ | POST /api/chat with RAG |
| NLP & AI Models | ✅ | Sentence transformers + Groq AI |
| User Interface | ✅ | Futuristic animated UI |
| Easy Interaction | ✅ | Drag-drop upload, real-time chat |
| Docker Deployment | ✅ | Dockerfile + docker-compose.yml |
| GitHub Repository | ✅ | Clean code, well-structured |
| README Documentation | ✅ | Complete setup & API docs |
| Presentation Ready | ✅ | Architecture overview included |

---

## 🎨 UI Features

The interface features a **stunning futuristic design**:

- 🌌 Animated particle canvas background
- 🔵 Glowing neon blue/cyan/purple accents
- 💫 Spinning hexagon logo with pulse effect
- 🌈 Rainbow gradient top bar
- ⚡ Animated upload rings
- 🛰️ Orbiting satellite system on welcome screen
- ✨ CRT scan lines for retro-futuristic feel
- 🎭 Smooth animations on all interactions
- 💎 Glass morphism effects throughout

---

## 🐳 Docker Deployment

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down

# Rebuild after changes
docker-compose up -d --build
```

---

## 🔧 Troubleshooting

### Issue: "Groq API key not configured"
**Solution:** Add your Groq API key to the `.env` file

### Issue: "Could not extract text from PDF"
**Solution:** Ensure PDF contains readable text (not scanned images)

### Issue: "Connection error"
**Solution:** Make sure Flask server is running on port 5000

### Issue: Python dependencies fail to install
**Solution:** Use Python 3.10 specifically (other versions may have compatibility issues)

---

## 📊 Performance

- **Upload:** ~2-3 seconds for typical 10-page PDF
- **Indexing:** ~1 second per 1000 words
- **Query Response:** ~0.5-1 second (thanks to Groq's speed!)
- **Concurrent Users:** Supports 2 workers (increase in production)

---

## 🚀 Future Enhancements

- [ ] Support for more file formats (DOCX, TXT, HTML)
- [ ] OCR for scanned PDFs
- [ ] Conversation history
- [ ] Multi-language support
- [ ] Export chat as PDF
- [ ] User authentication
- [ ] Cloud storage integration
- [ ] Advanced analytics dashboard

---

## 📝 Notes for Evaluators

This project demonstrates:

1. **Full-Stack Development** — Flask backend + JavaScript frontend
2. **AI/ML Integration** — RAG architecture with embeddings + LLM
3. **NLP Techniques** — Semantic search, chunking, vector similarity
4. **API Design** — RESTful endpoints with proper error handling
5. **DevOps** — Docker containerization for easy deployment
6. **Code Quality** — Clean structure, comments, documentation
7. **UI/UX Design** — Professional, intuitive, visually striking interface

---

**Built with ♥ by Jamal**  
**Dedicated to AppLab**  
**February 2026**

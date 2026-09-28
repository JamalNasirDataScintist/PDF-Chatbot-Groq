"""
DocuMind AI — PDF Intelligence Platform
Powered by Groq AI (Lightning-Fast LLM Inference)

AppLab AI/ML Engineer Assessment
Built by Jamal with ♥
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import logging
from datetime import datetime

from services.pdf_processor import PDFProcessor
from services.chatbot import Chatbot
from config import Config

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize services
pdf_processor = PDFProcessor()
chatbot = Chatbot()

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


@app.route('/')
def index():
    """Serve the main application interface"""
    return render_template('index.html')


@app.route('/api/upload', methods=['POST'])
def upload_document():
    """
    Upload PDF Document
    
    Accepts PDF file, extracts text, and indexes it in the knowledge base.
    Uses NLP techniques (sentence transformers) to create semantic embeddings.
    """
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400

        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'success': False, 'error': 'Only PDF files are supported'}), 400

        # Save file securely
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        logger.info(f"File saved: {filepath}")

        # Extract text from PDF
        extracted_text, page_count = pdf_processor.extract_text(filepath)

        if not extracted_text:
            return jsonify({
                'success': False,
                'error': 'Could not extract text from PDF. Ensure it contains readable text.'
            }), 400

        # Add to chatbot knowledge base
        doc_id = chatbot.add_document(extracted_text, filename)
        logger.info(f"Document indexed: {filename} ({page_count} pages)")

        return jsonify({
            'success': True,
            'message': f'Successfully uploaded and indexed "{filename}"',
            'document_id': doc_id,
            'filename': filename,
            'pages': page_count,
            'text_length': len(extracted_text)
        }), 200

    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500


@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Chat with Groq AI
    
    Uses RAG (Retrieval Augmented Generation):
    1. Retrieves relevant chunks via semantic search
    2. Sends context + question to Groq AI
    3. Returns intelligent, context-aware answer
    
    Model: llama-3.3-70b-versatile (lightning fast!)
    """
    try:
        data = request.get_json()

        if not data or 'question' not in data:
            return jsonify({'success': False, 'error': 'No question provided'}), 400

        question = data['question'].strip()

        if not question:
            return jsonify({'success': False, 'error': 'Question cannot be empty'}), 400

        if not chatbot.has_documents():
            return jsonify({
                'success': False,
                'error': 'Please upload a PDF document before asking questions.'
            }), 400

        # Get AI-powered answer using Groq
        response = chatbot.get_answer(question)

        logger.info(f"Question answered: {question[:50]}...")

        return jsonify({
            'success': True,
            'question': question,
            'answer': response['answer'],
            'sources': response.get('sources', []),
            'confidence': response.get('confidence', 'medium'),
            'model': 'llama-3.3-70b-versatile',
            'provider': 'Groq'
        }), 200

    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500


@app.route('/api/documents', methods=['GET'])
def get_documents():
    """List all uploaded documents in knowledge base"""
    try:
        documents = chatbot.get_document_list()
        return jsonify({
            'success': True,
            'documents': documents,
            'count': len(documents)
        }), 200
    except Exception as e:
        logger.error(f"Error fetching documents: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/clear', methods=['POST'])
def clear_documents():
    """Clear all documents from knowledge base"""
    try:
        chatbot.clear_documents()
        logger.info("Knowledge base cleared")
        return jsonify({
            'success': True,
            'message': 'All documents cleared successfully'
        }), 200
    except Exception as e:
        logger.error(f"Error clearing documents: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'DocuMind AI — PDF Intelligence Platform',
        'model': 'llama-3.3-70b-versatile',
        'provider': 'Groq',
        'documents_loaded': len(chatbot.get_document_list()),
        'timestamp': datetime.now().isoformat()
    }), 200


if __name__ == '__main__':
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )

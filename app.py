from flask import Flask, request, jsonify
from service.llm_gimi import QCMGenerator
import os
from dotenv import load_dotenv
import traceback
from werkzeug.utils import secure_filename

# Charger les variables d'environnement
load_dotenv()

app = Flask(__name__)

# Configuration for file uploads
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create required directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('chroma_db', exist_ok=True)
os.makedirs('metadata', exist_ok=True)

# Initialiser le générateur de QCM
qcm_generator = QCMGenerator()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/generate', methods=['POST'])
def api_generate_qcm():
    """Endpoint API dédié pour générer des questions (format JSON uniquement)"""
    try:
        has_pdf = False
        filename = None
        stats = None
        
        # Check if there's a file in the request
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No selected file', 'status': 'error'}), 400
            
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                # Process the PDF file
                try:
                    qcm_generator.rag_service.process_pdf(filepath)
                    # Get document statistics
                    stats = qcm_generator.rag_service.get_document_stats()
                    has_pdf = True
                except Exception as e:
                    return jsonify({'error': f'Error processing PDF: {str(e)}', 'status': 'error'}), 500
        
        # Get JSON data from form data if not in request.json
        # json_data = request.json if request.json else request.form.to_dict()
        json_data = request.get_json(silent=True) or request.form.to_dict()

        
        # Use handle_json_request for question generation
        response = handle_json_request(json_data, has_pdf)
        
        # If we have a PDF, add file information to the response
        if has_pdf and response.status_code == 200:
            response_data = response.get_json()
            response_data['metadata'].update({
                'filename': filename,
                'document_stats': stats
            })
            return jsonify(response_data)
            
        return response
            
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e), 'status': 'error'}), 500

def handle_json_request(json_data, has_pdf=False):
    """Traiter les requêtes au format JSON"""
    if not json_data:
        return jsonify({'error': 'Données JSON requises', 'status': 'error'}), 400
    
    # Get question parameters
    num_open_questions = int(json_data.get('num_open_questions', 0))
    num_yes_no_questions = int(json_data.get('num_yes_no_questions', 0))
    
    # Verify at least one type of question is requested
    if num_open_questions == 0 and num_yes_no_questions == 0:
        return jsonify({'error': 'Veuillez spécifier au moins un type de question à générer', 'status': 'error'}), 400
    
    # Generate questions
    try:
        if has_pdf:
            # If we have a processed PDF, use the vector store
            questions = qcm_generator.generate_questions_from_text(
                text_content="",  # Empty string since we're using the vector store
                num_open_questions=num_open_questions,
                num_yes_no_questions=num_yes_no_questions
            )
            # Get document statistics for PDF
            stats = qcm_generator.rag_service.get_document_stats()
        else:
            # If no PDF, require text content
            text_content = json_data.get('text_content', '')
            if not text_content:
                return jsonify({'error': 'Text content is required when no PDF is provided', 'status': 'error'}), 400
            
            # Process the text content through RAG system
            try:
                qcm_generator.rag_service.process_text(text_content)
                # Get document statistics
                stats = qcm_generator.rag_service.get_document_stats()
            except Exception as e:
                return jsonify({'error': f'Error processing text: {str(e)}', 'status': 'error'}), 500
            
            # Generate questions using the processed text
            questions = qcm_generator.generate_questions_from_text(
                text_content=text_content,
                num_open_questions=num_open_questions,
                num_yes_no_questions=num_yes_no_questions
            )
        
        response_data = {
            'status': 'success',
            'questions': questions,
            'metadata': {
                'total_questions': len(questions),
                'open_questions': num_open_questions,
                'yes_no_questions': num_yes_no_questions,
                'document_stats': stats
            }
        }
            
        return jsonify(response_data)
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': f'Erreur lors de la génération des questions: {str(e)}', 'status': 'error'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
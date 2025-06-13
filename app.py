from flask import Flask, render_template, request, jsonify
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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/documentation')
def api_documentation():
    """Page de documentation de l'API"""
    return render_template('api_docs.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle PDF file upload"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part', 'status': 'error'}), 400
    
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
            
            return jsonify({
                'status': 'success',
                'message': 'File uploaded and processed successfully',
                'filename': filename,
                'document_stats': stats
            })
        except Exception as e:
            return jsonify({'error': str(e), 'status': 'error'}), 500
    
    return jsonify({'error': 'Invalid file type', 'status': 'error'}), 400

@app.route('/generate', methods=['POST'])
def generate_qcm():
    """API pour générer des questions à partir d'un texte (compatible avec le formulaire HTML)"""
    # Déterminer si la requête vient du formulaire ou est en JSON
    if request.content_type and 'application/json' in request.content_type:
        return handle_json_request(request.json)
    else:
        return handle_form_request(request.form)

@app.route('/api/generate', methods=['POST'])
def api_generate_qcm():
    """Endpoint API dédié pour générer des questions (format JSON uniquement)"""
    try:
        return handle_json_request(request.json)
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e), 'status': 'error'}), 500

def handle_form_request(form_data):
    """Traiter les requêtes provenant du formulaire HTML"""
    text_content = form_data.get('text_content', '')
    
    if not text_content:
        return jsonify({'error': 'Texte requis', 'status': 'error'}), 400
    
    # Vérifier quels types de questions sont demandés
    open_questions_selected = form_data.get('open_questions') == 'on'
    yes_no_questions_selected = form_data.get('yes_no_questions') == 'on'
    
    # Obtenir le nombre de questions pour chaque type
    num_open_questions = int(form_data.get('num_open_questions', 0)) if open_questions_selected else 0
    num_yes_no_questions = int(form_data.get('num_yes_no_questions', 0)) if yes_no_questions_selected else 0
    
    # Vérifier qu'au moins un type de question est sélectionné
    if num_open_questions == 0 and num_yes_no_questions == 0:
        return jsonify({'error': 'Veuillez sélectionner au moins un type de question à générer', 'status': 'error'}), 400
    
    # Générer les questions
    try:
        questions = qcm_generator.generate_questions_from_text(
            text_content=text_content,
            num_open_questions=num_open_questions,
            num_yes_no_questions=num_yes_no_questions
        )
        
        return jsonify({'questions': questions, 'status': 'success'})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': f'Erreur lors de la génération des questions: {str(e)}', 'status': 'error'}), 500

def handle_json_request(json_data):
    """Traiter les requêtes au format JSON"""
    if not json_data:
        return jsonify({'error': 'Données JSON requises', 'status': 'error'}), 400
    
    text_content = json_data.get('text_content', '')
    
    if not text_content:
        return jsonify({'error': 'Texte requis', 'status': 'error'}), 400
    
    # Obtenir le nombre de questions pour chaque type
    num_open_questions = int(json_data.get('num_open_questions', 0))
    num_yes_no_questions = int(json_data.get('num_yes_no_questions', 0))
    
    # Vérifier qu'au moins un type de question est demandé
    if num_open_questions == 0 and num_yes_no_questions == 0:
        return jsonify({'error': 'Veuillez spécifier au moins un type de question à générer', 'status': 'error'}), 400
    
    # Générer les questions
    try:
        questions = qcm_generator.generate_questions_from_text(
            text_content=text_content,
            num_open_questions=num_open_questions,
            num_yes_no_questions=num_yes_no_questions
        )
        
        return jsonify({
            'status': 'success',
            'questions': questions,
            'metadata': {
                'total_questions': len(questions),
                'open_questions': num_open_questions,
                'yes_no_questions': num_yes_no_questions
            }
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': f'Erreur lors de la génération des questions: {str(e)}', 'status': 'error'}), 500

if __name__ == '__main__':
    # Create api_docs.html template if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    if not os.path.exists('templates/api_docs.html'):
        with open('templates/api_docs.html', 'w', encoding='utf-8') as f:
            f.write('''
<!DOCTYPE html>
<html>
<head>
    <title>Documentation API de Génération de Questions</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; line-height: 1.6; }
        h1, h2, h3 { color: #333; }
        pre { background: #f5f5f5; padding: 15px; border-radius: 5px; overflow-x: auto; }
        .endpoint { margin-bottom: 30px; border-left: 4px solid #2196F3; padding-left: 15px; }
        .method { display: inline-block; padding: 3px 8px; border-radius: 3px; color: white; background: #4CAF50; }
        .param-table { border-collapse: collapse; width: 100%; margin: 15px 0; }
        .param-table th, .param-table td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        .param-table th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <h1>Documentation API de Génération de Questions</h1>
    
    <div class="endpoint">
        <h2><span class="method">POST</span> /api/generate</h2>
        <p>Génère des questions ouvertes et/ou oui/non à partir d'un texte fourni.</p>
        
        <h3>Paramètres (format JSON)</h3>
        <table class="param-table">
            <tr>
                <th>Paramètre</th>
                <th>Type</th>
                <th>Requis</th>
                <th>Description</th>
            </tr>
            <tr>
                <td>text_content</td>
                <td>string</td>
                <td>Oui</td>
                <td>Le texte source pour générer les questions</td>
            </tr>
            <tr>
                <td>num_open_questions</td>
                <td>integer</td>
                <td>Non (défaut: 0)</td>
                <td>Nombre de questions ouvertes à générer</td>
            </tr>
            <tr>
                <td>num_yes_no_questions</td>
                <td>integer</td>
                <td>Non (défaut: 0)</td>
                <td>Nombre de questions oui/non à générer</td>
            </tr>
        </table>
        
        <h3>Exemple de Requête</h3>
        <pre>
curl -X POST http://localhost:5000/api/generate \
    -H "Content-Type: application/json" \
    -d '{
        "text_content": "L\'intelligence artificielle (IA) est l\'ensemble des théories et des techniques développant des programmes informatiques complexes capables de simuler certains traits de l\'intelligence humaine.",
        "num_open_questions": 2,
        "num_yes_no_questions": 1
    }'
        </pre>
        
        <h3>Exemple de Réponse</h3>
        <pre>
{
    "status": "success",
    "questions": [
        {
            "question": "Comment le texte définit-il l'intelligence artificielle?",
            "reference_answer": "Le texte définit l'intelligence artificielle comme l'ensemble des théories et des techniques développant des programmes informatiques complexes capables de simuler certains traits de l'intelligence humaine.",
            "type": "open"
        },
        {
            "question": "Quels traits l'intelligence artificielle est-elle capable de simuler selon le texte?",
            "reference_answer": "Selon le texte, l'intelligence artificielle est capable de simuler certains traits de l'intelligence humaine.",
            "type": "open"
        },
        {
            "question": "L'intelligence artificielle peut-elle simuler tous les traits de l'intelligence humaine selon le texte?",
            "answer": "non",
            "justification": "Le texte précise que l'IA est capable de simuler 'certains traits de l'intelligence humaine', ce qui implique une limitation et non une capacité à simuler tous les traits.",
            "type": "yes_no"
        }
    ],
    "metadata": {
        "total_questions": 3,
        "open_questions": 2,
        "yes_no_questions": 1
    }
}
        </pre>
    </div>
    
    <div class="endpoint">
        <h2>Test avec Postman</h2>
        <ol>
            <li>Ouvrez Postman</li>
            <li>Créez une nouvelle requête POST avec l'URL: <code>http://localhost:5000/api/generate</code></li>
            <li>Dans l'onglet "Headers", ajoutez: <code>Content-Type: application/json</code></li>
            <li>Dans l'onglet "Body", sélectionnez "raw" et "JSON", puis entrez votre requête JSON</li>
            <li>Cliquez sur "Send" pour soumettre la requête</li>
        </ol>
    </div>
</body>
</html>
            ''')
    
    app.run(debug=True)
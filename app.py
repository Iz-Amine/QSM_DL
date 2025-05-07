from flask import Flask, render_template, request, jsonify
from service.llm_gimi import QCMGenerator
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

app = Flask(__name__)

# Initialiser le générateur de QCM
qcm_generator = QCMGenerator()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_qcm():
    """API pour générer des QCMs à partir d'un texte"""
    text_content = request.form.get('text_content', '')
    num_questions = int(request.form.get('num_questions', 5))
    
    if not text_content:
        return jsonify({'error': 'Texte requis'}), 400
    
    # Générer les QCMs
    questions = qcm_generator.generate_qcm_from_text(text_content, num_questions)
    
    return jsonify({'questions': questions})

if __name__ == '__main__':
    app.run(debug=True)
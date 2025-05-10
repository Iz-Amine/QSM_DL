import json
from service.llm_gimi import QCMGenerator

# Texte de test
test_text = """
L'intelligence artificielle (IA) est l'ensemble des théories et des techniques 
développant des programmes informatiques complexes capables de simuler certains 
traits de l'intelligence humaine. Elle comporte plusieurs branches, dont l'apprentissage 
automatique et l'apprentissage profond.
"""

# Initialiser le générateur
generator = QCMGenerator()

try:
    # Tester la génération des deux types de questions
    print("Envoi des requêtes à l'API Gemini...")
    questions = generator.generate_questions_from_text(
        text_content=test_text,
        num_open_questions=1,
        num_yes_no_questions=1,
        model="gemini-2.0-flash"
    )
    
    # Afficher le résultat brut pour le débogage
    print(f"Résultat brut: {json.dumps(questions, indent=2)}")
    
    # Afficher les résultats
    if questions:
        # Séparer les questions par type
        open_questions = [q for q in questions if q.get('type') == 'open']
        yes_no_questions = [q for q in questions if q.get('type') == 'yes_no']
        
        # Afficher les questions ouvertes
        if open_questions:
            print("\n--- QUESTIONS OUVERTES ---")
            for i, q in enumerate(open_questions):
                print(f"Question {i+1}: {q['question']}")
                print(f"Réponse de référence: {q['reference_answer']}")
                print()
        
        # Afficher les questions oui/non
        if yes_no_questions:
            print("\n--- QUESTIONS OUI/NON ---")
            for i, q in enumerate(yes_no_questions):
                print(f"Question {i+1}: {q['question']}")
                print(f"Réponse: {q['answer']}")
                print(f"Justification: {q['justification']}")
                print()
    else:
        print("Aucune question n'a été générée.")
except Exception as e:
    print(f"Erreur lors du test: {e}")
    import traceback
    traceback.print_exc()
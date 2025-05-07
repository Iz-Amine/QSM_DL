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
    # Tester la génération
    print("Envoi de la requête à l'API Gemini...")
    questions = generator.generate_qcm_from_text(test_text, 2, model="gemini-2.0-flash")
    
    # Afficher le résultat brut pour le débogage
    print(f"Résultat brut: {json.dumps(questions, indent=2)}")
    
    # Afficher les résultats
    if questions:
        for i, q in enumerate(questions):
            print(f"Question {i+1}: {q['question']}")
            print(f"Réponse de référence: {q['reference_answer']}")
            print()
    else:
        print("Aucune question n'a été générée.")
except Exception as e:
    print(f"Erreur lors du test: {e}")
    import traceback
    traceback.print_exc()
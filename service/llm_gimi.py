import json
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

class QCMGenerator:
    def __init__(self):
        # Get API key
        self.api_key = os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")
        
        # Initialize the Gemini client
        self.client = genai.Client(api_key=self.api_key)
    
    def generate_qcm_from_text(self, text_content, num_questions=5, model="gemini-2.0-flash"):
        """
        Generate open-ended questions with reference answers from text using the Google Gemini API
        """
        try:
            # Create the prompt
            prompt = f"""
            Generate {num_questions} open-ended questions about the following text:
            
            {text_content}
            
            IMPORTANT INSTRUCTIONS:
            1. Create questions that are strictly based ONLY on the information contained in the text above.
            2. Do not use any external knowledge or information not present in the provided text.
            3. The questions and answers MUST be in the SAME LANGUAGE as the input text.
               - If the text is in French, generate questions and answers in French.
               - If the text is in Arabic, generate questions and answers in Arabic.
               - Always match the exact language of the original text.
            
            Each question should:
            1. Be an open-ended question (not multiple choice)
            2. Include a comprehensive reference answer that can be directly verified from the text
            3. Encourage thoughtful responses rather than simple yes/no or one-word answers
            
            Format the response as JSON:
            {{
              "questions": [
                {{
                  "question": "...",
                  "reference_answer": "..."
                }}
              ]
            }}
            
            Provide ONLY the JSON with no additional text.
            """
            
            print("Sending request to Gemini API...")
            
            # Make the request to Gemini API
            response = self.client.models.generate_content(
                model=model,
                contents=prompt
            )
            
            print(f"Response received from Gemini API")
            
            # Extract the content
            content = response.text
            
            # Try to parse JSON from content
            try:
                # Find JSON object in content
                start_index = content.find("{")
                end_index = content.rfind("}") + 1
                
                if start_index >= 0 and end_index > start_index:
                    json_str = content[start_index:end_index]
                    parsed_data = json.loads(json_str)
                    
                    # Extract questions
                    questions = parsed_data.get("questions", [])
                    if questions:
                        print(f"Successfully extracted {len(questions)} questions")
                        return questions
                    else:
                        print("No questions found in parsed data")
                else:
                    print("Could not find JSON in response content")
            except Exception as e:
                print(f"Error parsing JSON: {e}")
                print(f"Content: {content[:200]}...")  # Print first 200 chars
            
            return []
            
        except Exception as e:
            print(f"Error generating QCMs: {e}")
            import traceback
            traceback.print_exc()
            return []

# Example usage
if __name__ == "__main__":
    generator = QCMGenerator()
    
    sample_text = """
    Python is a high-level, interpreted programming language that was created 
    by Guido van Rossum and first released in 1991. It emphasizes code readability 
    with its notable use of significant whitespace. Its language constructs and 
    object-oriented approach aim to help programmers write clear, logical code 
    for projects of all scales.
    """
    
    questions = generator.generate_qcm_from_text(sample_text, num_questions=3)
    
    for i, q in enumerate(questions, 1):
        print(f"\nQuestion {i}: {q['question']}")
        print(f"Correct Answer: {q['correct_answer']}")
        print("Distractors:")
        for j, distractor in enumerate(q['distractors'], 1):
            print(f"  {j}. {distractor}")
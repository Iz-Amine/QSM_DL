import json
import os
import requests
from dotenv import load_dotenv

load_dotenv()

class QCMGenerator:
    def __init__(self):
        # Get API key
        self.api_key = os.environ.get("LLAMA_API_KEY")
        if not self.api_key:
            raise ValueError("LLAMA_API_KEY environment variable is not set")
    
    def generate_qcm_from_text(self, text_content, num_questions=5):
        """
        Generate multiple-choice questions from text using direct HTTP requests
        """
        try:
            # API endpoint - check the documentation for the correct URL
            api_url = "https://api.llama-api.com/chat/completions"
            
            # Request payload
            payload = {
                "model": "llama3.1-70b",
                "messages": [
                    {
                        "role": "user",
                        "content": f"""
                        Generate {num_questions} multiple-choice questions about the following text:
                        
                        {text_content}
                        
                        Each question should have:
                        1. A question
                        2. A correct answer
                        3. Three incorrect but plausible answers
                        
                        Format the response as JSON:
                        {{
                          "questions": [
                            {{
                              "question": "...",
                              "correct_answer": "...",
                              "distractors": ["...", "...", "..."]
                            }}
                          ]
                        }}
                        
                        Provide ONLY the JSON with no additional text.
                        """
                    }
                ]
            }
            
            # Headers
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Make the request
            print("Sending request to LLaMA API...")
            response = requests.post(api_url, headers=headers, json=payload)
            
            print(f"Response status: {response.status_code}")
            
            # Check if the request was successful
            if response.status_code == 200:
                # Parse the response
                data = response.json()
                
                # Try to extract the content
                content = data.get("choices", [])[0].get("message", {}).get("content", "")
                
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
                except Exception as e:
                    print(f"Error parsing JSON: {e}")
                    print(f"Content: {content[:200]}...")  # Print first 200 chars
            else:
                print(f"API request failed: {response.status_code}")
                print(f"Response text: {response.text[:200]}...")
            
            return []
            
        except Exception as e:
            print(f"Error generating QCMs: {e}")
            import traceback
            traceback.print_exc()
            return []
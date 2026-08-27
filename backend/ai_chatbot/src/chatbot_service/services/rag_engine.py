from typing import Dict, Any, List

class RAGEngine:
    """
    Retrieval-Augmented Generation (RAG) engine for the AI Chatbot.
    Uses pgvector (mocked here) to retrieve nutrition knowledge and 
    user history before querying the LLM.
    """
    
    def __init__(self):
        # We assume Ollama is running locally for the LLM
        self.llm_url = "http://localhost:11434/api/generate"
        
    def _detect_clinical_escalation(self, query: str) -> bool:
        """
        T-128: Escalation to human.
        Detects if the user is asking clinical/medical questions that 
        our AI is not legally allowed to answer without a human nutritionist.
        """
        clinical_keywords = [
            "diabetes", "cancer", "kidney", "renal", "pregnant", 
            "disease", "pain", "doctor", "blood pressure", "pcos"
        ]
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in clinical_keywords)
        
    def _retrieve_context(self, query: str, user_id: str) -> str:
        """
        T-126: RAG retrieval.
        Queries pgvector for relevant nutrition articles and user history.
        """
        # Mocking pgvector retrieval
        return "Context: The user's BMR is 1600. They prefer vegetarian food."

    async def generate_response(self, query: str, user_id: str) -> Dict[str, Any]:
        """
        Generates a contextual response to the user's chat message.
        """
        
        # 1. Check for clinical escalation
        if self._detect_clinical_escalation(query):
            return {
                "type": "escalation",
                "message": "It sounds like you're asking a medical or clinical question. For your safety, I'm transferring this chat to a human clinical nutritionist. They will respond shortly."
            }
            
        # 2. Retrieve Context (RAG)
        context = self._retrieve_context(query, user_id)
        
        # 3. Call LLM (We mock the HTTP call here for the MVP architecture)
        # In reality, this would use httpx to call self.llm_url with the context + query
        mock_llm_response = f"Based on your profile, {query} is a great choice! Keep it up."
        
        return {
            "type": "ai_response",
            "message": mock_llm_response
        }

rag_engine = RAGEngine()

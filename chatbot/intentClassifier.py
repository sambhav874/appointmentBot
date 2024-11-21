class IntentClassifier:
    @staticmethod
    def classify_intent(query, intents):
        """
        Classify the user's intent based on keyword matching.
        Returns the most likely intent and confidence score.
        """
        query_lower = query.lower()
        
        # Check for multi-word intents first
        intent_matches = {}
        for intent, keywords in intents.items():
            # Count matches
            matches = sum(1 for keyword in keywords if keyword in query_lower)
            
            # Calculate confidence based on number of matches and query length
            if matches > 0:
                # Adjust confidence calculation
                confidence = (matches / len(keywords)) * 100
                intent_matches[intent] = confidence
        
        # Return the intent with highest confidence
        if intent_matches:
            top_intent = max(intent_matches, key=intent_matches.get)
            return top_intent, intent_matches[top_intent]
        
        return 'general', 0
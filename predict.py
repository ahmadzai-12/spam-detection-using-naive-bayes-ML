"""
Email Spam Detection - Prediction Module
Utility for making predictions with the trained model
"""

from model_training import SpamDetectionModel

class SpamPredictor:
    """Wrapper class for easy predictions"""
    
    def __init__(self, model_path='models/spam_model.pkl'):
        self.model = SpamDetectionModel()
        self.model.load_model(model_path)
    
    def predict_email(self, email_text):
        """Predict if an email is spam"""
        return self.model.predict(email_text)
    
    def batch_predict(self, emails):
        """Predict multiple emails at once"""
        results = []
        for email in emails:
            results.append(self.predict_email(email))
        return results


# Quick test function
def test_predictor():
    predictor = SpamPredictor()
    
    print("Spam Detection Predictor Ready!")
    print("-" * 50)
    
    while True:
        print("\nEnter email text (or 'quit' to exit):")
        email = input("> ")
        
        if email.lower() == 'quit':
            break
        
        if email.strip():
            result = predictor.predict_email(email)
            print(f"\nResult: {result['label']}")
            print(f"Confidence: {result['confidence']:.2f}%")
            print(f"Spam Probability: {result['spam_probability']:.2f}%")
            print(f"Ham Probability: {result['ham_probability']:.2f}%")


if __name__ == "__main__":
    test_predictor()
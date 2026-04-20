"""
Email Spam Detection System - Model Training Module
Uses Multinomial Naive Bayes with TF-IDF Vectorization
"""

import pandas as pd
import numpy as np
import re
import nltk
import pickle
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

# Download required NLTK data
nltk.download('stopwords')
from nltk.corpus import stopwords

class SpamDetectionModel:
    """Complete spam detection model with preprocessing, training, and prediction"""
    
    def __init__(self):
        self.vectorizer = None
        self.classifier = None
        self.stop_words = set(stopwords.words('english'))
        
    def clean_text(self, text):
        """
        Clean and preprocess email text
        Steps: lowercase, remove punctuation, remove stopwords
        """
        # Convert to lowercase
        text = text.lower()
    
        # Remove punctuation and special characters
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove stopwords
        words = text.split()
        words = [word for word in words if word not in self.stop_words]
        
        return ' '.join(words)
    
    def load_and_preprocess_data(self, csv_path):
        """Load dataset and apply preprocessing"""
        print("Loading dataset...")
        df = pd.read_csv(csv_path)
        
        # Display basic information
        print("\n=== Dataset Information ===")
        print(f"Dataset shape: {df.shape}")
        print("\nFirst 5 rows:")
        print(df.head())
        print("\nDataset info:")
        print(df.info())
        
        # Check class distribution
        print("\nClass Distribution:")
        print(df['label'].value_counts())
        print(f"Spam percentage: {df['label'].value_counts()['spam']/len(df)*100:.2f}%")
        print(f"Ham percentage: {df['label'].value_counts()['ham']/len(df)*100:.2f}%")
        
        # Clean text data
        print("\nPreprocessing text data...")
        df['cleaned_text'] = df['text'].apply(self.clean_text)
        
        # Convert labels to binary (spam=1, ham=0)
        df['label_binary'] = df['label'].map({'spam': 1, 'ham': 0})
        
        return df
    
    def train(self, csv_path, test_size=0.2):
        """Train the spam detection model"""
        # Load and preprocess data
        df = self.load_and_preprocess_data(csv_path)
        
        # Split features and target
        X = df['cleaned_text']
        y = df['label_binary']
        
        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        print(f"\nTraining set size: {len(X_train)}")
        print(f"Test set size: {len(X_test)}")
        
        # TF-IDF Vectorization
        print("\nApplying TF-IDF Vectorization...")
        self.vectorizer = TfidfVectorizer(
            max_features=5000,  # Limit features for efficiency
            ngram_range=(1, 2),  # Use unigrams and bigrams
            min_df=2,  # Ignore terms that appear in less than 2 documents
            max_df=0.95  # Ignore terms that appear in more than 95% of documents
        )
        
        X_train_tfidf = self.vectorizer.fit_transform(X_train)
        X_test_tfidf = self.vectorizer.transform(X_test)
        
        print(f"TF-IDF feature shape: {X_train_tfidf.shape}")
        
        # Train Multinomial Naive Bayes
        print("\nTraining Multinomial Naive Bayes classifier...")
        self.classifier = MultinomialNB(alpha=1.0)  # Laplace smoothing
        self.classifier.fit(X_train_tfidf, y_train)
        
        # Make predictions
        y_pred = self.classifier.predict(X_test_tfidf)
        
        # Evaluate model
        print("\n=== Model Evaluation ===")
        print(f"Accuracy: {accuracy_score(y_test, y_pred)*100:.2f}%")
        
        print("\nConfusion Matrix:")
        print(confusion_matrix(y_test, y_pred))
        
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred, target_names=['Ham', 'Spam']))
        
        return df, X_test, y_test, y_pred
    
    def save_model(self, model_path='models/spam_model.pkl'):
        """Save trained model and vectorizer to disk"""
        import os
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        model_data = {
            'classifier': self.classifier,
            'vectorizer': self.vectorizer,
            'stop_words': self.stop_words
        }
        
        with open(model_path, 'wb') as file:
            pickle.dump(model_data, file)
        
        print(f"\nModel saved successfully to {model_path}")
    
    def load_model(self, model_path='models/spam_model.pkl'):
        """Load trained model from disk"""
        with open(model_path, 'rb') as file:
            model_data = pickle.load(file)
        
        self.classifier = model_data['classifier']
        self.vectorizer = model_data['vectorizer']
        self.stop_words = model_data['stop_words']
        
        print(f"Model loaded successfully from {model_path}")
    
    def predict(self, email_text):
        """Predict if an email is spam or not"""
        # Clean the input text
        cleaned_text = self.clean_text(email_text)
        
        # Transform using the fitted vectorizer
        text_tfidf = self.vectorizer.transform([cleaned_text])
        
        # Predict
        prediction = self.classifier.predict(text_tfidf)[0]
        probability = self.classifier.predict_proba(text_tfidf)[0]
        
        result = {
            'is_spam': bool(prediction),
            'label': 'Spam' if prediction == 1 else 'Ham',
            'confidence': float(max(probability)) * 100,
            'spam_probability': float(probability[1]) * 100,
            'ham_probability': float(probability[0]) * 100
        }
        
        return result


def main():
    """Main function to train and save the model"""
    print("="*60)
    print("EMAIL SPAM DETECTION SYSTEM - MODEL TRAINING")
    print("="*60)
    
    # Create and train model
    model = SpamDetectionModel()
    
    # Train on dataset
    df, X_test, y_test, y_pred = model.train('data/spam_emails.csv')
    
    # Save the trained model
    model.save_model()
    
    # Test with sample emails
    print("\n=== Sample Predictions ===")
    test_emails = [
        "Congratulations! You've won a free lottery ticket. Click here to claim!",
        "Hi, can we reschedule our meeting to tomorrow? Thanks!",
        "URGENT: Your bank account has been compromised. Verify now!",
        "The project deadline has been extended to next week."
    ]
    
    for email in test_emails:
        result = model.predict(email)
        print(f"\nEmail: {email[:50]}...")
        print(f"Prediction: {result['label']} (Confidence: {result['confidence']:.2f}%)")


if __name__ == "__main__":
    main()
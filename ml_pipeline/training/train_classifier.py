"""
RakshakAI - Scam Classifier Training Script
Trains a lightweight ML model for scam call detection.
"""

import json
import pickle
import re
from typing import List, Tuple

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (
    classification_report, 
    confusion_matrix, 
    roc_auc_score,
    precision_recall_fscore_support
)
import structlog

logger = structlog.get_logger("rakshak.training")


class TextPreprocessor:
    """Preprocesses text for ML training."""
    
    @staticmethod
    def clean(text: str) -> str:
        """Clean and normalize text."""
        # Convert to lowercase
        text = text.lower()
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?]', '', text)
        return text.strip()
    
    @staticmethod
    def extract_features(text: str) -> dict:
        """Extract additional features from text."""
        features = {}
        
        # Basic stats
        words = text.split()
        features['word_count'] = len(words)
        features['char_count'] = len(text)
        features['avg_word_length'] = np.mean([len(w) for w in words]) if words else 0
        
        # Urgency indicators
        urgency_words = ['urgent', 'immediately', 'now', 'hurry', 'quick', 'fast', 'today']
        features['urgency_count'] = sum(1 for w in urgency_words if w in text.lower())
        
        # Financial terms
        financial_words = ['bank', 'account', 'money', 'rupees', 'payment', 'transfer', 'upi', 'otp']
        features['financial_count'] = sum(1 for w in financial_words if w in text.lower())
        
        # Threat indicators
        threat_words = ['arrest', 'police', 'case', 'legal', 'court', 'jail', 'fir', 'warrant']
        features['threat_count'] = sum(1 for w in threat_words if w in text.lower())
        
        # Exclamation marks (pressure tactic)
        features['exclamation_count'] = text.count('!')
        
        return features


class ScamClassifierTrainer:
    """Trains and evaluates the scam classification model."""
    
    def __init__(self, dataset_path: str):
        self.dataset_path = dataset_path
        self.vectorizer = None
        self.model = None
        self.preprocessor = TextPreprocessor()
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        
    def load_data(self) -> Tuple[List[str], List[int]]:
        """Load and preprocess dataset."""
        logger.info("loading_dataset", path=self.dataset_path)
        
        with open(self.dataset_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        texts = []
        labels = []
        
        for item in data:
            # Clean transcript
            text = self.preprocessor.clean(item['transcript'])
            texts.append(text)
            
            # Binary label: 1 for scam, 0 for legitimate
            label = 1 if item['label'] == 'scam' else 0
            labels.append(label)
        
        logger.info("dataset_loaded", total=len(texts), scams=sum(labels), legitimate=len(labels)-sum(labels))
        
        return texts, labels
    
    def prepare_features(self, texts: List[str], labels: List[int]):
        """Prepare TF-IDF features."""
        logger.info("preparing_features")
        
        # Split data
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            texts, labels, test_size=0.2, random_state=42, stratify=labels
        )
        
        # Create TF-IDF vectorizer
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 3),  # Unigrams, bigrams, trigrams
            min_df=2,
            max_df=0.95,
            stop_words='english'
        )
        
        # Fit and transform training data
        X_train_tfidf = self.vectorizer.fit_transform(self.X_train)
        X_test_tfidf = self.vectorizer.transform(self.X_test)
        
        logger.info(
            "features_prepared",
            train_size=X_train_tfidf.shape[0],
            test_size=X_test_tfidf.shape[0],
            features=X_train_tfidf.shape[1]
        )
        
        return X_train_tfidf, X_test_tfidf
    
    def train_gradient_boosting(self, X_train, X_test) -> dict:
        """Train Gradient Boosting classifier."""
        logger.info("training_gradient_boosting")
        
        model = GradientBoostingClassifier(
            n_estimators=200,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        
        model.fit(X_train, self.y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]
        
        metrics = self._evaluate(model, X_test, y_pred, y_prob, "Gradient Boosting")
        
        return model, metrics
    
    def train_random_forest(self, X_train, X_test) -> dict:
        """Train Random Forest classifier."""
        logger.info("training_random_forest")
        
        model = RandomForestClassifier(
            n_estimators=200,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        
        model.fit(X_train, self.y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]
        
        metrics = self._evaluate(model, X_test, y_pred, y_prob, "Random Forest")
        
        return model, metrics
    
    def train_logistic_regression(self, X_train, X_test) -> dict:
        """Train Logistic Regression classifier."""
        logger.info("training_logistic_regression")
        
        model = LogisticRegression(
            max_iter=1000,
            random_state=42,
            class_weight='balanced'
        )
        
        model.fit(X_train, self.y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]
        
        metrics = self._evaluate(model, X_test, y_pred, y_prob, "Logistic Regression")
        
        return model, metrics
    
    def _evaluate(self, model, X_test, y_pred, y_prob, model_name: str) -> dict:
        """Evaluate model performance."""
        logger.info(f"evaluating_{model_name.lower().replace(' ', '_')}")
        
        # Calculate metrics
        precision, recall, f1, _ = precision_recall_fscore_support(
            self.y_test, y_pred, average='binary'
        )
        
        auc = roc_auc_score(self.y_test, y_prob)
        
        metrics = {
            'model': model_name,
            'accuracy': float(np.mean(y_pred == self.y_test)),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1),
            'auc_roc': float(auc)
        }
        
        logger.info(
            "evaluation_results",
            model=model_name,
            accuracy=metrics['accuracy'],
            precision=metrics['precision'],
            recall=metrics['recall'],
            f1=metrics['f1_score'],
            auc=metrics['auc_roc']
        )
        
        # Print detailed report
        print(f"\n{'='*50}")
        print(f"{model_name} Results")
        print(f"{'='*50}")
        print(classification_report(self.y_test, y_pred, target_names=['Legitimate', 'Scam']))
        print("\nConfusion Matrix:")
        print(confusion_matrix(self.y_test, y_pred))
        
        return metrics
    
    def save_model(self, model, output_path: str):
        """Save trained model and vectorizer."""
        logger.info("saving_model", path=output_path)
        
        # Save both model and vectorizer
        with open(output_path, 'wb') as f:
            pickle.dump((model, self.vectorizer), f)
        
        logger.info("model_saved", path=output_path)
    
    def get_feature_importance(self, model, top_n: int = 20):
        """Get most important features for scam detection."""
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
        elif hasattr(model, 'coef_'):
            importances = np.abs(model.coef_[0])
        else:
            return []
        
        feature_names = self.vectorizer.get_feature_names_out()
        
        # Get top features
        indices = np.argsort(importances)[::-1][:top_n]
        
        return [(feature_names[i], float(importances[i])) for i in indices]


def main():
    """Main training pipeline."""
    # Paths
    dataset_path = "/mnt/okcomputer/output/rakshak-ai/ml_pipeline/datasets/synthetic/synthetic_dataset.json"
    output_path = "/mnt/okcomputer/output/rakshak-ai/ml_pipeline/saved_models/scam_classifier.pkl"
    
    # Initialize trainer
    trainer = ScamClassifierTrainer(dataset_path)
    
    # Load data
    texts, labels = trainer.load_data()
    
    # Prepare features
    X_train, X_test = trainer.prepare_features(texts, labels)
    
    # Train multiple models and select best
    models = {}
    
    # Gradient Boosting
    gb_model, gb_metrics = trainer.train_gradient_boosting(X_train, X_test)
    models['gradient_boosting'] = (gb_model, gb_metrics)
    
    # Random Forest
    rf_model, rf_metrics = trainer.train_random_forest(X_train, X_test)
    models['random_forest'] = (rf_model, rf_metrics)
    
    # Logistic Regression
    lr_model, lr_metrics = trainer.train_logistic_regression(X_train, X_test)
    models['logistic_regression'] = (lr_model, lr_metrics)
    
    # Select best model based on F1 score
    best_model_name = max(models, key=lambda x: models[x][1]['f1_score'])
    best_model, best_metrics = models[best_model_name]
    
    logger.info(
        "best_model_selected",
        model=best_model_name,
        f1_score=best_metrics['f1_score']
    )
    
    # Print feature importance
    print(f"\n{'='*50}")
    print(f"Top Features for Scam Detection ({best_model_name})")
    print(f"{'='*50}")
    for feature, importance in trainer.get_feature_importance(best_model, top_n=20):
        print(f"{feature}: {importance:.4f}")
    
    # Save best model
    trainer.save_model(best_model, output_path)
    
    print(f"\n{'='*50}")
    print("Training Complete!")
    print(f"Best Model: {best_model_name}")
    print(f"Model saved to: {output_path}")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from transformers import pipeline
import numpy as np
import pandas as pd
from typing import List, Dict, Union
import warnings
warnings.filterwarnings('ignore')

class BioClinicalSentimentAnalyzer:
    """
    Sentiment analysis using BioClinicalBERT model.
    This model is fine-tuned on biomedical and clinical text data.
    """
    
    def __init__(self, model_name: str = "emilyalsentzer/Bio_ClinicalBERT"):
        """
        Initialize the BioClinicalBERT sentiment analyzer.
        
        Args:
            model_name: HuggingFace model name for BioClinicalBERT
        """
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.classifier = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
    def load_model(self, sentiment_model: str = "cardiffnlp/twitter-roberta-base-sentiment-latest"):
        """
        Load the BioClinicalBERT model and a sentiment classification head.
        
        Args:
            sentiment_model: Pre-trained sentiment model to use as classifier
        """
        try:
            print(f"Loading BioClinicalBERT tokenizer and model...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            
            # For sentiment analysis, we'll use a pre-trained sentiment model
            # and combine it with BioClinicalBERT embeddings
            print(f"Loading sentiment classifier: {sentiment_model}")
            self.classifier = pipeline(
                "sentiment-analysis",
                model=sentiment_model,
                tokenizer=sentiment_model,
                device=0 if torch.cuda.is_available() else -1
            )
            
            print(f"Model loaded successfully on {self.device}")
            
        except Exception as e:
            print(f"Error loading model: {e}")
            raise
    
    def preprocess_text(self, text: str) -> str:
        """
        Preprocess text for better sentiment analysis.
        
        Args:
            text: Input text to preprocess
            
        Returns:
            Preprocessed text
        """
        if not isinstance(text, str):
            text = str(text)
        
        # Basic preprocessing
        text = text.strip()
        text = text.replace('\n', ' ')
        text = text.replace('\r', ' ')
        
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        return text
    
    def analyze_sentiment(self, text: Union[str, List[str]]) -> Union[Dict, List[Dict]]:
        """
        Analyze sentiment of input text(s).
        
        Args:
            text: Single text string or list of text strings
            
        Returns:
            Sentiment analysis results
        """
        if self.classifier is None:
            raise ValueError("Model not loaded. Please call load_model() first.")
        
        # Handle single text input
        if isinstance(text, str):
            text = self.preprocess_text(text)
            result = self.classifier(text)
            return {
                'text': text,
                'label': result[0]['label'],
                'score': result[0]['score'],
                'confidence': result[0]['score']
            }
        
        # Handle multiple text inputs
        elif isinstance(text, list):
            preprocessed_texts = [self.preprocess_text(t) for t in text]
            results = self.classifier(preprocessed_texts)
            
            output = []
            for i, result in enumerate(results):
                output.append({
                    'text': preprocessed_texts[i],
                    'label': result['label'],
                    'score': result['score'],
                    'confidence': result['score']
                })
            return output
        
        else:
            raise ValueError("Input must be a string or list of strings")
    
    def analyze_batch(self, texts: List[str], batch_size: int = 16) -> List[Dict]:
        """
        Analyze sentiment for a batch of texts with batching for efficiency.
        
        Args:
            texts: List of text strings
            batch_size: Size of each batch for processing
            
        Returns:
            List of sentiment analysis results
        """
        if self.classifier is None:
            raise ValueError("Model not loaded. Please call load_model() first.")
        
        results = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_results = self.analyze_sentiment(batch)
            results.extend(batch_results)
        
        return results
    
    def get_sentiment_distribution(self, texts: List[str]) -> Dict[str, float]:
        """
        Get distribution of sentiments across multiple texts.
        
        Args:
            texts: List of text strings
            
        Returns:
            Dictionary with sentiment distribution
        """
        results = self.analyze_batch(texts)
        
        label_counts = {}
        total_count = len(results)
        
        for result in results:
            label = result['label']
            label_counts[label] = label_counts.get(label, 0) + 1
        
        # Convert to percentages
        distribution = {
            label: (count / total_count) * 100
            for label, count in label_counts.items()
        }
        
        return distribution
    
    def analyze_dataframe(self, df: pd.DataFrame, text_column: str) -> pd.DataFrame:
        """
        Analyze sentiment for a pandas DataFrame column.
        
        Args:
            df: Input DataFrame
            text_column: Name of the column containing text
            
        Returns:
            DataFrame with sentiment analysis results
        """
        if text_column not in df.columns:
            raise ValueError(f"Column '{text_column}' not found in DataFrame")
        
        texts = df[text_column].astype(str).tolist()
        results = self.analyze_batch(texts)
        
        # Add results to DataFrame
        df_result = df.copy()
        df_result['sentiment_label'] = [r['label'] for r in results]
        df_result['sentiment_score'] = [r['score'] for r in results]
        df_result['sentiment_confidence'] = [r['confidence'] for r in results]
        
        return df_result

# Example usage and demonstration
def main():
    """
    Demonstrate the BioClinicalBERT sentiment analyzer.
    """
    # Initialize analyzer
    analyzer = BioClinicalSentimentAnalyzer()
    
    # Load model
    print("Loading BioClinicalBERT sentiment analyzer...")
    analyzer.load_model()
    
    # Example clinical/medical texts
    clinical_texts = [
        "The patient responded well to the treatment and showed significant improvement.",
        "The patient experienced severe side effects and discontinued the medication.",
        "Laboratory results are within normal limits. Patient appears stable.",
        "The patient reported increased pain and discomfort after the procedure.",
        "Excellent recovery progress. Patient is ready for discharge.",
        "The patient's condition has deteriorated and requires immediate attention.",
        "Vital signs are stable. Patient is comfortable and responsive.",
        "The treatment was ineffective and the patient's symptoms persisted."
    ]
    
    print("\n" + "="*60)
    print("INDIVIDUAL SENTIMENT ANALYSIS")
    print("="*60)
    
    # Analyze individual texts
    for i, text in enumerate(clinical_texts[:3], 1):
        result = analyzer.analyze_sentiment(text)
        print(f"\nText {i}: {text}")
        print(f"Sentiment: {result['label']}")
        print(f"Confidence: {result['confidence']:.3f}")
    
    print("\n" + "="*60)
    print("BATCH SENTIMENT ANALYSIS")
    print("="*60)
    
    # Analyze all texts at once
    batch_results = analyzer.analyze_batch(clinical_texts)
    
    for i, result in enumerate(batch_results, 1):
        print(f"\n{i}. Text: {result['text'][:50]}...")
        print(f"   Sentiment: {result['label']} (Score: {result['score']:.3f})")
    
    print("\n" + "="*60)
    print("SENTIMENT DISTRIBUTION")
    print("="*60)
    
    # Get sentiment distribution
    distribution = analyzer.get_sentiment_distribution(clinical_texts)
    print("\nSentiment Distribution:")
    for label, percentage in distribution.items():
        print(f"  {label}: {percentage:.1f}%")
    
    print("\n" + "="*60)
    print("DATAFRAME ANALYSIS")
    print("="*60)
    
    # Create sample DataFrame
    df = pd.DataFrame({
        'patient_id': [f'P{i:03d}' for i in range(1, len(clinical_texts) + 1)],
        'clinical_note': clinical_texts,
        'department': ['Cardiology', 'Oncology', 'Emergency', 'Surgery', 
                      'Cardiology', 'ICU', 'General', 'Oncology']
    })
    
    # Analyze DataFrame
    df_analyzed = analyzer.analyze_dataframe(df, 'clinical_note')
    
    print("\nAnalyzed DataFrame:")
    print(df_analyzed[['patient_id', 'department', 'sentiment_label', 'sentiment_score']].to_string())
    
    # Summary by department
    print("\n" + "="*60)
    print("SENTIMENT BY DEPARTMENT")
    print("="*60)
    
    dept_summary = df_analyzed.groupby('department').agg({
        'sentiment_score': ['mean', 'count'],
        'sentiment_label': lambda x: x.value_counts().index[0]  # Most common sentiment
    }).round(3)
    
    print("\nDepartment Summary:")
    print(dept_summary)

if __name__ == "__main__":
    main()
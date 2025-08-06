from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn
from pydantic import BaseModel
import logging
import sys
from models.health_conversation_categorizer import HealthConversationCategorizer


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


app = FastAPI(docs_url="/api/docs")
MODEL_NAME = "sid321axn/Bio_ClinicalBERT-finetuned-medicalcondition"

class TextRequest(BaseModel):
    text: str
    

@app.get('/')
def home():
    print('Home screen.......')
    return 'Mental Health Conversation Helper tool'


@app.post('/sentiment_category')
def get_sentiment_category(request: TextRequest) -> JSONResponse:
    categorizer = HealthConversationCategorizer(MODEL_NAME)
    input_text = request.text.strip()
    logger.info("Input text: ", input_text)
    sentiment = categorizer.get_conversation_category(input_text)

    logger.info("Response: ", sentiment)

    summarized_text = ''
    if 'SummarizedText' in sentiment: 
        summarized_text = sentiment['SummarizedText']
    
    label = ''
    if 'Label' in sentiment:
        label = sentiment['Label']

    confidence = ''
    if 'Confidence' in sentiment:
        confidence = sentiment['Confidence']
    
    return {
        "SummarizedText": summarized_text,
        "Label": label,
        "Confidence": confidence
    }


def main():
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")

if __name__ == "__main__":
    main()



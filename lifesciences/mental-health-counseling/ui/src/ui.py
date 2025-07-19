import streamlit as st
import requests
from time import time 

DEFAULT_API_URL = "http://127.0.0.1:8000"

def call_sentiment_category(text:str, api_url:str, timeout:int=30):
    try:
        # start_time = time()
        payload = {
            "text": text
        }

        response = requests.post(api_url, json=payload, timeout=timeout)
        # end_time = time()

        if response.status_code == 200:
            result = response.json()
            return True, result
        else : 
            try:
                error_detail = response.json()
                return False, f"API error response: {response.status_code} with Message: {error_detail}"
            except:
                return False, f"API error {response.status_code}, Text: {response.text}"
            
    except requests.exceptions.ConnectionError:
        return False, f"Unable to connect to API {api_url}. Make sure the server is up and running"
    except requests.exceptions.Timeout:
        return False, f"Request timed out after {timeout} seconds"
    except Exception as e:
        return False, f"Error: {str(e)}"
    

def main():
    st.set_page_config(page_title="Mental Health Counseling", layout="wide")
    st.title("Mental Health Counseling Tool")
    st.subheader("Enter Patients feelings to understand their sentiment")

    # st.header("Text Input")
    user_input = st.text_area("Enter Patient's statement here", height=300, placeholder="Type or paste text here..")
    get_sentiment_button = st.button("Get Patient Sentiment", use_container_width=True)

    if get_sentiment_button and user_input:
        success, patient_sentiment = call_sentiment_category(user_input, f"{DEFAULT_API_URL}/sentiment_category")
        if success : 
            st.success("Data sent successfully")

            st.title("Response: ")
            label = patient_sentiment.get("Label")
            confidence = patient_sentiment.get("Confidence")
            summarized_text = patient_sentiment.get("SummarizedText")

            # col1, col2 = st.columns(2)
            # with col1 : 
            st.metric("Sentiment", label)
            st.metric("Confidence", confidence)
            if summarized_text.strip():
                st.metric("Summarized Text", summarized_text)
            
            # st.write(patient_sentiment)
        else:
            st.error("Failed to get valid response from the API")
    elif get_sentiment_button and not user_input:
        st.warning("Please enter some text to process")
    elif not get_sentiment_button :
        st.info("Enter text and click 'Get Patient Sentiment' button")


if __name__ == "__main__":
    main()
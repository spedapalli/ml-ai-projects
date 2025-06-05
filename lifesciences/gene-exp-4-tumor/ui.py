import streamlit as st
import requests
import pandas as pd
from time import time
from datetime import datetime
from io import BytesIO

DEFAULT_API_URL = "http://127.0.0.1:8000/predict"


# sourced from claude
def call_prediction_api(uploaded_file, api_url, timeout=30):
    """
    Call the FastAPI prediction endpoint with uploaded CSV file
    """
    try:
        # Reset file pointer to beginning
        uploaded_file.seek(0)

        # Prepare files for API call
        files = {
            'file': (uploaded_file.name, uploaded_file, 'text/csv')
        }

        # Make API call with timeout
        start_time = time()
        response = requests.post(api_url, files=files, timeout=timeout)
        end_time = time()

        response_time = round(end_time - start_time, 2)

        if response.status_code == 200:
            result = response.json()
            return True, result, response_time
        else:
            try:
                error_detail = response.json()
                return False, f"API Error {response.status_code}: {error_detail}", response_time
            except:
                return False, f"API Error {response.status_code}: {response.text}", response_time

    except requests.exceptions.ConnectionError:
        return False, "Could not connect to API. Make sure the server is running.", 0
    except requests.exceptions.Timeout:
        return False, f"Request timed out after {timeout} seconds.", timeout
    except Exception as e:
        return False, f"Error: {str(e)}", 0



def validate_csv_data(df, expected_columns=None):
    """
    Validate the uploaded CSV data
    """
    issues = []

    # Check for empty dataframe
    if df.empty:
        issues.append("The CSV file is empty")

    # Check for missing values
    missing_values = df.isnull().sum().sum()
    if missing_values > 0:
        issues.append(f"Found {missing_values} missing values")

    # Check expected columns (if provided)
    if expected_columns and len(df.columns) != expected_columns:
        issues.append(f"Expected {expected_columns} columns, found {len(df.columns)}")

    # Check for non-numeric data (assuming gene expression data should be numeric)
    numeric_columns = df.select_dtypes(include=['number']).columns
    if len(numeric_columns) < len(df.columns):
        non_numeric = len(df.columns) - len(numeric_columns)
        issues.append(f"Found {non_numeric} non-numeric columns")

    return issues


def main():
    st.set_page_config(page_title="Cancer Tumor prediction given set of gene expressions",
                       layout="wide")

    st.title("Cancer Tumor prediction given set of gene expressions")
    st.subheader("Upload a CSV file with (18604) gene expression data")

    with st.sidebar:
        st.header("Configuration")

        # API URL config
        api_url = st.text_input("API_URL",
                                value=DEFAULT_API_URL,
                                help="Enter the URL of your FastAPI prediction endpoint")

        # response wait time
        timeout = st.slider("Request Timout (seconds)",
                            min_value = 5,
                            max_value = 120,
                            value = 30,
                            help="Maximum time to wait for API response")

        expected_cols = st.number_input("Expected columns (optional)",
                                        #min_value=18604,
                                        value=18604,
                                        help="Set to 0 to skip column count validation")

        st.markdown("---")

        # API Status check
        if st.button("Test API Connection"):
            with st.spinner("Testing connection....."):
                try:
                    response = requests.get(api_url.replace('/predict', '/'), timeout=5)
                    if response.status_code == 200 :
                        st.success('API is reachable')
                    else :
                        st.warning(f'API returned status code {response.status_code}')
                except:
                    st.error('Cannot reach API URL')


    # Main body on the page
    # file upload
    uploaded_file = st.file_uploader("CSV file",
                                    type=['csv'],
                                    help="Upload a CSV file containing 18604 gene expressions")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Data validation and Preview")

        if uploaded_file is not None:
            st.success(f"File uploaded: {uploaded_file.name}")

            file_details = {
                "Filename": uploaded_file.name,
                "File size": f"{len(uploaded_file.getvalue()):,} bytes",
                "Upload time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            }

            with st.expander("File Details"):
                for key, value in file_details.items():
                    st.write(f"**{key}:** {value}")

            #preview
            try :
                # create copy for preview
                file_copy = BytesIO(uploaded_file.getvalue())
                df = pd.read_csv(file_copy, index_col=0)    #set index_col. Dont want index col to be converted into a column of its own

                st.subheader("Data Preview")

                info_col1, info_col2, info_col3 = st.columns(3)
                with info_col1:
                    st.metric("Rows", f"{df.shape[0]:,}")
                with info_col2:
                    st.metric("Columns", f"{df.shape[1]:,}")
                with info_col3:
                    st.metric("Memory Usage", f"{df.memory_usage(deep=True).sum() / 1024:.1f} KB")

                #data validation
                validation_issues = validate_csv_data(df,
                                                    expected_columns = expected_cols if expected_cols > 0 else None)


                if validation_issues:
                    st.warning("Data validation failed. See below: ")
                    for issue in validation_issues:
                        st.write(f"{issue}")
                else :
                    st.success("Data validation successful")

                with st.expander("View Sample Data"):
                    st.dataframe(df.head(5), use_container_width=True)

                #statistics - given large # of features, we will not output this.
                # with st.expander("Basic Statistics"):
                #     numeric_df = df.select_dtypes(include=['number'])
                #     if not numeric_df.empty:
                #         st.dataframe(numeric_df.describe(), use_container_width=True)
                #     else:
                #         st.write("No numeric columns found for statistics")

            except:
                st.error(f"Error reading CSV file: {str(e)}")
                return

    with col2:
        st.subheader("Predict which Cancer Tumor it could be")

        if uploaded_file is not None:
            if st.button("Get Prediction", type='primary', use_container_width=True):
                with st.spinner("Processing...."):
                    success, result, response_time = call_prediction_api(uploaded_file=uploaded_file,
                                                                        api_url=DEFAULT_API_URL,
                                                                        timeout=timeout)

                    if success:
                        st.success("Prediction successful")

                        prediction = result.get('prediction', "Unable to Predict")

                        st.write("Predicted Class")
                        st.dataframe(prediction, height=300)
                        # st.write('\n'.join(str(val) for val in prediction))
                        st.write(f"Response time: {response_time}sec")
                        # st.metric(label="Predicted Class",
                        #         value='\n'.join(str(val) for val in prediction),
                        #         delta=f"Response time: {response_time}sec")

                        if 'confidence' in result:
                            st.metric('Confidence: ', f"{result['confidence']:.2%}")

                        # full response
                        with st.expander("Full API Response"):
                            st.json(result)

                        #save results option
                        if st.button("Save Results"):
                            results_data = {
                                'timestamp': datetime.now().isoformat(),
                                'filename' : uploaded_file.name,
                                'prediction' : prediction,
                                'response_time' : response_time,
                                'full_response' : result
                            }

                            json_str = json.dumps(results_data, indent=2)
                            st.download_button(label="Download Results as JSON",
                                            data=json_str,
                                            file_name=f"prediction_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                                mime="application/json")

                    else:
                        st.error("Prediction failed:")
                        st.error(result)

        else :
            st.info("Upload a CSV file first")

    st.markdown("---")
    st.markdown("NOTE: Ensure the fastAPI server is up and running")



# # upload file - old code
# uploaded_file = st.file_uploader(label='Upload CSV file', type='csv')

# if uploaded_file is not None and st.button("Predict"):
#     df = pd.read_csv(uploaded_file)
#     file_content = df.to_dict('records')

#     # with open(uploaded_file, 'rb') as file:
#     #     file_content = file.read()

#     # datafiles = {'file': ('xgb_X_after_pca_dataset.csv', file_content, 'text/csv')}
#     # payload = {}

#     response = requests.post(url, files = file_content)
#     json_response = response.json()
#     prediction = json_response.get('prediction', None)
#     # print('Prediction: \n', prediction)
#     if prediction is not None:
#         prediction_list = list(prediction)
#         pred_values = '\n'.join(val for val in prediction_list)
#         st.write(pred_values)

if __name__ == "__main__":
    main()
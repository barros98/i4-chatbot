import requests
import streamlit as st

def get_api_response(question, session_id, model):
    if not st.session_state.get("openai_api_key"):
        st.error("Please enter your OpenAI API key in the sidebar!")
        return None

    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'X-OpenAI-Key': st.session_state.openai_api_key
    }
    data = {"question": question, "model": model}
    if session_id:
        data["session_id"] = session_id

    try:
        response = requests.post("http://backend:8000/chat", headers=headers, json=data)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API request failed with status code {response.status_code}: {response.text}")
            return None
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return None

def upload_document(file, api_key):
    try:
        files = {"file": (file.name, file, file.type)}
        headers = {'X-OpenAI-Key': api_key}
        response = requests.post("http://backend:8000/upload-doc", files=files, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to upload file. Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"An error occurred while uploading the file: {str(e)}")
        return None

def list_documents():
    try:
        response = requests.get("http://backend:8000/list-docs")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch document list. Error: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        st.error(f"An error occurred while fetching the document list: {str(e)}")
        return []

def delete_document(file_id):
    if not st.session_state.get("openai_api_key"):
        st.error("Please enter your OpenAI API key in the sidebar!")
        return None

    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'X-OpenAI-Key': st.session_state.openai_api_key
    }
    data = {"file_id": file_id}

    try:
        response = requests.post("http://backend:8000/delete-doc", headers=headers, json=data)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to delete document. Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"An error occurred while deleting the document: {str(e)}")
        return None

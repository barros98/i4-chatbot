from fastapi import FastAPI, File, UploadFile, HTTPException, Header, Depends
from pydantic_models import QueryInput, QueryResponse, DocumentInfo, DeleteFileRequest
from langchain_utils import get_rag_chain, set_openai_api_key
from db_utils import insert_application_logs, get_chat_history, get_all_documents, insert_document_record, delete_document_record
from chroma_utils import index_document_to_chroma, delete_doc_from_chroma
import os
import uuid
import logging
import shutil
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from fastapi.responses import JSONResponse

# Set up logging
logging.basicConfig(filename='app.log', level=logging.INFO)

# Initialize FastAPI app
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Você deve configurar isso adequadamente em produção
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def get_api_key(x_openai_key: Optional[str] = Header(None)) -> str:
    if not x_openai_key:
        raise HTTPException(status_code=401, detail="OpenAI API Key is required")
    return x_openai_key

@app.get("/health")
async def health_check():
    try:
        # Verificar se o diretório de dados existe
        os.makedirs("/app/data", exist_ok=True)
        
        # Verificar se podemos escrever no diretório
        test_file = "/app/data/test.txt"
        with open(test_file, "w") as f:
            f.write("test")
        os.remove(test_file)
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "healthy",
                "service": "chatbot-api",
                "timestamp": str(uuid.uuid4())
            }
        )
    except Exception as e:
        logging.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )

@app.get("/")
def root():
    return {"message": "API FastAPI está rodando com sucesso!"}

# --- Chat Endpoint ----------------------------------------------------------------------------------------------------------------------------------------------------
@app.post("/chat", response_model=QueryResponse)
async def chat(query_input: QueryInput, api_key: str = Depends(get_api_key)):
    set_openai_api_key(api_key)
    session_id = query_input.session_id or str(uuid.uuid4())
    logging.info(f"Session ID: {session_id}, User Query: {query_input.question}, Model: {query_input.model.value}")

    chat_history = get_chat_history(session_id)
    rag_chain = get_rag_chain(query_input.model.value)
    answer = rag_chain.invoke({
        "input": query_input.question,
        "chat_history": chat_history
    })['answer']

    insert_application_logs(session_id, query_input.question, answer, query_input.model.value)
    logging.info(f"Session ID: {session_id}, AI Response: {answer}")
    return QueryResponse(answer=answer, session_id=session_id, model=query_input.model)

# --- Upload Endpoint ----------------------------------------------------------------------------------------------------------------------------------------------------
@app.post("/upload-doc")
async def upload_and_index_document(
    file: UploadFile = File(...),
    api_key: str = Depends(get_api_key)
):
    set_openai_api_key(api_key)
    allowed_extensions = ['.pdf', '.docx', '.html']
    file_extension = os.path.splitext(file.filename)[1].lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Unsupported file type. Allowed types are: {', '.join(allowed_extensions)}")

    temp_file_path = f"temp_{file.filename}"

    try:
        # Save the uploaded file to a temporary file
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_id = insert_document_record(file.filename)
        success = index_document_to_chroma(temp_file_path, file_id)

        if success:
            return {"message": f"File {file.filename} has been successfully uploaded and indexed.", "file_id": file_id}
        else:
            delete_document_record(file_id)
            raise HTTPException(status_code=500, detail=f"Failed to index {file.filename}.")
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

# --- List Documents Endpoint ----------------------------------------------------------------------------------------------------------------------------------------------------
@app.get("/list-docs", response_model=list[DocumentInfo])
def list_documents():
    return get_all_documents()

# --- Delete Documents Endpoint ----------------------------------------------------------------------------------------------------------------------------------------------------
@app.post("/delete-doc")
async def delete_document(
    request: DeleteFileRequest,
    api_key: str = Depends(get_api_key)
):
    set_openai_api_key(api_key)
    chroma_delete_success = delete_doc_from_chroma(request.file_id)

    if chroma_delete_success:
        db_delete_success = delete_document_record(request.file_id)
        if db_delete_success:
            return {"message": f"Successfully deleted document with file_id {request.file_id} from the system."}
        else:
            return {"error": f"Deleted from Chroma but failed to delete document with file_id {request.file_id} from the database."}
    else:
        return {"error": f"Failed to delete document with file_id {request.file_id} from Chroma."}





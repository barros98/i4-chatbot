from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from typing import List
from langchain_core.documents import Document
import os
from chroma_utils import vectorstore

retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

output_parser = StrOutputParser()


# Reformula a pergunta do usuário se baseando no histórico da conversa
contextualize_q_system_prompt = """
Dado um histórico de conversa e a pergunta mais recente do usuário, a qual pode fazer referência a esse histórico, 
formule uma pergunta independente que possa ser compreendida sem a necessidade do histórico da conversa. NÃO responda à pergunta,
apenas reformule-a se necessário ou retorne-a como está.
"""
contextualize_q_prompt = ChatPromptTemplate.from_messages([
    ("system", contextualize_q_system_prompt),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])

# Gera a resposta final do LLM se baseando no conteúdo do retrieve e no histórico do chat
qa_prompt = ChatPromptTemplate.from_messages([
    ("system", "Você é um assistente de IA ajudante. Use o seguinte contexto para responder a pergunta do usuário."),
    ("system", "Context: {context}"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}")
])


# RAG Chain
def get_rag_chain(model="gpt-4o-mini", api_key=None):
    if not api_key:
        raise ValueError("API key is required")
    
    llm = ChatOpenAI(model=model, api_key=api_key)
    history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_q_prompt)
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)    
    return rag_chain











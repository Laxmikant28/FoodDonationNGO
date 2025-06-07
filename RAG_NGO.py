import os
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
import warnings
from langchain_huggingface import HuggingFaceEmbeddings
warnings.filterwarnings("ignore")
from langchain_ollama import OllamaEmbeddings
from dotenv import load_dotenv
load_dotenv() 

os.environ['HF_TOKEN'] = os.getenv('HF_TOKEN', '')
# # Read the NGO_Info 
documents = []
        
# Create NGO information text file if it doesn't exist
ngo_info_file = "NGO_INFO.txt"
        # 
loader = TextLoader(ngo_info_file)
documents.extend(loader.load())
text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=200,
            chunk_overlap=20,
        #     length_function=len,
            separators=["\n\n", "\n"]
        )

text_chunks = text_splitter.split_documents(documents)
 
embeddings = HuggingFaceEmbeddings(
    model="all-MiniLM-L6-v2",
)

vectorstore = FAISS.from_documents(
            documents=text_chunks,
            embedding=embeddings
        )

vectorstore.save_local("ngo_vectorstore")

# # Step-by-Step RAG Implementation
# # Using LangChain, TextLoader, FAISS, RecursiveTextSplitter, and Groq

# # Step 1: Import Required Libraries
# import os
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain.embeddings import HuggingFaceEmbeddings
# from langchain.vectorstores import FAISS
# from langchain.chains import RetrievalQA
# from langchain_groq import ChatGroq
# from langchain.prompts import PromptTemplate


# # Step 7: Set up Groq LLM
# llm = ChatGroq(
# #     groq_api_key=os.environ["GROQ_API_KEY"],
#     model_name="gemma2-9b-it",  # You can also use "llama2-70b-4096"
#     temperature=0.5
# )

# loaded_vectorstore = FAISS.load_local("ngo_vectorstore", embeddings, allow_dangerous_deserialization=True)

# # Step 8: Create Custom Prompt Template
# prompt_template = """
# You are a helpful assistant for Hope Harvest Foundation, a food donation NGO. 
# Use the following context to answer the question about the NGO.

# Context: {context}

# Question: {question}

# Please provide a helpful and accurate answer based on the context provided. 
# If the question is not related to the NGO or cannot be answered from the context, 
# politely redirect the user to ask about NGO-related topics.

# Answer:
# """

# PROMPT = PromptTemplate(
#     template=prompt_template,
#     input_variables=["context", "question"]
# )

# # Step 9: Create Retrieval QA Chain
# qa_chain = RetrievalQA.from_chain_type(
#     llm=llm,
#     chain_type="stuff",
#     retriever=loaded_vectorstore.as_retriever(
#         search_type="similarity",
#         search_kwargs={"k": 3}  # Retrieve top 3 most similar chunks
#     ),
#     chain_type_kwargs={"prompt": PROMPT},
#     return_source_documents=True
# )

# while True:
#     user_question = input("\n👤 Your Question: ")
    
#     if user_question.lower() in ['quit', 'exit', 'bye']:
#         print("👋 Thank you for learning about Hope Harvest Foundation!")
#         break
    
#     if user_question.strip() == "":
#         continue
    
#     try:
#         # Get response from RAG system
#         result = qa_chain({"query": user_question})
#         print(f"\n🤖 Answer: {result['result']}")
        
#     except Exception as e:
#         print(f"❌ Error: {e}")
#         print("Please try again with a different question.")




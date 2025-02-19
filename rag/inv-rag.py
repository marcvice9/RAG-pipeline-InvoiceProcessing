# 1. Ingest PDF Files
from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain_community.document_loaders import OnlinePDFLoader
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.document_loaders.image import UnstructuredImageLoader
from pdf2image import convert_from_path
import os

doc_path = "./invoices/galile.pdf"
model = "llama3.2"

print("Starting script")

if os.path.exists(doc_path):
    print("PDF file exists")

    print("Attempting to create images...")
    images = convert_from_path(doc_path, dpi=300, poppler_path=r'Release-24.08.0-0\poppler-24.08.0\Library\bin')
    print("Images created successfully")

    images_path = []

    for i, image in enumerate(images):
        image_name = doc_path.split('/')[-1].split('.')[0]
        image_path = os.path.abspath(f"./invoices-images/{image_name}.png")
        image.save(image_path, "PNG")
        images_path.append(image_path)

    print(f"Stored {len(images)} images in invoices-images folder")
    
    loader = UnstructuredImageLoader(file_path=images_path[0])
    print("UnstructuredImageLoader created successfully")
    
    try:
        print("Attempting to load the image...")
        data = loader.load()
        print("Images loaded successfully")
        #print(data)

        content = data[0].page_content
        #print(content[:100])
    
    except Exception as e:
        print(f"Error loading images: {e}")

else:
    print("Missing PDF file")

# 2. Extract Text from PDF Files and split into small chunks

from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma

# Split and chunk
print("Splitting text into chunks...")
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=300)
chunks = text_splitter.split_documents(data)
print("Text split into chunks successfully")

# print(f"Number of chunks: {len(chunks)}")
# print(f"First chunk: {chunks[0]}")

# 3. Convert chunks into vectors using embedding model & save embeddings to a vector db

import ollama
ollama.pull("nomic-embed-text")

print("Attempting to create embeddings and store in Vector db...")
vector_db = Chroma.from_documents(
    documents=chunks,
    embedding=OllamaEmbeddings(model="nomic-embed-text"),
    collection_name="invoices-rag"
)

print("Embeddings saved to vector db successfully")

# 6. Retrieval

from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_ollama import ChatOllama
from langchain_core.runnables import RunnablePassthrough
import cfg.config as cfg

print("Initializing ChatOllama...")
llm = ChatOllama(model=model)

print("Attempting to create retriever...")
retriever = vector_db.as_retriever()
print("Retriever succesfully created...")

# Specify the invoice to process
query = f"Retrieve information for invoice {cfg.INVOICE_NAME}"

print("Generating answer based on the prompt...")
documents = retriever.get_relevant_documents(query)
context = " ".join([doc.page_content for doc in documents])

prompt = ChatPromptTemplate.from_template(cfg.PROMPT)

chain = (
    {"context": context, "INVOICE_NAME": cfg.INVOICE_NAME}
    | prompt
    | llm
    | JsonOutputParser()
)

res = chain.invoke()
print(res)

'''
print("Attempting to create ChatPromptTemplate...")
prompt = ChatPromptTemplate.from_template(PROMPT)
print("ChatPromptTemplate succesfully created")

print("Creating the chain...")
chain = (
    {"context": retriever, "INVOICE_NAME": INVOICE_NAME, "question": RunnablePassthrough()}
    | prompt
    | llm
    | JsonOutputParser()
)
print("Chain created successfully")

res = chain.invoke(input=("What is the total amount payable?"))

print(res)
'''
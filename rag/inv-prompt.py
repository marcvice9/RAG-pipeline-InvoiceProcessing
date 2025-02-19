# 1. Ingest PDF Files
from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain_community.document_loaders import OnlinePDFLoader
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.document_loaders.image import UnstructuredImageLoader
from pdf2image import convert_from_path
import os
import cfg.config as cfg


print("Starting script")

if os.path.exists(cfg.DOC_PATH):
    print("PDF file exists")

    print("Attempting to create images...")
    images = convert_from_path(cfg.DOC_PATH, dpi=300, poppler_path=r'Release-24.08.0-0\poppler-24.08.0\Library\bin')
    print("Images created successfully")

    images_path = []

    for i, image in enumerate(images):
        image_name = cfg.DOC_PATH.split('/')[-1].split('.')[0]
        image_path = os.path.abspath(f"./invoices-images/{image_name}.png")
        image.save(image_path, "PNG")
        images_path.append(image_path)

    print(f"Stored {len(images)} images in invoices-images folder")
    
    loader = UnstructuredImageLoader(file_path=images_path[0], mode="elements")
    print("UnstructuredImageLoader created successfully")
    
    try:
        print("Attempting to load the image...")
        data = loader.load()
        print("Images loaded successfully")
        print(data)

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
text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=300)
chunks = text_splitter.split_documents(data)
print("Text split into chunks successfully")

print(f"Type of chunks: {type(chunks)}")
print(f"Number of chunks: {len(chunks)}")
print(f"First chunk: {chunks[0]}")
print(f"Type of first chunk: {type(chunks[0])}")

# Concatenate the content of all chunks into a single string
invoice_data = " ".join([chunk.page_content for chunk in chunks])

# 6. Retrieval

from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_ollama import ChatOllama
import cfg.config as cfg

print("Initializing ChatOllama...")
llm = ChatOllama(model=cfg.MODEL)

prompt_template = ChatPromptTemplate.from_messages(cfg.MESSAGES)
prompt = prompt_template.invoke({"INVOICE_DATA": invoice_data})
res = llm.invoke(prompt)
print(res.content)
# 1. Ingest PDF Files
from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain_community.document_loaders import OnlinePDFLoader
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.document_loaders.image import UnstructuredImageLoader
from langchain.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from pdf2image import convert_from_path
import cv2
import pytesseract
import numpy as np
import os
import sys

# Adding the project's root directory to sys.path to enable importing modules from sibling folders.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from cfg import rag_config as cfg

def correct_image_orientation_with_ocr(image_path):
    # Load the image
    image = cv2.imread(image_path)

    # Convert the image to grayscale
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2GRAY)
    
    # Run Tesseract OCR to get orientation info
    details = pytesseract.image_to_osd(gray)
    
    # Parse the orientation from the OCR output
    if 'Rotate: 90' in details:
        # Rotate 90 degrees clockwise
        image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
    elif 'Rotate: 180' in details:
        # Rotate 180 degrees
        image = cv2.rotate(image, cv2.ROTATE_180)
    elif 'Rotate: 270' in details:
        # Rotate 270 degrees counterclockwise (or 90 degrees clockwise)
        image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
    
    # If no rotation info is found, return the image as is
    return image


print("Initializing ChatOllama...")
llm = ChatOllama(model=cfg.MODEL)

print("Starting script")

if os.path.exists(cfg.DOC_PATH):
    print("PDF file exists")

    print("Attempting to create images...")
    images = convert_from_path(cfg.DOC_PATH, dpi=300, poppler_path=r'Release-24.08.0-0\poppler-24.08.0\Library\bin')
    print("Images created successfully")

    images_path = []

    for i, image in enumerate(images):
        image_path = f"./invoices-images/{cfg.DOC_PATH.split('/')[-1].split('.')[0]}_{i}.png"
        image.save(image_path, "PNG")
        images_path.append(image_path)

        corrected_image = correct_image_orientation_with_ocr(image_path)
        corrected_image_path = f"./invoices-images/corrected_{cfg.DOC_PATH.split('/')[-1].split('.')[0]}_{i}.png"
        cv2.imwrite(corrected_image_path, corrected_image)

        # Invoke Multi-Modal Model with Vision-enabled capabilities to extract text from image
        prompt_template = ChatPromptTemplate.from_messages(cfg.MESSAGES_2)
        prompt = prompt_template.invoke({"INVOICE_IMAGE": corrected_image_path})
        res = llm.invoke(prompt)
        print(res.content)


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



prompt_template = ChatPromptTemplate.from_messages(cfg.MESSAGES)
prompt = prompt_template.invoke({"INVOICE_DATA": invoice_data})
res = llm.invoke(prompt)
print(res.content)
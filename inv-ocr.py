# 1. Ingest PDF Files
from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain_community.document_loaders import OnlinePDFLoader
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.document_loaders.image import UnstructuredImageLoader
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import os

doc_path = "./invoices/galile.pdf"
model = "llama3.2"

print("starting script...")

if os.path.exists(doc_path):
    print("PDF file exists")

    images = convert_from_path(doc_path, dpi=300, poppler_path=r'Release-24.08.0-0\poppler-24.08.0\Library\bin')

    images_path = []

    for i, image in enumerate(images):
        image_path = f"./invoices-images/{doc_path.split('/')[-1].split('.')[0]}.png"
        image.save(image_path, "PNG")
        images_path.append(image_path)

    print(f"Converted {len(images)} pages to images.")
    
    if not os.path.exists(images_path[0]):
        print(f"Error: Image file '{images_path[0]}' not found!")
    else:
        print(f"Image file exists: {images_path[0]}")

    image = Image.open(os.path.abspath(images_path[0]))
    ocr_text = pytesseract.image_to_string(image)
    print("ocr text created successfully")
    print(ocr_text)
    
    try:
        print("Attempting to load the image...")
        data = loader.load()
        print("Document loaded successfully")
        print(data)

        content = data[0].page_content
        print(content[:100])
    
    except Exception as e:
        print(f"Error loading document: {e}")

else:
    print("Missing PDF file")



# 2. Extract Text from PDF Files and split into small chunks

# 3. Convert chunks into vectors using embedding model

# 4. Save embeddings to a vector db

# 5. Perform similarity search on the vector db

# 6. Retrieve similar docs
# 1. Ingest PDF Files
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import os
import sys

# Adding the project's root directory to sys.path to enable importing modules from sibling folders.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from cfg import config as cfg

print("starting script...")

if os.path.exists(cfg.DOC_PATH):
    print("PDF file exists")

    images = convert_from_path(cfg.DOC_PATH, dpi=300, poppler_path=r'Release-24.08.0-0\poppler-24.08.0\Library\bin')

    images_path = []
    ocr_text = []

    for i, image in enumerate(images):
        image_path = f"./invoices-images/{cfg.DOC_PATH.split('/')[-1].split('.')[0]}_{i}.png"
        image.save(image_path, "PNG")
        images_path.append(image_path)

        image = Image.open(os.path.abspath(images_path[i]))
        ocr_text.append(pytesseract.image_to_string(image, config='--psm 1'))
        print("ocr text created successfully")
        print(ocr_text)

    print(f"Converted {len(images)} pages to images.")
    
    if not os.path.exists(images_path[0]):
        print(f"Error: Image file '{images_path[0]}' not found!")
    else:
        print(f"Image file exists: {images_path[0]}")

    

else:
    print("Missing PDF file")


# Concatenate the content of all chunks into a single string
invoice_data = ocr_text

# 6. Retrieval

from langchain.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama


print("Initializing ChatOllama...")
llm = ChatOllama(model=cfg.MODEL)

prompt_template = ChatPromptTemplate.from_messages(cfg.MESSAGES)
prompt = prompt_template.invoke({"INVOICE_DATA": invoice_data})
res = llm.invoke(prompt)
print(res.content)



# 2. Extract Text from PDF Files and split into small chunks

# 3. Convert chunks into vectors using embedding model

# 4. Save embeddings to a vector db

# 5. Perform similarity search on the vector db

# 6. Retrieve similar docs
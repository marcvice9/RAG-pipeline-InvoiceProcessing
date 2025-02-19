# AI-Powered Invoice Processing System with LLaVa & OCR
🚧 **This project is currently under development

## Overview  
This project is a locally hosted, secure AI-powered system for processing invoices. It uses **LLaVa** (Large Vision-Language Model) alongside **OCR** to extract structured data from scanned or digital PDFs and convert it into **JSON format**. The solution ensures data privacy by avoiding cloud-based processing and running entirely on local infrastructure.  

## Features  
- 📄 **Processes scanned and digital invoices** (PDF, images)  
- 🧠 **Uses LLaVa for vision-based understanding**  
- 🔍 **OCR fallback for text extraction**  
- 🔒 **Runs privately and securely**  
- 🛠 **Outputs structured data in JSON format**  

## System Architecture  
1. **Document Ingestion** – PDFs are dropped into a watch folder.  
2. **Preprocessing** – Converts PDFs to images (if needed).  
3. **OCR & AI Processing** – Extracts text and structure via OCR & LLaVa.  
4. **Data Structuring** – Transforms extracted information into a JSON format.  
5. **Storage & Output** – Saves JSON data for further processing.

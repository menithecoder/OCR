from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from io import BytesIO
from PIL import Image
import pytesseract
import re
import datetime
import os
from fastapi import Request


app = FastAPI()

# Path to your templates directory
templates = Jinja2Templates(directory="templates")

def analyze_payment_receipt(image: BytesIO):
    try:
        # Open the image from the BytesIO object
        image = Image.open(image)
        
        # Extract text using OCR
        text_heb = pytesseract.image_to_string(image, lang='heb')
        text_eng = pytesseract.image_to_string(image, lang='eng')
        print(text_heb)
        text = text_heb
        # Initialize results dictionary
        payment_info = {
            'name': None,
            'account_number': None,
            'amount': None,
            'date': None,
            'raw_text': text
        }
        
        # Extract account number, amount, date, and name from the text
        account_match = re.search(r'(\d+[-]\d+)', text)
        if account_match:
            payment_info['account_number'] = account_match.group(1)
        amount_match = re.search(r'(\d+)\s*₪', text)
        if amount_match:
            payment_info['amount'] = float(amount_match.group(1))
        else:
            amount_match = re.search(r'[\n\r]\s*(\d+)\s*[\n\r]', text)
            if amount_match:
                payment_info['amount'] = float(amount_match.group(1))
        date_match = re.search(r'(\d{2}/\d{2}/\d{4})', text)
        if date_match:
            date_str = date_match.group(1)
            try:
                payment_info['date'] = datetime.datetime.strptime(date_str, '%d/%m/%Y').date()
            except ValueError:
                pass
        name_match = re.search(r'הועבר על ידי\s+(.+?)[\n\r]', text)
        if name_match:
            payment_info['name'] = name_match.group(1).strip()
        
        return payment_info
    except Exception as e:
        return {"error": str(e)}

@app.get("/", response_class=HTMLResponse)
async def get_upload_form(request: Request):
    return templates.TemplateResponse("upload_form.html", {"request": request})

@app.post("/analyze/")
async def analyze(file: UploadFile = File(...)):
    try:
        image = await file.read()
        result = analyze_payment_receipt(BytesIO(image))
        
        if "error" in result:
            return {"error": result["error"]}
        else:
            return result
    
    except Exception as e:
        return {"error": str(e)}


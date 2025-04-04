from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
import shutil
import os
from PIL import Image
import pytesseract
import re
import datetime

app = FastAPI()

# Mount templates directory
templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def analyze_payment_receipt(image_path):
    try:
        image = Image.open(image_path)
        text_heb = pytesseract.image_to_string(image, lang='heb')
        text_eng = pytesseract.image_to_string(image, lang='eng')
        text = text_heb

        payment_info = {
            'name': None,
            'account_number': None,
            'amount': None,
            'date': None,
            'raw_text': text
        }

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
            try:
                payment_info['date'] = datetime.datetime.strptime(date_match.group(1), '%d/%m/%Y').date()
            except ValueError:
                pass

        name_match = re.search(r'הועבר על ידי\s+(.+?)[\n\r]', text)
        if name_match:
            payment_info['name'] = name_match.group(1).strip()

        return payment_info
    except Exception as e:
        return {"error": str(e)}

@app.get("/", response_class=HTMLResponse)
async def upload_form(request: Request):
    return templates.TemplateResponse("upload_form.html", {"request": request})

@app.post("/upload", response_class=HTMLResponse)
async def handle_upload(request: Request, file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    result = analyze_payment_receipt(file_path)

    return templates.TemplateResponse("upload.html", {
        "request": request,
        "result": result
    })
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

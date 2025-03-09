import pytesseract
from PIL import Image
import re
import datetime
import os

def analyze_payment_receipt(image_path):
    """
    Analyze a payment receipt image and extract key information.
    
    Args:
        image_path (str): Path to the receipt image
        
    Returns:
        dict: Extracted payment information
    """
    try:
        # Open the image
        image = Image.open(image_path)
        
        # Extract text using OCR - assuming Hebrew language
        text = pytesseract.image_to_string(image, lang='heb')
        
        # Initialize results dictionary
        payment_info = {
            'name': None,
            'account_number': None,
            'amount': None,
            'date': None,
            'raw_text': text
        }
        
        # Extract account number - looking for pattern matching the one in the image (972-526045120)
        account_match = re.search(r'(\d+[-]\d+)', text)
        if account_match:
            payment_info['account_number'] = account_match.group(1)
        
        # Extract amount - looking for a number followed by ₪ (shekel symbol)
        amount_match = re.search(r'(\d+)\s*₪', text)
        if amount_match:
            payment_info['amount'] = float(amount_match.group(1))
        else:
            # Alternative search for just numbers that might be the amount
            amount_match = re.search(r'[\n\r]\s*(\d+)\s*[\n\r]', text)
            if amount_match:
                payment_info['amount'] = float(amount_match.group(1))
        
        # Extract date - looking for date format DD/MM/YYYY
        date_match = re.search(r'(\d{2}/\d{2}/\d{4})', text)
        if date_match:
            date_str = date_match.group(1)
            try:
                payment_info['date'] = datetime.datetime.strptime(date_str, '%d/%m/%Y').date()
            except ValueError:
                pass
        
        # Extract name - typically after "הועבר על ידי" (transferred by) in Hebrew
        name_match = re.search(r'הועבר על ידי\s+(.+?)[\n\r]', text)
        if name_match:
            payment_info['name'] = name_match.group(1).strip()
        
        return payment_info
    
    except Exception as e:
        return {"error": str(e)}

def main():
    # Set the default image path to 'paybox.jpg' in the current directory
    image_path = 'paybox.jpg'
    
    # Check if the file exists
    if not os.path.exists(image_path):
        print(f"Error: '{image_path}' not found in the current directory.")
        return
    
    result = analyze_payment_receipt(image_path)
    
    print("\n=== Payment Receipt Analysis ===")
    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        print(f"Name: {result['name']}")
        print(f"Account Number: {result['account_number']}")
        print(f"Amount: {result['amount']} ₪")
        if result['date']:
            print(f"Date: {result['date'].strftime('%d/%m/%Y')}")
        else:
            print("Date: Not found")
    
    print("\nNote: For accurate results, ensure pytesseract is properly installed with Hebrew language support.")

if __name__ == "__main__":
    main()

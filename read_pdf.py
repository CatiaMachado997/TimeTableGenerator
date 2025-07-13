import PyPDF2
import os

def read_pdf():
    pdf_path = "MEGI_PRJT2_2024-2025_DEM_TT_v1.0.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"PDF file {pdf_path} not found!")
        return
    
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            print(f"PDF has {len(pdf_reader.pages)} pages")
            print("=" * 50)
            
            for page_num, page in enumerate(pdf_reader.pages, 1):
                print(f"\n--- PAGE {page_num} ---")
                text = page.extract_text()
                print(text)
                print("-" * 30)
                
    except Exception as e:
        print(f"Error reading PDF: {e}")

if __name__ == "__main__":
    read_pdf() 
import os

# Assuming this is a method from where you generate the pdf

def generate_pdf(pdf_content):
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
    os.makedirs(output_dir, exist_ok=True)
    pdf_path = os.path.join(output_dir, 'document.pdf')
    # Insert logic to create the PDF file at pdf_path using pdf_content
    
    return pdf_path

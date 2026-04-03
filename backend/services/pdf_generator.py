# updated content for pdf_generator.py with robust path handling

import os

# robust path handling example
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_PATH = os.path.join(CURRENT_DIR, 'pdfs')

# your code goes here

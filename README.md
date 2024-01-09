# FdaSearch

Due to the requirements for Poppler/Tesseract you may want to consider the environment you run this in. I developed this in Ubuntu and that's how it's meant to be run but the code can easily be changed to work with Windows .exe's

This project aims to find 510k PNs by keyword and product code. It does so through OCR of the Summary/Statement PDFs. If you only need product codes, you should be able to easily change the driver code to generate this list. 

The program mandates a `.csv` file in the data directory containing their medical devices list. Since FDA doesn't have an API, this is the closest we have. Fortunately it's local and extremely complete.

The program first filters by product code and then looks for keywords within the summary pdf. If there is no summary pdf, the product code is logged in a separate output text file. The keywords and vars can be found at the top of ``main.py``

## Prerequisites:
- Poppler (For PDF2Image)
  - Linux: `sudo apt-get install poppler-utils` and `sudo apt-get install libpoppler-dev
`
  - Windows: You're going to have to change the pdfscanner code. It will need a path to the exe (which you'll have to install) or be in PATH.
- [Tesseract](https://tesseract-ocr.github.io/tessdoc/Installation.html) (For OCR)
  - Linux: `sudo apt install tesseract-ocr` and `sudo apt install libtesseract-dev`
  - Windows: Same as above. Install, add to PATH
- All the libraries in the `main.py` list (use pip)
  - BeautifulSoup
  - Pandas
  - PyTesseract
  - PDF2Image
  - PIL (Pillow)
  - CV2 (OpenCV)
  - ... any others your system is missing
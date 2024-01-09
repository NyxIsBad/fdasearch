# fdasearch

The program mandates a ``.csv`` file in the same directory containing their medical devices list. Since FDA doesn't have an API, this is the closest we have. Fortunately it's local and extremely complete.

The program first filters by product code and then looks for keywords within the summary pdf. If there is no summary pdf, the product code is logged in a separate output text file. The keywords and vars can be found at the top of ``main.py``

## Prerequisites:
```py
# data related libs
import pandas as pd
import csv 
import pickle
# requirements for reading the pdf
import urllib.request
from io import BytesIO 
from PyPDF2 import PdfReader
# ocr
import platform
from tempfile import TemporaryDirectory
from pathlib import Path
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
# web scraping w/ bs4
import httplib2
from bs4 import BeautifulSoup, SoupStrainer
```
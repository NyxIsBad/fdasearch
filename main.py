# data related libs
import pandas as pd
import csv 
import pickle
# ocr
from tempfile import TemporaryDirectory
import pytesseract
import pdf2image
from PIL import Image
import requests
# web scraping w/ bs4
import httplib2
from bs4 import BeautifulSoup, SoupStrainer
# -------------------------
# GLOBALS
# -------------------------
# file prefix
DATADIR = "data/"
# data names (eg. the names of the csvs)
DATA = ['96cur','7680','8185','8690','9195']
# pdf prefix
PDFDIR = "pdf/"
# tmp prefix
TMPDIR = "tmp/"
# csv delimiter
DELIM = '|'
# valid product codes
VALID_CODE = ['GEI','PAY','ONQ','OHV','GEX','OHS','NUV','ONG','ONE','ONF']
# keywords - all lowercase
COND_KEYWORD = ['wrinkle']
KEYWORD = ['fitzpatrick','scale','type']
# DB Link (510k)
DBPREFIX = 'https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID='
# -------------------------
# FUNCS
# -------------------------
# -------------------------
# DATA/FILE SAVING/LOADING
# -------------------------
# Load codes from csv    
def load_csv(input):
    data = pd.read_csv(input, sep=DELIM, header=0, keep_default_na=False)
    return data # returns df
# load a list from a text file
def load_txt(input):
    user_list = list()
    with open(input,'r') as f:
        for line in f:
            user_list.append(line.rstrip())
    return user_list
# Load a list from file
def load_users(file):
    with open(str(file),"rb") as f:
        user_list = pickle.load(f)
    return user_list
# output a list as a text
def write_txt(out, lst):
    with open(out, "w") as f:
        for item in lst:
            f.write(f"{item}\n")
# read csv files
def read_single(file):
    return load_csv(file)
# read multiple csv
def read_multiple(arr):
    return pd.concat(map(lambda date: load_csv(f'{DATADIR}{date}.csv'), arr))
# -------------------------
# FILTERING
# -------------------------
# return the rows in a df that match a value in the arr
def filter_by_col_arr(pd_arr, column, value_arr):
    return pd_arr.loc[pd_arr[column].isin(value_arr)]
# return the rows in a df that match the value
def filter_by_col(pd_arr, column, value):
    return pd_arr.loc[pd_arr[column] == value]
# returns the column as a list
def get_col_as_list(pd_arr, column):
    return list(pd_arr[column])
# -------------------------
# READ/OCR PDF
# -------------------------
# Reading the text. There are multiple cases to this.
# Case 1: OCR correctly reads text. In this case, we concatenate all text and 
#       save it as a .txt file in PDFDIR/ocr/{code}.txt. Also return "success" or 1
# Case 2: We can't read it. Then, we return "fail" or 0. This will get concatenated to the 
#       "none_knums" variable and outputted as a text file.
def pdfscanner(type, prefix, code):
    # vars
    img_lst = []
    # open the file online and then create a pdfreader instance
    url = getlink(type, prefix, code)
    if url == "": 
        return 0
    # get the actual content.
    pdf = requests.get(url, stream=True).content
    # We use OCR to recognize the text. 
    # We can use PdfReader to find the DPI.
    # reader = PdfReader(bytes_stream)
    print(f"{type} of {code}: URL {url} | DB URL: {prefix}{code}")
    
    # Implementation of case 1:
    with TemporaryDirectory() as tempdir:
        # Step 1, turn the pdf into images.
        # read the pdf as images at 500dpi
        pdf_pages = pdf2image.convert_from_bytes(pdf, 500)
        for num, pg in enumerate(pdf_pages, start=1):
            fname = f'{tempdir}/{code}_{pg}_{num:03}.jpg'
            pg.save(fname,"JPEG")
            img_lst.append(fname)
        # Step 2, read the images
        # open the txt file output
        for img in img_lst:
            with open(f'{PDFDIR}/ocr/{code}.txt','w') as f: 
                # OCR the page
                page_txt = str(pytesseract.image_to_string(Image.open(img))).replace("-\n","")
                f.write(page_txt)
    return 1

# gets the link for a summary or statement from the FDA db by scraping
def getlink(type, prefix, code):
    http = httplib2.Http()
    status, resp = http.request(f'{prefix}{code}')
    for link in BeautifulSoup(resp, features='html.parser', parse_only=SoupStrainer('a')):
        if link.has_attr('href') and link.string==type:
            return link['href']
    return ""
# -------------------------
# DRIVER CODE
# -------------------------
# test code
pdfscanner('Summary',DBPREFIX,'K090406')
pdfscanner('Statement',DBPREFIX,'K090465')
# read the csvs in as df
csv = read_multiple(DATA)
# find results by product code
results = filter_by_col_arr(csv, 'PRODUCTCODE', VALID_CODE)
# find results with summary
results_summary = filter_by_col(results, 'STATEORSUMM', 'Summary')
results_statement = filter_by_col(results, 'STATEORSUMM', 'Statement')
results_none = filter_by_col(results, 'STATEORSUMM', '')
# get the knumbers
summary_knums = get_col_as_list(results_summary, 'KNUMBER')
statement_knums = get_col_as_list(results_statement, 'KNUMBER')
none_knums = get_col_as_list(results_none, 'KNUMBER')
# TODO: read each knum in summary_knums and statement_knums and save their contents to text files. 
# print some numbers
print(f'Total files: {len(results)}\n'
      f'Matching files with a knumber and summary: {len(summary_knums)}\n'
      f'Matching files by summary: {len(results_summary)}+{len(results_statement)}+{len(results_none)}')
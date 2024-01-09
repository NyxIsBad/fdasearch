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
import cv2
# web scraping w/ bs4
import httplib2
from bs4 import BeautifulSoup, SoupStrainer
# -------------------------
# GLOBALS
# -------------------------
# 1: read from csvs, generate lists, save them
# 2: read from lists, scan pdfs, create txts
# 3: scan through txts for keywords
start_idx = 1199
mode = 2
# file prefix
DATADIR = "data/"
# data names (eg. the names of the csvs)
DATA = ['96cur','7680','8185','8690','9195']
# pdf prefix
PDFDIR = "pdf/"
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
    lst = list()
    with open(input,'r') as f:
        for line in f:
            lst.append(line.rstrip())
    return lst
# Load a list from file
def load_obj(file):
    with open(file,"rb") as f:
        obj = pickle.load(f)
    return obj
# output a list as a text
def write_txt(out, lst):
    with open(out, "w") as f:
        for item in lst:
            f.write(f"{item}\n")
# write an object to file 
def write_obj(out, obj):
    with open(out, "wb") as f:
        pickle.dump(obj,f)
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
        # read the pdf as images
        pdf_pages = pdf2image.convert_from_bytes(pdf)
        for num, pg in enumerate(pdf_pages, start=1):
            fname = f'{tempdir}/{code}_{num:03}.png'
            pg.save(fname,"PNG")
            img_lst.append(fname)
        # Step 2, read the images
        # open the txt file output
        with open(f'{PDFDIR}/ocr/{code}.txt','w') as f: 
            for img in img_lst:
                # OCR the page
                # image preprocessing can be put under here
                image = cv2.imread(f'{img}')

                page_txt = str(pytesseract.image_to_string(image, lang='eng', config='--psm 6')).replace("-\n","")
                f.write(f'{page_txt}\n')
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

if mode==1:
    # read the csvs in as df
    csv = read_multiple(DATA)
    # find results by product code
    results = filter_by_col_arr(csv, 'PRODUCTCODE', VALID_CODE)
    
    # find results with summary
    results_summary = filter_by_col(results, 'STATEORSUMM', 'Summary')
    results_statement = filter_by_col(results, 'STATEORSUMM', 'Statement')
    results_none = filter_by_col(results, 'STATEORSUMM', '')
    # get the knumbers
    results_knums = get_col_as_list(results_summary, 'KNUMBER')
    summary_knums = get_col_as_list(results_summary, 'KNUMBER')
    statement_knums = get_col_as_list(results_statement, 'KNUMBER')
    none_knums = get_col_as_list(results_none, 'KNUMBER')
    # write to files
    write_obj(f'{DATADIR}matching_codes_pickle',results)
    write_obj(f'{DATADIR}matching_codes_with_summary_pickle', results_summary)
    write_obj(f'{DATADIR}matching_codes_with_statement_pickle', results_statement)
    write_obj(f'{DATADIR}matching_codes_none_pickle', results_none)

    write_txt(f'{DATADIR}matching_codes.txt', results_knums)
    write_txt(f'{DATADIR}matching_codes_with_summary.txt', summary_knums)
    write_txt(f'{DATADIR}matching_codes_with_statement.txt', statement_knums)
    write_txt(f'{DATADIR}matching_codes_none.txt', none_knums)
    # print some numbers
    print(f'Total files: {len(results)}\n'
        f'Matching files with a knumber and summary: {len(summary_knums)}\n'
        f'Matching files by summary: {len(results_summary)}+{len(results_statement)}+{len(results_none)}')
elif mode==2:
    summary_knums = load_txt(f'{DATADIR}matching_codes_with_summary.txt')
    print(f'Successfully loaded {len(summary_knums)} nums!')
    # vars
    failed = []
    success = []
    # create the txt files for each knum with a summary
    for num, knum in enumerate(summary_knums[start_idx:]):
        if pdfscanner('Summary', DBPREFIX, knum) == 1:
            print(f'Successfully converted #{num+start_idx}: {knum} to txt')
            success.append(knum)
        else:
            print(f'Failed to convert #{num+start_idx}: {knum} to txt')
            failed.append(knum)
    write_txt(f'{DATADIR}converted_to_txt.txt', success)
    write_txt(f'{DATADIR}failed_to_txt.txt', failed)
elif mode==3: 
    print("Implement mode 3")
else:
    print("How did you get here? Wrong mode #.")
        
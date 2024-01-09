import pandas as pd
import csv 
import urllib
from io import BytesIO 
from PyPDF2 import PdfReader
# -------------------------
# GLOBALS
# -------------------------
# dates (eg. the names of the csvs)
FILES = ['96cur','7680','8185','8690','9195']
# csv delimiter
DELIM = '|'
# valid product codes
VALIDS = ['GEI','PAY','ONQ','OHV','GEX','OHS','NUV','ONG','ONE','ONF']
# keywords - all lowercase
CONDITIONALKEYWORD = ['wrinkle']
KEYWORDS = ['fitzpatrick','scale','type']
# -------------------------
# HELPER FUNC
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
    return pd.concat(map(lambda date: load_csv(f'{date}.csv'), arr))
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
# DRIVER CODE
# -------------------------
# read the csvs in as df
csv = read_multiple(FILES)
# find results by product code
results = filter_by_col_arr(csv, 'PRODUCTCODE', VALIDS)
# find results with summary
results_with_summary = filter_by_col(results, 'STATEORSUMM', 'Summary')
# get the knumbers
knumbers = get_col_as_list(results_with_summary, 'KNUMBER')
print(len(knumbers))
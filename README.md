# fdasearch

The program mandates a ``.csv`` file in the same directory containing their medical devices list. Since FDA doesn't have an API, this is the closest we have. Fortunately it's local and extremely complete.

The program first filters by product code and then looks for keywords within the summary pdf. If there is no summary pdf, the product code is logged in a separate output text file. The keywords and vars can be found at the top of ``main.py``
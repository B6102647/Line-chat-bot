import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36 Edg/92.0.902.55',
    'Accept'          : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 
    'Accept-Language' : 'en-US,en;q=0.5',
    'DNT'             : '1', # Do Not Track Request Header 
    'Connection'      : 'close'}


def get_time():
     # Time zone in Thailand UTC+7
    tz = timezone(timedelta(hours = 7)) 
    # Create a date object with given timezone
    date = str(datetime.now(tz=tz))
    return date

def scaping(stockSymbol):
    url = 'https://finance.yahoo.com/quote/'+ stockSymbol 
    resp = requests.get(url, headers=headers, timeout=5).text 

    soup = BeautifulSoup(resp, 'html.parser')
    table = {}
    stock_price = soup.find_all('fin-streamer',{"class":"Fw(b) Fz(36px) Mb(-4px) D(ib)"})[0].text
    price = float(stock_price)
    table["Price"] = price

    table["Datetime"] = get_time()

    quote_notice = soup.find_all('div',{"id":"quote-market-notice"})[0].text
    isOpen = quote_notice.split(" ")[0] == "As"
    if isOpen :
        status = "open"
    else:
        status = "close"
    table["Status"] = status 

    # print("Price = ",table['Price'])
    # print("Time = ",table['Time'])
    # print("Status = ",table['Status'])
   
    return table

# scaping('AAPL')
import os
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import regex as re
import requests


pd.set_option('display.max_rows', None)
pd.set_option('mode.chained_assignment',None)
headers = {
    'authority': 'www.zillow.com',
    'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36',
    'accept': '*/*',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://www.zillow.com/los-angeles-ca/2_p/?searchQueryState=%7B%22pagination%22%3A%7B%22currentPage%22%3A2%7D%2C%22usersSearchTerm%22%3A%22Los%20Angeles%22%2C%22mapBounds%22%3A%7B%22west%22%3A-118.88620504589845%2C%22east%22%3A-117.93726095410157%2C%22south%22%3A33.54554919445917%2C%22north%22%3A34.49481997322805%7D%2C%22regionSelection%22%3A%5B%7B%22regionId%22%3A12447%2C%22regionType%22%3A6%7D%5D%2C%22isMapVisible%22%3Atrue%2C%22filterState%22%3A%7B%22sort%22%3A%7B%22value%22%3A%22globalrelevanceex%22%7D%2C%22ah%22%3A%7B%22value%22%3Atrue%7D%7D%2C%22isListVisible%22%3Atrue%7D',
    'accept-language': 'en-US,en;q=0.9',
}

with requests.session() as s:
    city = 'los-angeles/'
    page = 1
    end_page = 10
    url = ''
    url_list = []
    
    while page <= end_page:
        url = 'https://www.zillow.com/homes/for_sale/' +city+ f'{page}_p/'
        url_list.append(url)
        page += 1
    
    request = ''
    request_list = []
    
    for url in url_list:
        request = s.get(url, headers=headers)
        request_list.append(request)
    
soup = ''
soup_list = []

for request in request_list:
    soup = BeautifulSoup(request.content, 'html.parser')
    soup_list.append(soup)
soup_list[0]
df_list = []
for soup in soup_list:
    df = pd.DataFrame()
    for i in soup:
        address = soup.find_all (class_= 'list-card-addr')
        price = list(soup.find_all (class_='list-card-price'))
        beds = list(soup.find_all("ul", class_="list-card-details"))
        details = soup.find_all ('div', {'class': 'list-card-details'})
        home_type = soup.find_all ('div', {'class': 'list-card-footer'})
        last_updated = soup.find_all ('div', {'class': 'list-card-top'})
        brokerage = list(soup.find_all(class_= 'list-card-brokerage list-card-img-overlay',text=True))
        link = soup.find_all (class_= 'list-card-link')
        
        df['prices'] = price
        df['address'] = address
        df['beds'] = beds
        
    urls = []
    
    for link in soup.find_all("article"):
        href = link.find('a',class_="list-card-link")
        addresses = href.find('address')
        addresses.extract()
        urls.append(href)
    
    df['links'] = urls
    df['links'] = df['links'].astype('str')
    df['links'] = df['links'].replace('<a class="list-card-link list-card-link-top-margin" href="', ' ', regex=True)
    df['links'] = df['links'].replace('" tabindex="0"></a>', ' ', regex=True)
    df_list.append(df)
df_list[0]
df = pd.concat(df_list).reset_index().drop(columns='index')
df
df['address'] = df['address'].astype('str')
df['beds'] = df['beds'].astype('str')
#remove html tags
#df['prices'] = df['prices'].replace('\[', '', regex=True)
df.loc[:,'address'] = df.loc[:,'address'].replace('<address class="list-card-addr">', '', regex=True)
#df['prices'] = df['prices'].replace('\]', '', regex=True)
df.loc[:,'address'] = df.loc[:,'address'].replace('</address>', '', regex=True)
#df['prices'] = df['prices'].str.replace(r'\D', '')

#filter unwanted property types
df = df[~df['beds'].str.contains("Land for sale")]

#remove html tags from beds column
df.loc[:,'beds'] = df.loc[:,'beds'].replace('<ul class="list-card-details"><li class="">', ' ', regex=True)
df.loc[:,'beds'] = df.loc[:,'beds'].replace('<abbr class="list-card-label"> <!-- -->bds</abbr></li><li class="">', ' ', regex=True)
df.loc[:,'beds'] = df.loc[:,'beds'].replace('<abbr class="list-card-label"> <!-- -->ba</abbr></li><li class="">', ' ', regex=True)
df.loc[:,'beds'] = df.loc[:,'beds'].replace('<abbr class="list-card-label"> <!-- -->bd</abbr></li><li class="">', ' ', regex=True)
df.loc[:,'beds'] = df.loc[:,'beds'].replace('-<abbr class="list-card-label"> <!-- -->Foreclosure</abbr>', '- Foreclosure', regex=True)
df.loc[:,'beds'] = df.loc[:,'beds'].replace('<abbr class="list-card-label"> <!-- -->sqft</abbr></li><li class="list-card-statusText">', ' ', regex=True)
df.loc[:,'beds'] = df.loc[:,'beds'].replace('<abbr class="list-card-label"> <!-- -->acres lot</abbr></li><li class="list-card-statusText">', ' ', regex=True)
df.loc[:,'beds'] = df.loc[:,'beds'].replace('</li></ul>', '', regex=True)
df.loc[:,'beds'] = df.loc[:,'beds'].replace('--', '0', regex=True)
df.loc[:,'beds'] = df.loc[:,'beds'].replace('Multi-family', 'Multifamily', regex=True)
df.loc[:,'beds'] = df.loc[:,'beds'].replace(' for sale', '', regex=True)
df.loc[:,'beds'] = df.loc[:,'beds'].replace('-<abbr class="list-card-label"> <!0 0>Auction</abbr>', '- Auction', regex=True)
df.loc[:,'beds'] = df.loc[:,'beds'].replace('-<abbr class="list-card-label"> <!0 0>Pending</abbr>', '- Pending', regex=True)

#split beds column into beds, bath and sq_feet
#df[['beds','baths','sq_feet']] = df.beds.str.split(expand=True)
df.iloc[19]['beds']
df[['beds','type']] = df.beds.apply(
    lambda x: pd.Series(str(x).split('-')))
df.head()
df[['beds', 'baths', 'sq_feet']] = df.beds.str.split(expand=True)
df
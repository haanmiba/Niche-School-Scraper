#
# Author: Hans Bas
#
# Created: 02-20-2018
#

import pandas as pd
from bs4 import BeautifulSoup
import requests
import sys

## Check to see that there are three arguments passed in
if len(sys.argv) != 3:
    'Sorry! You need three arguments for this script to work: (1) python niche_high_school_scraper.py (2) <niche_url> (3) <file_name>'
    exit(0)

## Read in sys argument (should be a niche.com search result URL and the file name)
url = sys.argv[1]
file_name = sys.argv[2]

if 'niche.com' not in url:
    'Sorry! This script only works with the website niche.com!'
    exit(0)

## Make a request to the URL and pass in the contents to BeautifulSoup
r = requests.get(url)
s = BeautifulSoup(r.content, 'html.parser')

## Get all of the school titles and links to each individual school page
titles = s.findAll('h2', {'class': 'search-result__title'})
links = s.findAll('a', {'class': 'search-result__link'})

## Create an empty dictionary that will store all of the data
dict = {
    "School":[],
    "Address":[]
}

## Gather the information for each individual school.
for t, l in zip(titles, links):

    # Visit each of the links from the search result page for each school
    r_inner = requests.get(l['href'])
    s_inner = BeautifulSoup(r_inner.content, 'html.parser')

    # Get the address of the school
    address = s_inner.findAll('div', {'class': 'profile__address'})[0]
    address_inner_div = address.select('div')[1].select('div')

    # Split the address up into street, town/city, state, and zip code
    street = address_inner_div[0].next
    town_city = address_inner_div[1].next
    state = "".join(map(str, address_inner_div[1].contents))[-10:-8]
    zip = "".join(map(str, address_inner_div[1].contents))[-5:]

    # Add data to the dictionary
    dict['School'].append(t.next)
    dict['Address'].append('{}, {}, {} {}'.format(street, town_city, state, zip))

    print("{}|{}, {}, {} {}".format(t.next, street, town_city, state, zip))

## Write the data to an .xlsx spreadsheet
writer = pd.ExcelWriter(file_name + '.xlsx')
pd_dict = pd.DataFrame(dict)
pd_dict.to_excel(writer, 'Sheet1', index=False)
writer.save()
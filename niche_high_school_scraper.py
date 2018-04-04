#
# Author: Hans Bas
#
# Created: 02-20-2018
#

import pandas as pd
from bs4 import BeautifulSoup
import requests
import sys

## Read in sys argument (should be a niche.com search result URL and the file name) if provided 3 arguments. Else, read from input
url = sys.argv[1] if len(sys.argv) >= 3 else input('Please enter the niche.com search results url: ')

## Check to see if the URL is a niche.com URL
if 'niche.com' not in url:
    print('Sorry! This script only works with the website niche.com!')
    exit(0)

## Read in sys argument of output file name if provided 3 arguments. Else, read from input
file_name = sys.argv[2] if len(sys.argv) >= 3 else input('Please enter the name of the file you wish to output to: ')

## Make a request to the URL and pass in the contents to BeautifulSoup
r = requests.get(url)
s = BeautifulSoup(r.content, 'html.parser')

## Store all of the search results on the page
search_results = s.findAll('div', {'class': 'search-result'})

## Types of data to be scraped from niche.com search results page and each individual school
primary_data = ['School', 'Address', 'Overall Niche Grade']
niche_grade_rubric = ['Academics', 'Diversity', 'Teachers', 'College Prep', 'Clubs & Activities',
                      'Health & Safety', 'Administration', 'Sports', 'Food', 'Resources & Facilities']

## The dictionary that will store all of the data
data = {k : [] for k in primary_data + niche_grade_rubric}

## Gather the information for each individual school that appeared on the search results.
for s in search_results:

    # Get the link to each school's individual page, and each school's individual name
    link = s.findAll('a', {'class': 'search-result__link'})[0]['href']
    title = s.findAll('h2', {'class': 'search-result__title'})[0].next

    # Add the school's name to the dictionary
    data['School'].append(title)

    # Make a request to the individual school's Niche webpage
    r_inner = requests.get(link)
    s_inner = BeautifulSoup(r_inner.content, 'html.parser')

    # Scrape the school's mailing address
    address = s_inner.findAll('div', {'class': 'profile__address'})[0]
    address_inner_div = address.select('div')[1].select('div')
    address_inner_split = ''.join(map(str, address_inner_div[1].contents)).split(' ')
    street = address_inner_div[0].next
    town_city = address_inner_div[1].next
    state = ''.join(map(str, address_inner_div[1].contents))[-9:-7]
    zip = ''.join(map(str, address_inner_div[1].contents))[-5:]
    mailing_address = '{}, {}, {} {}'.format(street, town_city, state, zip)

    # Add the school's mailing address to the dictionary
    data['Address'].append(mailing_address)
    print('{}|{}'.format(title, mailing_address))

    # Get the school's overall Niche grade and add it to the dictionary
    overall_niche_grade = s_inner.findAll('div', {'class': 'overall-grade__niche-grade'})[0].findAll('div', {'class': 'niche__grade'})[0].next
    data['Overall Niche Grade'].append(overall_niche_grade)
    print('Overall Niche Grade: {}'.format(overall_niche_grade))

    # Gather all of the tags that contain the school's grades
    niche_grades = s_inner.findAll('div', {'class': 'report-card'})[0].findAll('ol', {'class': 'ordered__list__bucket'})[0].findAll('div', {'class': 'niche__grade'})

    # Go through each school tag and gather its individual grades according to different grade categories. Add to dictionary
    for i in range(len(niche_grade_rubric)):
        data[niche_grade_rubric[i]].append(niche_grades[i].next)
        print('{}: {}'.format(niche_grade_rubric[i], niche_grades[i].next))

## Write the data to an .xlsx spreadsheet
writer = pd.ExcelWriter(file_name + '.xlsx')
pd_data = pd.DataFrame(data)
pd_data = pd_data[primary_data + niche_grade_rubric]
pd_data.to_excel(writer, 'Sheet1', index=False)
writer.save()
import requests
from bs4 import BeautifulSoup

def binder():
    '''returns link to binder login'''
    return 'https://skyscanner.agiloft.com/gui2/samlssologin.jsp?project=Skyscanner'

def maxims():
    from random import randint
    '''Reads the maxims and passes the variable to function
    according to input'''
    contentslist = []
    with open("maxims.txt", "r") as maximlist:
        maximlines = maximlist.readlines()
        maximlist.close()
        for i in maximlines:
            contentslist.append(i)

    maximselection = randint(0, len(contentslist))
    return "{}".format(contentslist[maximselection])

def company_details(company_name):
    '''Search for address, company number'''
    if len(company_name) > 0:
        query = '+'.join(company_name[1::])
        query = query.replace('+limited', '').replace('+plc', '')
        record = []
        addresses = []
        companystrings = ''
        url = "https://beta.companieshouse.gov.uk/search/companies?q="+query
        data = requests.get(url)
        data = data.text
        soup = BeautifulSoup(data, "html.parser")
        for link in soup.find_all('a'):
            comp_option = str(link)
            if 'SearchSuggestions' in comp_option:
                comp_url = str(link.get('href'))
                comp_ref = comp_url.replace('/company/', '')
                namepart = str(link.contents).replace('<strong>', '').replace('</strong>', '').replace('[', '').replace(']', '').replace('\\n', '').replace(',', '').replace("'", '')
                namepart = ' '.join(namepart.split())
                nameoption = namepart.strip().lstrip()
                companystrings = nameoption
                record.append((companystrings, comp_ref))

        try:
            final_list = []
            for link in soup.find_all('p', class_=""):
                if "<strong" not in str(link) and "matches" not in str(link) and "<img" not in str(link):
                    addresses.append(link.contents[0])
            information = list(zip(record, addresses))
            for i in information[0:10]:
                final_list.append("*{}*, {}, {}.".format(i[0][0], i[0][1], i[1]))
            return '\n'.join(final_list)
        except:
            return "No companies found!"
    else:
        return

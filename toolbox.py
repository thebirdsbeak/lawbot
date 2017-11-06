import requests
from bs4 import BeautifulSoup
from master_list import disclaimers as DISCLAIMERS
from master_list import signatories as SIGNATORIES
from spellcheck import spellcheck

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

def disclaimer(disclaimer_type):
    if len(disclaimer_type) > 1:
        if disclaimer_type[1] == "options":
            options = [key for key in DISCLAIMERS]
            return ('\n'.join(options)).title()
        else:
            try:
                disclaimer_query = spellcheck(disclaimer_type[1], DISCLAIMERS, THRESHOLD)
                print(disclaimer_query)
            except:
                return "I don't understand - try 'disclaimer options' for options."
            if disclaimer_query:
                return(DISCLAIMERS[disclaimer_query])
            else:
                print("Nothing found!")
    else:
        return

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

def who_signs(contract_type, THRESHOLD):
    '''Function that grabs and returns the signatories'''
    if len(contract_type) > 1:
        if contract_type[1] == "options":
            options = [key for key in SIGNATORIES]
            return ('\n'.join(options)).title()
        else:
            contract_type = contract_type[1].lower()
            try:
                contract = spellcheck(contract_type, SIGNATORIES, THRESHOLD - 10)
                if contract:
                    signer_list_emea = [signer for signer in SIGNATORIES[contract][0]]
                    signer_list_apac = [signer for signer in SIGNATORIES[contract][1]]
                    message_string_emea = '*(¯`·._.·(¯`·._.· EMEA {} ·._.·´¯)·._.·´¯)*\n'.format(contract.upper())
                    message_string_apac = '*(¯`·._.·(¯`·._.· APAC {} ·._.·´¯)·._.·´¯)*\n'.format(contract.upper())
                    for emea_signer in signer_list_emea:
                        signer = emea_signer.replace(' ', '')
                        location =  'https://flightdeck.skyscannertools.net/index.html?id='+signer
                        message_string_emea += '*{}* - {}\n'.format(emea_signer, location)
                    for apac_signer in signer_list_apac:
                        signer = apac_signer.replace(' ', '')
                        if signer != "No_signatories":
                            location =  'https://flightdeck.skyscannertools.net/index.html?id='+signer
                            message_string_apac += '*{}* - {}\n'.format(apac_signer, location)
                        else:
                            message_string_apac += '*No signatories for this entity.*'
                    return message_string_emea+'\n'+message_string_apac

    # Remove returning error before prod
            except Exception as error:
                return str(error)
    else:
        return ERROR_RESPONSE

# -*- coding: utf-8 -*-



#!pip install requests-html


from pprint import pprint

from requests_html import HTML, HTMLSession

#need to import a module that can talk with an HTML session ( website)

import csv


session = HTMLSession()

#Disclaimer I'm not 100% sure everything done in this code is legal, so please use a VPN
#%%


def drug_list_function(r):

    '''
    
    
    input: Example use this function from Requests html and fill it with a URL before this code  
    r=session.get('https://www.drugbank.ca/unearth/q?utf8=%E2%9C%93&query=hydrophobic&searcher=drugs')
    In this case I looked up hydrohpobic drugs on main page
    output: Makes a list of all the urls associated to all drug sites on the first webpage 
    where you search up a drug characteristic
    '''
    list_drug_sites=[]
    
    for link in r.html.links:
      if 'drugs/DB' in link: #this is where you need to select that its in the Drug Database DB from the url
      
    
        WEBSITE_PREFIX = 'https://www.drugbank.ca'
    
        # whenever you need to 
        full_addresss = WEBSITE_PREFIX + link #concatinates the two to make a proper search
        list_drug_sites.append(full_addresss) 
        

    return list_drug_sites


    








#%%


def get_max_pages(r):
  '''
    

    Parameters
    ----------
    r : Give in a search query with a session.get , 
        example r = session.get('https://www.drugbank.ca/unearth/q?c=_score&d=down&query=vitamin&searcher=drugs')
        here I am looking up all the vitamins in the drug databank
        DESCRIPTION.

    Returns
    -------
    TYPE: the an ineger with the number of pages of urls for that search  query
        DESCRIPTION. so a vitamin search query yields 13 pages each with 20 links


    '''
 
  all_page_numbers = r.html.find('.page-link') # first, find all the links to all the page numbers
  last_page = all_page_numbers[-1] # -1 selects the link to the last page
  
  # at this point, last_page.text is something like: <a class="page-link" href="/unearth/q?c=_score&amp;d=down&amp;page=13&amp;query=vitamin&amp;searcher=drugs">??</a>
  segments = last_page.html.split('&')  # segments is a list split  gives  [..., page=13, query=vitamin, ...] etc.
  
  
  for segment in segments: # now, we want to extract the number from "page=13" segment
    if 'page-link' in segment: #if page-link is hit skip over it
        continue
    if 'page' in segment:
      number_string = segment.split('=')[-1] # this splits "page=13" to a list [page,13] where last element is our page number which we return
      # print(number_string)
      return int(number_string) # this is necessary because the last page number is a string '13', not int so we convert to int.
  
    
#%%


def get_all_pages(r):
    '''
    

    Parameters
    ----------
    r : TYPE: Give in a search query with a session.get , 
        example r = session.get('https://www.drugbank.ca/unearth/q?c=_score&d=down&query=vitamin&searcher=drugs')
        here I am looking up all the vitamins in the drug databank
        DESCRIPTION.

    Yields
    ------
    all_pages : TYPE list
        DESCRIPTION. Gives a list of all the urls 

    '''
    
    max_page_number = get_max_pages(r)  # using previously defined function, get max page number

    
    all_pages = []  # we want to populate list of all pages, properly numbered
    
    
    for page_num in range(1,max_page_number+1): # we use range(1,max_page_number+1) so the counter starts at 1 instead of 0, and ends at max_page_number+1 instead of just max_page_number because range ends at one less than the specified ending.
      # define general form taken by paginated url string. 
     
      url_placeholder = "https://www.drugbank.ca/unearth/q?c=_score&d=down&page={}&query=vitamin&searcher=drugs"
    
      # note the url_placeholder.format(). Format looks for curly braces in string and replaces it with the specified variable. 
     
      
      all_pages.append(url_placeholder.format(page_num)) # after formatting, just add it to our page list.

    return all_pages 


#%%



def get_all_drugs(list_of_urls):
    '''
    Input: A list of page URLS
    Output: This will gives all the links to the drugs found on a given search query, so a lot of urls
    Therefore this prints out a link to every single drug on every single page related to the inital search
    
    '''
    output=[]

    for page in list_of_urls:
        this_page = session.get(page)
        output.extend(drug_list_function(this_page)) #just fits in all of the drug urls, using the extend
        
    return output




    
#%%
    

def safe_drug(r):
    '''
         
    input: Example use this function from Requests html and fill it with a URL before this code  
    r=session.get('https://www.drugbank.ca/drugs/DB14684s')
            
            
    Output: This will tell if the drug is 'safe' or not, if the function 
    finds a  'withdrawn'  from human dosing in the drugs page url, then it is not safe
    
    Safe drug: https://www.drugbank.ca/drugs/DB09185
    Not safe Drug: https://www.drugbank.ca/drugs/DB00365
   
    '''
    drug_humans = r.html.find('.col-md-10' +'.col-sm-8') 
    if drug_humans[3].text.find("Withdrawn") >=0 or drug_humans[3].text.find("withdrawn") >=0 :  
        return False
    else:
        return True
    

#%%


def drug_name(r):
    
    '''
    input: Takes in a session.get('URL')
    output: Outputs the name of the drug
    '''
    


    content_head= r.html.find('.align-self-center',first=True)  #using html location to get the drugs name
    return content_head.text





#%%



def drug_description(r):
    
    '''
    input: Takes in a session.get('URL')
    output: Outputs the description of the drug
    
    '''
    
    description = r.html.find('.col-md-10' +'.col-sm-8') #using the html location of the drug description 

    return description[4].text







#%%

def is_fever(r):
    
    '''
    input: Takes in a session.get('URL')
    output: Outputs if the drug helps with fevers or not
    
    '''

     
    fever=r.html.xpath('//ul[@class="list-unstyled table-list"]/../../*[contains(text(), "Associated Conditions")]/following::dd[1]', first=True)
    if not fever:
        return False
    if fever.text.find("Fever") >=0 or fever.text.find('Antipyretics') >=0 :  
        return True
    else:
        return False
    #brute force gets  the associate conditions with xpath



#%%

def is_painkiller(r):
    
    '''
    input: Takes in a session.get('URL')
    output: Outputs if the drug helps with pain or not
    
    '''
    
    pain = r.html.find('.list-unstyled' +'.table-list')
    if len(pain) <1:
        return False
    if pain[0].text.find("Painkiller") >=0 or pain[0].text.find("Pain") >=0  or pain[0].text.find('Analgesic') >=0 :  
        return True
    else:
        return False








#%%


def is_input(r,category):
    
    '''
    input: Takes in a session.get('URL') and a string input for category
    output: Outputs if the drug helps with the user input/ drug category
    is_input(r, input())
    
    '''
    
    looking_for = r.html.find('.list-unstyled' +'.table-list') 
    if len(looking_for) <2:
        return False
    if looking_for[0].text.find(str(category)) >=0  :  #looks at position for drug category fo what user input
        return True
    else:
        return False








#%%




def is_antihistamine(r):
    
    '''
    input: Takes in a session.get('URL')
    output: Outputs if the drug helps with allergies or asthma
    
    '''
    
    sneeze = r.html.find('.list-unstyled' +'.table-list')
    if len(sneeze) <2:
        return False
    if sneeze[1].text.find("Allergic") >=0 or sneeze[1].text.find("Asthma") >=0  :
        return True
    else:
        return False


#%%

#testing out some of the larger chunks of code

big_list = ['https://www.drugbank.ca/drugs/DB11073', 'https://www.drugbank.ca/drugs/DB06219', 'https://www.drugbank.ca/drugs/DB01580']


description_list=[]

for details in big_list:
    this_detail = session.get(details)
    description_list.append(drug_description(this_detail))
    
pprint(description_list) #this could be used for getting all the descriptions of the drugs you want
    
    
    
#%%
#test
# big_url_list= 

#looking up painkiller
my_search= session.get('https://www.drugbank.ca/unearth/q?utf8=%E2%9C%93&searcher=drugs&query=pain+killer')

max_pages = get_max_pages(my_search)
print(max_pages)  #gives 2 which is correct

all_the_pages = get_all_pages(my_search)
print(all_the_pages)
#prints out so works
#['https://www.drugbank.ca/unearth/q?c=_score&d=down&page=1&query=vitamin&searcher=drugs', 'https://www.drugbank.ca/unearth/q?c=_score&d=down&page=2&query=vitamin&searcher=drugs']


drugs_urls = get_all_drugs(all_the_pages) #this is what  I use to fill my csv below
pprint(drugs_urls)
#prints out all of the nice drugs that are in sech query
# ['https://www.drugbank.ca/drugs/DB00173',
#  'https://www.drugbank.ca/drugs/DB14484',





#testing if works
coke=drug_name(session.get('https://www.drugbank.ca/drugs/DB00907'))

print(coke) #prints cocaine


#test for my input / my medical condition
hist = session.get('https://www.drugbank.ca/drugs/DB00920') 
my_problem= 'Antihistamine'
if is_input(hist,my_problem)==True:
    print('helps with that problem')
else:
     print('doesnt help with that problem')


# test painkiller
advil = session.get('https://www.drugbank.ca/drugs/DB00316') 

if is_painkiller(advil)==True:
    print('helps with pain')
else:
      print('doesnt help with pain')
     
     
ascorbic_acid = session.get('https://www.drugbank.ca/drugs/DB00126')

if is_painkiller(ascorbic_acid)==True:
    print('helps with pain')
else:
      print('doesnt help with pain')     



# testing if drug is safe or not

Grepafloxacin= session.get('https://www.drugbank.ca/drugs/DB00365')   #i know it is not safe
if safe_drug(Grepafloxacin)==True:
    print('Safe')
else:
    print('Not Safe') 



#test if works antihistamine search works 
hist = session.get('https://www.drugbank.ca/drugs/DB00920') 

if is_antihistamine(hist)==True:
    print('helps with allergies')
else:
     print('doesnt help with allergies')


ascorbic_acid = session.get('https://www.drugbank.ca/drugs/DB00126')

if is_antihistamine(ascorbic_acid)==True:
    print('helps with allergies')
else:
     print('doesnt help with allergies')
     
#%%  



#filling up a csv file with my information that I gathered



csv_file = open('drug_scrape2.csv', 'w')

csv_writer = csv.writer(csv_file) #writing to the csv file



csv_writer.writerow(['drug name','url', 'drug description'])






my_output_list = []
for url in drugs_urls: #iterating through all the urls
    r = session.get(url)
    if not safe_drug(r): #if the drug is not safe then just contineu on and dont add it to csv
        continue
    keep_condition = is_fever(r) or is_painkiller(r) or is_antihistamine(r) or is_input(r,'Corticosteroids') #these are the keep conditions can be anything though
    print(keep_condition)
    if keep_condition:
        my_data = (drug_name(r), url, drug_description(r)) #if one of the keep conditions is met run all the functions on that url
        print(my_data)
        csv_writer.writerow(my_data) 


csv_file.close()

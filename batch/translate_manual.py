from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import LanguageTranslatorV3
from fake_headers import Headers
from unidecode import unidecode
from bs4 import BeautifulSoup
from csv import writer
import scrape as sc
import pandas as pd
import datetime
import requests
import winsound
import json
import uuid


'''
Steps to get key and service url:
1. visit: https://cloud.ibm.com/registration?target=%2Fapidocs%2Flanguage-translator%3Fcode%3Dpython
2. Sign up and verify your email
3. Log in again
4. Go to catalog -> services -> langauge-translator
5. Click 'Create' on bottom right to generate your key and service url
6. Click on 'Manage' to view key and service-url
7. Enter key in KEY and url in SERVICE_URL

steps to run:
1. On cli run `pip install ibm_watson`
2. Input is taken from non_eng.csv lying in the same working dir as this module
3. Check_size = True only returns the no. of chars in the websites given so you dont exceed your limit
4. Set check_size = False in __main__ to run the translator
5. Keep adding sites to the csv and they'll be appended to result_database/manual_data.csv
6. When done, set post_process = True to add uuid and header row, and remove repeated data

note 1: some pages contain a lot of chars (300k+) hence ibm limit would exceed, run would be failed and chars would be wasted
	  hence check for length before making api calls
note 2: if limit is exhausted, recreate an account using another email using the steps above
'''

KEY = ''
SERVICE_URL = ''

authenticator = IAMAuthenticator(KEY)
language_translator = LanguageTranslatorV3(
    version='2018-05-01',
    authenticator=authenticator
)
language_translator.set_service_url(SERVICE_URL)


def auto_detect_language(text):
	language = language_translator.identify(text).get_result()
	return language['languages'][0]['language']
def translate(text):
	translation = language_translator.translate(
	    text=text,
	    model_id='{}-en'.format(auto_detect_language(text))).get_result()
	return text,translation['translations'][0]['translation']

def size(soup):
	if len(soup.findAll('td'))==0:
		blocks = soup.findAll('div')
	elif len(soup.findAll('th'))==0:
		blocks = soup.findAll('td')
	else:
		blocks = soup.findAll('tr')
	length = 0
	for block in blocks:
		length+= len(block.get_text(separator=' ',strip=True).replace('\n',' ').replace('\t',' '))
	return length

def scraper(nation,url,soup):
	if len(soup.findAll('td'))==0:
		blocks = soup.findAll('div')
	elif len(soup.findAll('th'))==0:
		blocks = soup.findAll('td')
	else:
		blocks = soup.findAll('tr')

	result = []
	repeat_check = []
	for block in blocks:
		content = block.get_text(separator=' ',strip=True).replace('\n',' ').replace('\t',' ')
		if len(content)==0:
			continue
		try:
			content = translate(content)[1]
		except:
			print(content)
		content = unidecode(content)
		if content in repeat_check:                      # cleaner loop
			continue
		repeat_check.append(content)

		if sc.has_name(content) == 0:                     
			continue

		tags = block.findAll('a', href=True)             # to append related links
		links = [tag['href'] for tag in tags]

		imgs = block.findAll('img')                      # append related images
		img_list = []
		for img in imgs:
			try:
				src = img['src']
				img_list.append(src)
			except:
				continue
		links.extend(img_list)

		if links:
			for i in range(len(links)):
				if 'javascript' in links[i]:
					continue
				if links[i][:2] == '..':
					links[i] = links[i][2:]
				if 'http' not in links[i]:                # create visitable link
					links[i] = url + links[i]
		result.append([content,links])
	return result

def parse_soup(nation,url,soup):
    if soup is None:
        return
    content =  scraper(nation,url,soup)

    write_obj = open("./result_database/manual_data.csv", 'a+', newline='',encoding='utf-8')
    csv_writer = writer(write_obj)
    for items in content:
        prefix,ret_name,ministry = sc.returner(items[0])        
        l1 = [prefix.strip(),ret_name.strip(),ministry.strip()]
        if l1[0] == '' and l1[1] == '':     #no name no salutation //cleaner step
            continue
        if l1[1] in l1[2]:                  #name found in ministry //cleaner step
            continue
        if nation != 0:                     #0 if nation could not be retrieved from url
            l1.append(nation)
        else:
            l1.append('')
        l1.append(datetime.datetime.now())  #timestamp
        l1.append('PEP')                    #catagory
        image_url, facebook_url, instagram_url, twitter_url, other_urls = sc.link_parser(items[1])
        l1.extend((url,image_url, facebook_url, instagram_url, twitter_url, other_urls)) #urls
        csv_writer.writerow(l1)
    write_obj.close()

def main(size_flag,filename):
	headergen = Headers(headers=True)
	nations = pd.read_csv(filename,encoding= 'unicode_escape')
	for i in range(len(nations)):
		url = nations.iloc[i,0].strip()
		nation = nations.iloc[i,1].strip()
		response = requests.get(url,headers = headergen.generate()).content
		soup = BeautifulSoup(response, 'html.parser')
		if size_flag:
			print(f'{size(soup.body)} chars')
			continue
		parse_soup(nation,url,soup.body)

def postprocess():
    clean= ['Home','MPTrack','Shri','Smt','Dr','Mr','Mrs','Ms','cabinet','Minister','prime','Deputy','Ministry','Contact','Facebook','account','photo','mp','MP','Of','Biography','Email','Address','Roles','To','Read','more','Blog','Vacancies','Advertisement','Advertise','Office','Holding','Second','Member','Committee','Estimates','Fax','Find','Close','Links','Key','Figures','Stats','Statistics','Household','Full','name','Parks','Open','Menu','Languages','Opinion','Education','Address','Latest','Activity','Folketinget','Christiansborg','NA','PO','Father','Husband']
    banned = ['january','february','march','april','may','june','july','september','october','november','december','monday','tuesday','wednesday','thursday','friday','saturday','sunday','Party']
    try:
        df = pd.read_csv("result_database/manual_data.csv",names=['Prefix','Name','Designation','Nation','Created_date_time','Profile_Category','Source','Img_link','Facebook_account','Instagram_account','Twitter_account','Other_weblinks'],encoding= 'unicode_escape')
    except:
        return
    df = df.applymap(str)
    df.replace(to_replace = 'nan', value = '', inplace = True)
    print("Postprocessing...")
    
    df.dropna(subset=['Name'],inplace=True)
    df.drop_duplicates(subset=['Name'], keep='first',inplace=True)
    df.reset_index(drop=True, inplace=True)

    for count,_ in enumerate(df['Name']):
        if  len(df['Name'][count])<4:
            df.drop(count,axis=0,inplace=True)
            continue
        
        if  df['Prefix'][count].isnumeric() or len(df['Prefix'][count])>15:
            df.at[count, 'Prefix'] = ''
        if 'Home' in df['Prefix'][count]:
            df.at[count, 'Prefix'] = df['Name'][count].replace('Home','')
        for item in df['Name'][count].split(' '):
            if len(item)<2:
                df.at[count, 'Name'] = df['Name'][count].replace(item,'')
            for word in clean:
                if word in item:
                    new_val = df['Name'][count].replace(word,'').strip()
                    df.at[count, 'Name'] = new_val
            for ban in banned:
                if ban in item.lower():
                    df.drop(count,axis=0,inplace=True)
                    break
            else:
                continue
            break
                    

    df.dropna(subset=['Name'],inplace=True)
    df.drop_duplicates(subset=['Name'], keep='first',inplace=True)
    df.reset_index(drop=True, inplace=True)
    uuids = []
    for _ in range(len(df)):
        uuids.append(uuid.uuid4().hex)
    df.insert(0, '_id', uuids)

    print("Postprocessing complete. Database contains {} rows".format(len(df)))
    df.to_csv("result_database/manual_data.csv",index=False)

if __name__ == '__main__':

	csvpath = './non_eng.csv' #separate csv for manual scraping
	check_size = True      #check length of webpage before running translator
	post_process = False   #run once only after all sites are done
	
	if not post_process:
		main(check_size,csvpath)

	if post_process:
		postprocess()		  
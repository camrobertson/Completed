# Import all libraries needed for the tutorial

# General syntax to import specific functions in a library: 
##from (library) import (specific library function)
from pandas import DataFrame, read_csv

# General syntax to import a library but no functions: 
##import (library) as (give the library a nickname/alias)
import matplotlib.pyplot as plt
import pandas as pd #this is how I usually import pandas
import sys #only needed to determine Python version number
import matplotlib as mpl #only needed to determine Matplotlib version number
import urllib3
import re
import pandas as pd
from bs4 import BeautifulSoup
import csv

"""Order:
#get_data = get the data from each respective website.  Once per year
get_data calls add_data, to split up and add the data to drugs_dict
add_data calls add_drug, to be sure that there is an instance for each drug. 

WORKS!!!!!!!!!!
"""


class Drugs(object):

	def __init__(self, name, company = 'Generic Drug', rev2013 = 'NA', rev2012 = 'NA', rev2011 = 'NA', rev2010 = 'NA', refno = 'NA'):
		self.name = name
		self.rev2013 = rev2013
		self.rev2012 = rev2012
		self.rev2011 = rev2011
		self.rev2010 = rev2010
		self.company = company
		self.refno = refno

#gets the data from the websites
def get_data(page, year, drugs_dict):
	http = urllib3.PoolManager()
	r = http.request('GET', page)

	soup = BeautifulSoup(r.data, "html.parser")

	###get all groups
	items = soup.find_all("tr")
	data = []
	for i in items[1:101]: data.append(i.get_text('|', strip = True))

	s = pd.Series(data)
	s2 = s.str.split('|')
	
	drugs_dict = add_data(year, s2, drugs_dict)
	
	return(drugs_dict)

	
def hasNumbers(inputString):
	return any(char.isdigit() for char in inputString)

	
#build the dictionary with teh names from all the sets. 
def add_drug(drug, drugs_dict):
	#for drug in drugs: 
	if drug in drugs_dict: next
	else: drugs_dict[drug] = Drugs(drug)
	return drugs_dict

	
def add_data(year, s2, drugs_dict):
	
	for i in s2:
		if len(i)<5: #was 4, changed to 5 to try to narrow smaller elements
			print (i)
			drugs_dict = add_drug(i[1], drugs_dict)
			print (len(i))
			for j in range(1, len(i)): 
				if hasNumbers(i[j]):
					print("revenue is: ", i[j])
					if year == '2010': drugs_dict[i[1]].rev2010 = i[j]
					if year == '2013': drugs_dict[i[1]].rev2013 = i[j]
					if year == '2012': drugs_dict[i[1]].rev2012 = i[j]
					if year == '2011': drugs_dict[i[1]].rev2011 = i[j]
				next 
		else:
			#print(i)
			drugs_dict = add_drug(i[-4], drugs_dict)
			drugs_dict[i[-4]].company = i[-3]

			if year == '2010': drugs_dict[i[-4]].rev2010 = i[-2]
			if year == '2013': drugs_dict[i[-4]].rev2013 = i[-2]
			if year == '2012': drugs_dict[i[-4]].rev2012 = i[-2]
			if year == '2011': drugs_dict[i[-4]].rev2011 = i[-2]
	
	return drugs_dict	
		

		
def add_fda_no(drugs_dict, name):
	num = []
	dname = []
	with open(name) as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			
			
			num.append(row['ApplNo'])
			dname.append(row['DrugName'])
				
	for i in dname:
		if i in drugs_dict: drugs_dict[i].refno = "Found"
		else: next
		
	return drugs_dict
"""
#Open the .txt files as csvs. 
products = pd.read_csv('./target/Products.txt', low_memory = False)
print("open 1")
submissions = pd.read_csv('./target/Submissions.txt')
print("open 2")
sub_db = pd.merge(products, submissions, on=['ApplNo'])
sub_db.to_csv('./target/sub_db.csv')
"""		


#Main#

drugs_dict = {}
	
page_2013 = "https://www.drugs.com/stats/top100/2013/sales"
page_2012 = "https://www.drugs.com/stats/top100/2012/sales"
page_2011 = "https://www.drugs.com/stats/top100/2011/sales"
page_2010 = "https://www.drugs.com/top200.html"
page_2009 = "https://www.drugs.com/top200_2009.html"
page_2008 = "https://www.drugs.com/top200_2008.html"
products_file = './target/Products.txt'

drugs_dict = get_data(page_2013, '2013', drugs_dict)
drugs_dict = get_data(page_2012, '2012', drugs_dict)
drugs_dict = get_data(page_2011, '2011', drugs_dict)
drugs_dict = get_data(page_2010, '2010', drugs_dict)
drugs_dict = add_fda_no(drugs_dict, products_file)

#current section 05_13
with open('drug_rev_data.csv', 'w', newline='') as csvfile:
	spamwriter = csv.writer(csvfile, delimiter=':', quotechar='|', quoting=csv.QUOTE_MINIMAL)
	for i in drugs_dict:
		spamwriter.writerow([drugs_dict[i].name, drugs_dict[i].refno, drugs_dict[i].company, drugs_dict[i].rev2013, drugs_dict[i].rev2012, drugs_dict[i].rev2011, drugs_dict[i].rev2010]) 

"""for i in drugs_dict: print("\n\n", drugs_dict[i].name, "\nDrugNo ", drugs_dict[i].refno, "\nCompany: ", drugs_dict[i].company, "\n2013: ", drugs_dict[i].rev2013, "\n2012: ", drugs_dict[i].rev2012, "\n2011: ", drugs_dict[i].rev2011, "\n2010: " 
, drugs_dict[i].rev2010)
print ("\nLength of list: ", len(drugs_dict))
"""
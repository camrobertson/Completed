""" Aim is to read txt file from FAERS database as a csv with delimiter $
3/1/2018 - data is just scrapped, with no initial screen by REPT_COD, AGE, SEX, etc.
3/3/3018 - 
	streamlined process,  allocated key processes into functions
	inserted a counter / cap to help test if it's working. 
	Included drug name and date of approval from FDA sub files


From DRUG (DRUGyyQq.TXT)
	- PRIMARYID [0]
	- CASEID	[1]
	- DRUGNAME	[4]
	- NDA_NUM	[15]
	
From DEMOGRAPHIC (DEMOyyQq.TXT)
	- PRIMARYID (Used to match) [0]
	- CASEID					[1]
	- CASEVERSION (not added in first version) [2]
	- EVENT_DT (May be a partial date)			[4]
	- FDA_dt -- when FDA received the event ... more complete [5]

From Drugs@FDA
	- DRUGNAME
	- NDA_NUM
	- DATE Original App was approved (may need to filter to ensure original app, not supp)
	- DATE first ANDA was approved
	- Type of approval (Priority, Accelerated)
	- From Drug Products file, Priority / Standard = [7]
	
"""
	
	
import csv
import datetime
import gc
import random
from collections import Counter


class Drugs(object):
	def __init__(self, primaryid, caseid, caseversion, NDA_NUM = "", drug_seq = "", drugname=[], FDA_dt = [], appr_dt = 'NA', exp_path = '', tot_yr = ''):
 
		self.primaryid = primaryid
		self.caseid = caseid
		self.caseversion = caseversion
		self.FDA_dt = []
		self.drugname = []
		self.NDA_NUM = NDA_NUM
		self.exp_path = []
		self.appr_dt = appr_dt
		self.drug_seq = drug_seq
		self.tot_yr = tot_yr


def add_ae_report(primaryid, caseid, caseversion, FDA_dt, drugs_dict):
	#for drug in drugs: 
	#if drug.upper() in drugs_dict: next
	drugs_dict[primaryid] = Drugs(primaryid, caseid, caseversion)
	drugs_dict[primaryid].FDA_dt.append(FDA_dt)
	return drugs_dict
 
 
def get_NDA(drug, products, name_match):
	for h in products:
		if len(h) > 5:
			if h[5] in drug.drugname:
				drug.NDA_NUM = h[0]
				name_match += 1
	return drug, name_match
	

def get_len_demo_ae():
	with open (demo_ae_files) as p:
		reader = csv.reader(p, delimiter='$')
		demo_ae = list(reader)
	return len(demo_ae), demo_ae
	

def init_demo_ae(drugs_dict, total, key_tracker, counter, iter_updates, demo_ae, x, tally):
	total = counter + iter_updates
	''' Removing drug_ae from inherited variables to improve efficiency ... might need to replace
	with open (demo_ae_files) as p:
		reader = csv.reader(p, delimiter='$')
		demo_ae = list(reader) 
	'''
	if total == 0: total = len(demo_ae)
	#Stopping it from counting the same numbers over and over...for j in range(counter, total):
	
	for i in demo_ae[counter:total]:
		dice = random.randrange(x)
		#print(dice)
		if counter >= total: break
		counter += 1
		if dice > 0: continue  #RANDOM GENERATOR TO SEE IF IT SPEEDS IT UP -- remove if this totally messes with teh times or doesn't change at all
		#print (dice, "is = 0")
		#print(i)
		drugs_dict = add_ae_report(i[0], i[1], i[2], i[5], drugs_dict)
		key_tracker.append(i[0])
		tally += 1
	#print ("number of files initiated: ", total)
	#print(counter)
	return drugs_dict, key_tracker, counter, tally


def init_drug_ae(drugs_dict, drug_ae, key_tracker):
	"""removing drug_ae from the inherited variables for efficiency ... need to replace it if this doesn't work
	with open (drug_ae_files) as f:
		reader = csv.reader(f, delimiter='$')
		drug_ae = list(reader) 
	"""
		#for i in [*drugs_dict]: #i should be the key for each dict item. --> this is the original line that worked. 
	for i in key_tracker:	#should have the same effect as above, except will allow to reinitialize. 
		for j in drug_ae:
			if i == j[0]:  #if the dict key matches the primary id of drug_ae line
				if j[3] == 'PS':
					if j[4] in drugs_dict[i].drugname: continue #we've already recorded a primary suspect drug for that primaryid
					else: 
						drugs_dict[i].drug_seq = j[3]
						drugs_dict[i].drugname.append(j[4])
						if j[15]: drugs_dict[i].NDA_NUM = j[15]
				break
	return drugs_dict

def add_sub_prod(drugs_dict, key_tracker):
	with open ('submissions.txt') as f:
		reader = csv.reader(f, delimiter = '\t')
		submissions = list(reader)
	
	with open ('products.txt') as p:
		reader = csv.reader(p, delimiter = '\t')
		products = list(reader) 

	#Added some counters to get a sense of how we're doing.
	total_counter = 0
	name_match = 0
	NDA_match = 0
		
	for i in key_tracker:
		#DEBUG CODE if input('\nBreak?') == 'Y': break 
		total_counter += 1
		if drugs_dict[i].NDA_NUM == "":
			drugs_dict[i], name_match = get_NDA(drugs_dict[i], products, name_match)
		
		for j in submissions:
				#DEBUG CODE print(drugs_dict[i].NDA_NUM, " :: ", j[0])
			if drugs_dict[i].NDA_NUM == j[0]:
				drugs_dict[i].appr_dt = j[5]
				drugs_dict[i].exp_path.append(j[7])
				NDA_match += 1
				break
	
	return drugs_dict, name_match, NDA_match, total_counter		


def hasNumbers(inputString):
	return any(char.isdigit() for char in inputString)
	
	
def get_time_lapse(reports_lib, reports_list, drugs_dict, key_tracker):
	
	for i in key_tracker:
		#print("Key: ", i, "Drugs_Dict: ", drugs_dict[i].NDA_NUM)
		FDA_dt = drugs_dict[i].FDA_dt
		appr_dt = drugs_dict[i].appr_dt
		if hasNumbers(FDA_dt):
			#print("YES POINT C!!!")
			#print("Approval Date: ", appr_dt)
			if hasNumbers(appr_dt):
				#print ("YES POINT D!!!")
				FDA_dt_yr = FDA_dt[0][:4]
				appr_dt_yr = str(appr_dt[:4])
				tot_yr = int(FDA_dt_yr) - int(appr_dt_yr)
				
				reports_list.append(tot_yr)
				drugs_dict[i].tot_yr = tot_yr
				reports_lib.setdefault(tot_yr, []).append(drugs_dict[i].NDA_NUM)
				#reports_lib[drugs_dict[i].primaryid] = tot_yr

				#print(reports_lib[tot_yr])
				#print ("Year Reported:\t", FDA_dt_yr, "\tYear Approved:\t", appr_dt_yr, "\tTotal Years:\t", tot_yr)
		#else: print("NO POINT C!!")
	return reports_lib, reports_list, drugs_dict
	
def frequency_count(itt, nr_bins, minn=None, maxx=None):  #swiped from the web
	ret = []
	if minn < 0:
		minn = min(itt)
	if maxx < 0:
		maxx = max(itt)
	binsize = (maxx - minn) / float(nr_bins) #man, do I hate int division

	#construct bins
	ret.append([float("-infinity"), minn, 0]) #-inf -> min
	for x in range(0, nr_bins):
		start = minn + x * binsize
		ret.append([round(start, 2), round(start+binsize, 2), 0])
	ret.append([maxx, float("infinity"), 0]) #maxx -> inf

	#assign items to bin
	for item in itt:
		for binn in ret:
			if binn[0] <= item < binn[1]:
				binn[2] += 1		
	
	#for i in ret: print (i)  DEBUG CODE
	return ret, binsize 
	
def write_drugs_csv(drugs_dict, save_file):
	with open(save_file, 'w', newline='') as csvfile:
		spamwriter = csv.writer(csvfile, delimiter=':')
		spamwriter.writerow(["Primary_ID", "Case_ID", "Case_Version", "FDA_dt", "Drug_name", "NDA_NUM", "approval_dt", "exp_path", "drug_seq", "tot_yr"])
		for i in drugs_dict:
			spamwriter.writerow([
				drugs_dict[i].primaryid,
				drugs_dict[i].caseid,
				drugs_dict[i].caseversion,
				drugs_dict[i].FDA_dt,
				drugs_dict[i].drugname,
				drugs_dict[i].NDA_NUM,
				drugs_dict[i].appr_dt,
				drugs_dict[i].exp_path,
				drugs_dict[i].drug_seq,
				drugs_dict[i].tot_yr
				])

#GET THIS RIGHT ON SUNDAY.. 
def write_report(ret, num_of_buckets, starttime, tally, counter, time_final, total_len, cycles, report_file, ret_minn, ret_maxx, rand_rang, total, file_quarter):
	thefile = open(report_file, 'w')
	thefile.writelines([
		"Time_Start: ", str(starttime)[:-5], "\tEnd_Time: ", str(time_final)[:-5], 
		"\nFiles tallied: ", str(tally), "\tCounter: ", str(counter), "\tCycles: ", str(cycles),
		"\nNumber of Buckets:", str(num_of_buckets), "\tMin: ", str(ret_minn), "\tMax: ", str(ret_maxx), 
		"\nRandom Sample: ", str(100/rand_rang), "%\tTotal:", str(total), "File Quarter", file_quarter])
	for i in ret: 
		for x in i:
			thefile.write("%s," % x)
		thefile.write("\n")


def write_distribution(reports_lib, num_of_buckets, file_quarter, dist_file):
	with open(dist_file, 'w', newline='') as csvfile:
		spamwriter = csv.writer(csvfile, delimiter=',')
		spamwriter.writerow(["Year", "Instances", "List"])
		for i in reports_lib:
			spamwriter.writerow([i, len(set(reports_lib[i])), set(reports_lib[i])])
			#print(i, len(reports_lib[i]), reports_lib[i])

def write_frequency(reports_lib, num_of_buckets, file_quarter, freq_file):
	with open(freq_file, 'w', newline='') as csvfile:
		spamwriter = csv.writer(csvfile, delimiter=',')
		spamwriter.writerow(["Year", "Frequency: List"])
		for i in reports_lib:
			spamwriter.writerow([i, Counter(reports_lib[i])])
			#print("Reports Lib ", i, Counter(reports_lib[i]))
		
"""main"""


#Identify File Locations


#initiate variables: 
#initiate dictionary, where key = primaryid, value = [list of drugs]

starttime = datetime.datetime.now()
num_of_buckets = 35
ret_minn = 	0							#Sets up the lower value for histogram - set to < 0 to create automatically
ret_maxx = 	35							#Sets up higher limit - set to < 0 to create automatically
total = 0							#specifiy the number of files to create per quarter;  if set to 0, will go for the full list. 
iter_updates = 50000					#specifies how often the tally should be updated... need to also set to 0 to run full list.
counter = 0								#tracks position in overall process, so updates can be provided in near real time. keep initalized at 0
rand_rang = 5							#Set to 1/x to get % of files (e.g., set to 4 to get 25% of files, 5 to get 20%, 1, to get 100%
tally = 0								#Tally count to find out how many of total files were added. 
drugs_dict = {}
reports_list = []
cycle_times = []
key_tracker = []
ret = []								#RET is the return tally of bin size and number of values for histogram
reports_lib={}
file_quarters = ["15Q4", "15Q3", "15Q2", "15Q1", "14Q4", "14Q3", "14Q2"] #"17Q3", "17Q2", "17Q1", "16Q4", "16Q3", "16Q2", "16Q1"] #,
"""
file_quarters = ["17Q2", 
				"17Q1",
				"16Q4", 
				"16Q3",
				"16Q2", 
				"16Q1", 
				"15Q4", 
				"15Q3", 
				"15Q2", 
				"15Q1"]
				"14Q4", 
				"14Q3",
				"14Q2"]#File quarter for each 
"""			

for file_quarter in file_quarters:


	print("\n\n\n\n****\nRUN: ", file_quarter, "\n****")
	save_file = "Reports/DRUG%s_Dictionary_compiled.txt" % file_quarter
	report_file = "Reports/DRUG%s_Primary_report.txt" % file_quarter
	dist_file = "Reports/DRUG%s_drug_ae_instances.txt" % file_quarter
	freq_file = "Reports/DRUG%s_drug_ae_frequency.txt" % file_quarter

	drug_ae_files = 'C:/Users/Andrew/Documents/Python_Scripts/FDA_Scripts/FAERS/faers_ascii_20%s/ascii/DRUG%s.txt' % (file_quarter, file_quarter)
	demo_ae_files = 'C:/Users/Andrew/Documents/Python_Scripts/FDA_Scripts/FAERS/faers_ascii_20%s/ascii/DEMO%s.txt' % (file_quarter, file_quarter)

	total_len, demo_ae = get_len_demo_ae()	#Need a stopping point. Also, opens file and demo_ae data 

	#gc.collect()
	#New section to open file once. 
	with open (drug_ae_files) as f:
		reader = csv.reader(f, delimiter='$')
		drug_ae = list(reader) 

	if total == 0:
		if (iter_updates == 0): cycles = total_len
		else: cycles = int(total_len/iter_updates)
	else: cycles = int(total/iter_updates)

	print("Total Number Reports:\t", total, "of", total_len, '\n')
	print("Update Frequency:\t", iter_updates, " Reports")
	print("Total Number Cycles:\t",  cycles, '\n\n\n')

	for i in range(cycles):
		print ("FileQuarter: ", file_quarter, "Cycle ", i+1, "of", cycles)
		key_tracker = [] #reinitialize the key_tracker for each cycle.  

		#Start with Demo data base since the primary ID are unique per line.
		#key_tracker is reinitialized each time in init_demo_ae, and should track the keys for this round of the loop
		drugs_dict, key_tracker, counter, tally = init_demo_ae(drugs_dict, total, key_tracker, counter, iter_updates, demo_ae, rand_rang, tally)
		#print ("Step 1 complete", "\nTIME: ", (datetime.datetime.now() - starttime))
		
		#Next, search each primary id and append the list of drugs involved.	
		drugs_dict = init_drug_ae(drugs_dict, drug_ae, key_tracker)		
		#print ("\nKeyTracker in Main", key_tracker)
		#gc.collect() #inserting this to clear the memory ... will take a look at the runtimes. 
		#input the submissions and product data entered from FDA, saved as final_dict
		#COMMENTED OUT TO OPTIMIZE
		drugs_dict, name_match, NDA_match, total_counter = add_sub_prod(drugs_dict, key_tracker)
		#print ("Step 3 complete", "\nTIME: ", (datetime.datetime.now() - starttime))

		print ("Cycle ", i+1, " of", cycles, " complete", "\tTIME: ", str(datetime.datetime.now() - starttime)[:-5], "\t", tally, ' of ', counter, "files indexed")

		cycle_times.append(datetime.datetime.now() - starttime)
		#print("\nFound w/ Name_Match: \t", name_match, 
		#		"\nNDA Match: \t", NDA_match, 
		#		"\nTotal Counter: \t", total_counter)
				

		#Next, calculate (in years) time between approval and FDA report		
		reports_lib, reports_list, drugs_dict = get_time_lapse(reports_lib, reports_list, drugs_dict, key_tracker)
		#print ("Step 3 complete", "\nTIME: ", (datetime.datetime.now() - starttime))
		#print ("keys_tracked: ", key_tracker, '\n\n')
		#Set up histogram
		ret, binsize = frequency_count(reports_list, num_of_buckets, ret_minn, ret_maxx)
		
		#DEBUG CODE: if input('\nBreak?') == 'Y': break
		
		#for j in i:
		#	print (round(j, 2))
		#print("REPORTS LIB POINT A HAS", reports_lib)
		#print("\nDict_length: ", len(drugs_dict), "\tFiles Added: ", ret)
		
		
	count = 0
	for i in cycle_times:
		print ("Cycle: ", count, "\tTime: ", i)
		count += 1
		
	print ("Start Time :", starttime)
	print ("File ", drug_ae_files[-8])
	print (tally, " of ", counter, "files added")
	print ("\nWriting Files for: ", file_quarter) 	
	
	time_final = datetime.datetime.now() - starttime
	write_drugs_csv(drugs_dict, save_file)
	write_report(ret, num_of_buckets, starttime, tally, counter, time_final, total_len, cycles, report_file, ret_minn, ret_maxx, rand_rang, total, file_quarter)
	write_distribution(reports_lib, num_of_buckets, file_quarter, dist_file)
	write_frequency(reports_lib, num_of_buckets, file_quarter, freq_file)
	
	drugs_dict = {}
	reports_list = []
	cycle_times = []
	key_tracker = []
	ret = []								#RET is the return tally of bin size and number of values for histogram
	reports_lib={}
	counter = 0						#Restart the counter




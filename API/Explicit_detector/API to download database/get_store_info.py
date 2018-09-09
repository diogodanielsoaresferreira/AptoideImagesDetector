# Diogo Daniel Soares Ferreira
# diogodanielsoaresferreira@ua.pt
# Aptoide, 2016

# This script receives an argument the maximum number of id's to search.
# It connects to the database and saves information on the id's that were not processed yet.
# Example: python get_store_info.py 20

from bs4 import BeautifulSoup
import urllib
import urllib2
import json
import sys, traceback
import sqlite3
import os

# In the future, change to a more robust database system (MySQL, ...)

# Database has two tables:

# App_data:
# Id|Title|Age|Description|wurl|category|repo

# Crawl_list
# id|is_processed|date|search_tags

# Rarely, some applications are not parsed due to errors on Beautiful Soup parser.


def get_store_info(db, **keyword_parameters):
	url = "http://webservices.aptoide.com/webservices/3/getApkInfo/id:"

	c = db.cursor()
	c.execute(''' SELECT id FROM crawl_list ''')

	i = 0

	# Check if exists a maximum value for the list to be crawled
	if 'max_value' in keyword_parameters and keyword_parameters['max_value']>0:
		i = keyword_parameters['max_value']
	
	text=""

	# For all id's fetched
	for sid in c.fetchall():
		print sid[0]
		c.execute(''' SELECT is_processed FROM crawl_list WHERE id=? ''', (sid[0],))
		if c.fetchone()[0]==1:
			print str(sid[0])+" was already crawled"
			
		else:
			c.execute(''' UPDATE crawl_list SET is_processed=1 WHERE id=? ''',(sid[0],))
			if 'max_value' in keyword_parameters and keyword_parameters['max_value']>0:
				i-=1
			try:
				webpage = urllib2.urlopen(url+str(sid[0])+"/json")
				soup = BeautifulSoup(webpage, "lxml")
			
				text = soup.get_text()

				page = json.loads(text)
				if page['status']!='FAIL':

					repo = page['apk']['repo']

					name = page['meta']['title']			
					print name

					description = page['meta']['description']

					wurl = page['meta']['wurl']
					categories = []

					for cat in page['meta']['categories']['standard']:
						categories.append(cat['name'])

					for cat in page['meta']['categories']['custom']:
						categories.append(cat['name'])

					scr = []
					scr_hd = []

					if 'sshots' in page['media']:
						for s in page['media']['sshots']:
							scr.append(s)

					if 'sshots_hd' in page['media']:
						for s in page['media']['sshots_hd']:
							scr_hd.append(s['path'])

					maj = page['meta']['min_age']

					exp = False

					if maj>=18:
						exp=True

					icon = page['apk']['icon']

					icon_hd = []
					if 'icon_hd' in page['apk']:
						icon_hd = page['apk']['icon_hd']

					filename, file_extension = os.path.splitext(icon)
							
					path = os.path.join(os.getcwd(),"images/icon/"+str(sid[0])+file_extension)

					resource = urllib.urlopen(icon)
					output = open(path,"w+")
					output.write(resource.read())
					output.close()

					if exp==True:
						path = os.path.join(os.getcwd(),"images/icons_explicit/"+str(sid[0])+file_extension)

						resource = urllib.urlopen(icon)
						output = open(path,"w+")
						output.write(resource.read())
						output.close()
					else:
						path = os.path.join(os.getcwd(),"images/icons_non-explicit/"+str(sid[0])+file_extension)

						resource = urllib.urlopen(icon)
						output = open(path,"w+")
						output.write(resource.read())
						output.close()

					if icon_hd:
						filename, file_extension = os.path.splitext(icon_hd)

						path = os.path.join(os.getcwd(),"images/icon/"+str(sid[0])+"_hd"+file_extension)

						resource = urllib.urlopen(icon_hd)
						output = open(path,"w+")
						output.write(resource.read())
						output.close()

						if exp==True:
							path = os.path.join(os.getcwd(),"images/icons_explicit/"+str(sid[0])+"_hd"+file_extension)

							resource = urllib.urlopen(icon_hd)
							output = open(path,"w+")
							output.write(resource.read())
							output.close()
						else:
							path = os.path.join(os.getcwd(),"images/icons_non-explicit/"+str(sid[0])+"_hd"+file_extension)

							resource = urllib.urlopen(icon_hd)
							output = open(path,"w+")
							output.write(resource.read())
							output.close()

					n=0
					for screenshot in scr:
						filename, file_extension = os.path.splitext(screenshot)

						path = os.path.join(os.getcwd(),"images/screenshots/"+str(sid[0])+"_"+str(n)+file_extension)

						resource = urllib.urlopen(screenshot)
						output = open(path,"w+")
						output.write(resource.read())
						output.close()

						if exp==True:
							path = os.path.join(os.getcwd(),"images/screenshot_explicit/"+str(sid[0])+"_"+str(n)+file_extension)

							resource = urllib.urlopen(screenshot)
							output = open(path,"w+")
							output.write(resource.read())
							output.close()
						else:
							path = os.path.join(os.getcwd(),"images/screenshot_non-explicit/"+str(sid[0])+"_"+str(n)+file_extension)

							resource = urllib.urlopen(screenshot)
							output = open(path,"w+")
							output.write(resource.read())
							output.close()
						n+=1

					n=0
					for screenshot in scr_hd:
						filename, file_extension = os.path.splitext(screenshot)

						path = os.path.join(os.getcwd(),"images/screenshots/"+str(sid[0])+"_"+str(n)+"_hd"+file_extension)

						resource = urllib.urlopen(screenshot)
						output = open(path,"w+")
						output.write(resource.read())
						output.close()

						if exp==True:
							path = os.path.join(os.getcwd(),"images/screenshot_explicit/"+str(sid[0])+"_"+str(n)+"_hd"+file_extension)

							resource = urllib.urlopen(screenshot)
							output = open(path,"w+")
							output.write(resource.read())
							output.close()
						else:
							path = os.path.join(os.getcwd(),"images/screenshot_non-explicit/"+str(sid[0])+"_"+str(n)+"_hd"+file_extension)

							resource = urllib.urlopen(screenshot)
							output = open(path,"w+")
							output.write(resource.read())
							output.close()

						n+=1

					c.execute(''' INSERT INTO app_data VALUES(?,?,?,?,?,?,?) ''', (sid[0],name,maj,description,wurl,''.join(categories),repo,))
					db.commit()
			except:
				print "Error during parsing"
				traceback.print_exc(file=sys.stdout)
				#print text

		if 'max_value' in keyword_parameters and keyword_parameters['max_value']>0:
			if i==0:
				break
			
			

def reset_database(db):
	c = db.cursor()
	c.execute(''' UPDATE crawl_list SET is_processed=0 ''')
	c.execute(''' DROP TABLE app_data ''')
	c.execute('''create table app_data(id BIGINT, title text , age TINYINT, description text,wurl text, category text, repo text)''')
	db.commit()

if __name__=="__main__":

	db = sqlite3.connect('app_info.db')

	if len(sys.argv)>1:
		try:
			get_store_info(db, max_value=int(sys.argv[1]))
		except:
			if(sys.argv[1]=='-r'):
				reset_database(db)
				db.close()
				exit()
			get_store_info(db)
	else:
		get_store_info(db)
	c = db.cursor()
	c.execute(''' SELECT id FROM app_data ''')
	print len(c.fetchall())
	#print c.fetchall()
	#c.execute(''' SELECT * FROM crawl_list ''')
	#print c.fetchall()
	db.close()

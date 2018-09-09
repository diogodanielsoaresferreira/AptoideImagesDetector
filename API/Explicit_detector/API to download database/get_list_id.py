# Diogo Daniel Soares Ferreira
# diogodanielsoaresferreira@ua.pt
# Aptoide, 2016

# This script receives as argument the words on query and (optional) the maximum value
# for apps searched. Then, saves the id to a database and mark the as no processed.
# Example: python get_list_id.py games 20

from bs4 import BeautifulSoup
import urllib2
import json
import sys
import re
import time
import sqlite3


# Database has two tables:

# app_data:
# Id|Title|Age|Description|wurl|category|repo

# crawl_list
# id|is_processed|date|search_tags

# If there are double quotes on description, removes them
def replaceChar(jstr):
    newStr = ''
    while len(jstr.split('"description":"')) != 1:
        [sl, sr] = jstr.split('"description":"', 1)
        newStr += sl
        [sinner, jstr] = sr.split('"},"stats":', 1)
        sinner = sinner.replace('"', ' ')
        newStr += '"description":"'
        newStr += sinner
        newStr += '"},"stats":'
    else:
        newStr += jstr
    return newStr


def get_list_id(db, query, **keyword_parameters):

	url = "http://ws2.aptoide.com/api/7/listSearchApps/query="
	i=0
	offset=0
	total=1
	c = db.cursor()

	# Check if exists a maximum value for the id's list
	if 'max_list' in keyword_parameters and keyword_parameters['max_list']>0:
		i = keyword_parameters['max_list']

	try:
		while offset < total:
			webpage = urllib2.urlopen(url+query+"/offset="+str(offset))
			soup = BeautifulSoup(webpage, "lxml")
			try:
				# Remove double quotes in description
				text = replaceChar(soup.get_text())

				page = json.loads(text)
				data = page['datalist']['list']
				
				# Adding app id's
				for app in data:
					if 'max_list' in keyword_parameters and keyword_parameters['max_list']>0:
						if i==0:
							break
						i -= 1

					# Saves on the database
					c.execute(''' SELECT id FROM crawl_list WHERE id=? ''', (app['id'],))
					try:
						if c.fetchone():
							print str(app['id'])+" already exists in the database"
							
						else:
							c.execute(''' INSERT INTO crawl_list VALUES (?,?,?,?) ''', (app['id'],0,time.time(),query,))
							db.commit()
					except:
						print "Could not save in the database"
						exit(1)

				# Updates next page content
				offset = int(page['datalist']['next'])
				total = int(page['datalist']['total'])

				if 'max_list' in keyword_parameters and keyword_parameters['max_list']>0:
					if i==0:
						break
			except:
				print "Error while parsing json document"
				print "Webpage ignored"
				offset += 25

	except urllib2.HTTPError:
		print "Error while fetching from database."

def reset_database(db):
	c = db.cursor()
	c.execute(''' DROP TABLE crawl_list''')
	c.execute('''create table crawl_list(id BIGINT, is_processed TINYINT, date BIGINT, search_tags text)''')
	db.commit()

if __name__=="__main__":
	query = ""
	maxvalue = 0
	i=1
	db = []

	db = sqlite3.connect('app_info.db')

		# Parsing command-line arguments
	if len(sys.argv)>=2:
		if sys.argv[1]=='-r':
			reset_database(db)
			exit(0)
		while i<len(sys.argv):
			if i!=1 and i==len(sys.argv)-1:
				try:
					maxvalue = int(sys.argv[i])
				except ValueError:
					query += sys.argv[i]
			else:
				query += sys.argv[i]
			i+=1

		get_list_id(db, query, max_list = maxvalue)
			
	c = db.cursor()
	c.execute(''' SELECT id FROM crawl_list ''')
	print (len(c.fetchall()))
	#print c.fetchall()

	db.close()



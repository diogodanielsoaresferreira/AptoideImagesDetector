# Diogo Daniel Soares Ferreira
# diogodanielsoaresferreira@ua.pt
# Aptoide, 2016

# API in Django to deploy the analysis of an app, given its MD5 or ID.
# Just start the server and write the following url:
# http://127.0.0.1:8000/detect_mature/md5sum=md5_of_app
# or
# http://127.0.0.1:8000/detect_mature/id=md5_of_app

# If you don't have acess to local images, change the config.json "local_or_web_images" to "web" instead of "local"

from threading import Thread
import os
from django.http import HttpResponse
from django.shortcuts import redirect
from django.db.models.base import ModelBase
from bs4 import BeautifulSoup
from datetime import datetime, time
from Explicit_detector import analyse_app
import threading
import urllib2
import json
import sqlite3

# Save the Illustration2Vec model on memory
# Not needed to load everytime that exists a request
class Model(ModelBase):
	_model = analyse_app.get_model()
	_local = True

# Decorator to use for multi-threading
def postpone(function):
  def decorator(*args, **kwargs):
    t = Thread(target = function, args=args, kwargs=kwargs)
    t.daemon = True
    t.start()
  return decorator

# Gets the local url of an image
def local_url(parent_dir, image_path):
	try:
		image_path = image_path['path']
	except:
		pass
	path = image_path.split("/")[-1:][0]
	final_path = "/"+parent_dir+"/"+path[0]+"/"+path[1]+"/"+path[2]+"/"+path
	return final_path

# Asycnhronous function that analyses the information of an app and returns if it is explicit or not
@postpone
def get_data_async(page, url_async, cache_reload, md5_or_id):
	illust2vec = Model._model
	exp = False

	# Loads the configuration file
	p = os.path.abspath(os.path.join("../", os.pardir))

	with open(p+"/config.json") as json_data:
		config = json.load(json_data)

	# If web is set, the script will try to parse the iamges from the web services
	if config['directories']['local_or_web_images']=='web':
			Model._local = False

	print "Fetching data..."
	title = page['meta']['title']

	app_id = page['apk']['id']

	md5 = page['apk']['md5sum']

	description = page['meta']['description']

	categories = []

	for cat in page['meta']['categories']['standard']:
		categories.append(cat['name'])

	for cat in page['meta']['categories']['custom']:
		categories.append(cat['name'])

	scr = []
	scr_hd = []
	
	if 'sshots' in page['media']:
		for s in page['media']['sshots']:
			if Model._local:
				scr.append(local_url(config['directories']['local_image_path_prefix'],s))
			else:
				try:
					scr.append(s['path'])
				except:
					scr.append(s)

	if 'sshots_hd' in page['media']:
		for s in page['media']['sshots_hd']:
			if Model._local:
				scr.append(local_url(config['directories']['local_image_path_prefix'],s))
			else:
				try:				
					scr_hd.append(s['path'])
				except:
					scr_hd.append(s)

	min_age = page['meta']['min_age']

	icon = page['apk']['icon']

	if Model._local:
		icon = local_url(config['directories']['local_image_path_prefix'], icon)

	icon_hd = []
	if 'icon_hd' in page['apk']:
		icon_hd = page['apk']['icon_hd']
		if Model._local:
			icon_hd = local_url(config['directories']['local_image_path_prefix'],icon_hd)

	icons = []
	icons.append(icon)
	if icon_hd:
		icons.append(icon_hd)

	screenshots = scr+scr_hd
	size = len(description)
	print "Analysing app..."
	# Gets the percentage for safe and explicit content
	dist = analyse_app.analyse_app(page['apk']['id'], page['apk']['md5sum'], illust2vec, icons, screenshots, description,''.join(categories), min_age, size, title, cache_reload)
	try:
		if dist.prob('exp')>0.5:
			exp = True
	except:
		if dist>0.5:
			exp = True
	# Tries to open url_async/True or url_async/False to sinalize the end of script
	try:
		if md5_or_id=="md5":
			print "Opening "+str(url_async)+"md5sum="+md5+"/mature="+str(exp)
			return urllib2.urlopen(str(url_async)+"md5sum="+md5+"/mature="+str(exp))
		else:
			print "Opening "+str(url_async)+"id="+str(app_id)+"/mature="+str(exp)
			return urllib2.urlopen(str(url_async)+"id="+str(app_id)+"/mature="+str(exp))
	except:
		print "Could not open the webpage"

# Synchronous function that analyses the information of an app and returns if it is explicit or not
def get_data_sync(page, cache_reload):
	illust2vec = Model._model
	exp = False

	# Loads the configuration file
	p = os.path.abspath(os.path.join("../", os.pardir))

	with open(p+"/config.json") as json_data:
		config = json.load(json_data)

	# If web is set, the script will try to parse the iamges from the web services
	if config['directories']['local_or_web_images']=='web':
			Model._local = False


	print "Fetching data..."
	title = page['meta']['title']

	app_id = page['apk']['id']

	description = page['meta']['description']

	categories = []


	for cat in page['meta']['categories']['standard']:
		categories.append(cat['name'])

	for cat in page['meta']['categories']['custom']:
		categories.append(cat['name'])

	scr = []
	scr_hd = []
	
	if 'sshots' in page['media']:
		for s in page['media']['sshots']:
			if Model._local:
				scr.append(local_url(config['directories']['local_image_path_prefix'],s))
			else:
				try:
					scr.append(s['path'])
				except:
					scr.append(s)

	if 'sshots_hd' in page['media']:
		for s in page['media']['sshots_hd']:
			if Model._local:
				scr.append(local_url(config['directories']['local_image_path_prefix'],s))
			else:
				try:				
					scr_hd.append(s['path'])
				except:
					scr_hd.append(s)

	min_age = page['meta']['min_age']

	icon = page['apk']['icon']

	if Model._local:
		icon = local_url(config['directories']['local_image_path_prefix'], icon)

	icon_hd = []
	if 'icon_hd' in page['apk']:
		icon_hd = page['apk']['icon_hd']
		if Model._local:
			icon_hd = local_url(config['directories']['local_image_path_prefix'],icon_hd)

	icons = []
	icons.append(icon)
	if icon_hd:
		icons.append(icon_hd)

	screenshots = scr+scr_hd
	size = len(description)
	print "Analysing app..."
	# Gets the percentage for safe and explicit content
	dist = analyse_app.analyse_app(page['apk']['id'], page['apk']['md5sum'], illust2vec, icons, screenshots, description,''.join(categories), min_age, size, title, cache_reload)
	try:
		if dist.prob('exp')>0.5:
			exp = True
	except:
		if dist>0.5:
			exp = True
	print "Done"
	return exp



# View for get by id
# For more detailed error logs comment the try... except and indentate correctly its content

def getbyId(request, app_id, cache_reload=0):

	# If cache relaod is 1, it will force the content to be rewritten in the cache
	if not cache_reload:
		cache_reload=0
	now = datetime.now()
	url = "http://webservices.aptoide.com/webservices/3/getApkInfo/id:"
	
	# Loads the configurations from a config file
	p = os.path.abspath(os.path.join("../", os.pardir))
	with open(p+"/config.json") as json_data:
		config = json.load(json_data)
	exp = False
	app_md5=""
	try:
		# Fetching the JSON content
		webpage = urllib2.urlopen(url+str(app_id)+"/json")
		soup = BeautifulSoup(webpage, "lxml")
								
		text = soup.get_text()
		page = json.loads(text)
		if page['status']!='FAIL':
			app_md5 = page['apk']['md5sum']
			# Check if is asynchronous or synchronous
			if config["synchronous_or_asynchronous"]=="asynchronous":
				# If cache_reload = 0, check cache
				if cache_reload==0:
					db = sqlite3.connect(config['directories']['final_database'])
					c = db.cursor()
					c.execute(''' SELECT ID FROM app WHERE app_md5=? ''',(app_md5,))
					res = c.fetchone()
					if res:
						# If we have the result, return it
						c.execute(''' SELECT is_mature FROM final_results WHERE for_id=? ''',(res[0],))
						res2 = c.fetchone()
						if res2:
							db.close()
							res=""
							if res2[0]>0.5:
								res="yes"
							else:
								res="no"
							return HttpResponse(json.dumps({'app_md5': app_md5,'app_id': int(app_id), 'status': 'OK','mature_content': res, 'time':str(datetime.now()-now)}, sort_keys=True), content_type='application/json')

				get_data_async(page, config["directories"]["asynchronous_dir"], cache_reload, "id")
				return HttpResponse(json.dumps({'app_md5': app_md5,'app_id': int(app_id), 'status': 'request_submitted','mature_content': '', 'time':str(datetime.now()-now)}, sort_keys=True), content_type='application/json')
			exp = get_data_sync(page, int(cache_reload))

		else:
			status = 'Failed'
			print "App does not exist"
			return HttpResponse(json.dumps({'app_md5': app_md5,'app_id': int(app_id),'status': 'Failed', 'mature_content': '', 'time':str(datetime.now()-now)}, sort_keys=True), content_type='application/json')
	except:
		status = 'Failed'
		print "Error during parsing"
		return HttpResponse(json.dumps({'app_md5': app_md5,'app_id': int(app_id),'status': 'Failed', 'mature_content': '', 'time':str(datetime.now()-now)}, sort_keys=True), content_type='application/json')

	# If it's explicit content, redirects to true page. Otherwise, redirects to false page.
	if exp:
		return HttpResponse(json.dumps({'app_md5': app_md5,'app_id': int(app_id), 'status': 'OK','mature_content': 'yes', 'time':str(datetime.now()-now)}, sort_keys=True), content_type='application/json')
	return HttpResponse(json.dumps({'app_md5': app_md5,'app_id': int(app_id), 'status': 'OK','mature_content': 'no', 'time':str(datetime.now()-now)}, sort_keys=True), content_type='application/json')



# View for get by md5
# For more detailed error logs comment the try... except and indentate correctly its content
def getbyMD5(request, app_md5, cache_reload=0):
	
	# If cache relaod is 1, it will force the content to be rewritten in the cache
	if not cache_reload:
		cache_reload=0
	now = datetime.now()
	url = "http://webservices.aptoide.com/webservices/3/getApkInfo/md5sum:"
	# Loads the configurations from a config file
	p = os.path.abspath(os.path.join("../", os.pardir))
	with open(p+"/config.json") as json_data:
		config = json.load(json_data)

	app_id = 0
	exp = False
	try:
		# Fetching the JSON content
		webpage = urllib2.urlopen(url+str(app_md5)+"/json")
		soup = BeautifulSoup(webpage, "lxml")
				
		text = soup.get_text()
		page = json.loads(text)
		if page['status']!='FAIL':
			app_id = page['apk']['id']
			# Check if is asynchronous or synchronous
			if config["synchronous_or_asynchronous"]=="asynchronous":
				# If cache_reload = 0, check cache
				if cache_reload==0:
					db = sqlite3.connect(config['directories']['final_database'])
					c = db.cursor()
					c.execute(''' SELECT ID FROM app WHERE app_md5=? ''',(app_md5,))
					res = c.fetchone()
					if res:
						# If we have the result, return it
						c.execute(''' SELECT is_mature FROM final_results WHERE for_id=? ''',(res[0],))
						res2 = c.fetchone()
						if res2:
							db.close()
							res=""
							if res2[0]>0.5:
								res="yes"
							else:
								res="no"
							return HttpResponse(json.dumps({'app_md5': app_md5,'app_id': int(app_id), 'status': 'OK','mature_content': res, 'time':str(datetime.now()-now)}, sort_keys=True), content_type='application/json')

				get_data_async(page, config["directories"]["asynchronous_dir"], cache_reload, "md5")
				return HttpResponse(json.dumps({'app_md5': app_md5,'app_id': int(app_id), 'status': 'request_submitted','mature_content': '', 'time':str(datetime.now()-now)}, sort_keys=True), content_type='application/json')
			exp = get_data_sync(page, int(cache_reload))

		else:
			status = 'Failed'
			print "App does not exist"
			return HttpResponse(json.dumps({'app_md5': app_md5,'app_id': app_id,'status': 'Failed', 'mature_content': '', 'time':str(datetime.now()-now)}, sort_keys=True), content_type='application/json')
	except:
		status = 'Failed'
		print "Error during parsing"
		return HttpResponse(json.dumps({'app_md5': app_md5,'app_id': app_id,'status': 'Failed', 'mature_content': '', 'time':str(datetime.now()-now)}, sort_keys=True), content_type='application/json')

	# If it's explicit content, redirects to true page. Otherwise, redirects to false page.
	if exp:
		return HttpResponse(json.dumps({'app_md5': app_md5,'app_id': app_id, 'status': 'OK','mature_content': 'yes', 'time':str(datetime.now()-now)}, sort_keys=True), content_type='application/json')
	return HttpResponse(json.dumps({'app_md5': app_md5,'app_id': app_id, 'status': 'OK','mature_content': 'no', 'time':str(datetime.now()-now)}, sort_keys=True), content_type='application/json')

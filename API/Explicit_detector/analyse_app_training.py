# Diogo Daniel Soares Ferreira
# diogodanielsoaresferreira@ua.pt
# Aptoide, 2016

# Full training to analyse the explicitness of an app

from __future__ import division
import i2v
import pickle
import os
import sqlite3
import collections
import glob
import pickle
from Illustration2Vector.illustration2vec_master.analyse_image import analyse_explicit
from Text_categorization.Text_categorization import text_cat
import random
import nltk
from datetime import datetime, time
from nltk.metrics import precision, recall, f_measure
from sklearn.naive_bayes import MultinomialNB, BernoulliNB
from sklearn.linear_model import LogisticRegression, SGDClassifier
from nltk.classify.scikitlearn import SklearnClassifier
from sklearn.svm import SVC, LinearSVC, NuSVC
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn import tree



def analyse_app_train(illust2vec, app_info):
	
	def find_features(icon_list, scr_list, description_result):
		features = {}
		maximum = 0
		flag = 0
		safe = 0

		# Find maximum percentage of explicitness and its safetiness percentage.

		if len(icon_list)==0:
			maximum = 0.5
			safe = 0.5
		else:
			for icon in icon_list:
				for data in icon:
					if data[0]=='explicit' and data[1]>maximum:
						maximum = data[1]
						flag = 1
					if data[0]=='safe' and flag==1:
						safe = data[1]
						flag = 0
		maximum_s = 0
		flag = 0
		safe_s = 0

		if len(scr_list)==0:
			maximum_s = 0.5
			safe_s = 0.5
		else:
			for scr in scr_list:
				for data in scr:
					if data[0]=='explicit' and data[1]>maximum_s:
						maximum_s = data[1]
						flag = 1
					if data[0]=='safe' and flag==1:
						safe_s = data[1]
						flag = 0

		features['ic_exp'] = maximum
		features['ic_non'] = safe
		features['sc_exp'] = maximum_s
		features['sc_non'] = safe_s
		features['desc_exp'] = description_result.prob('exp')
		return features

	featuresets = []
	# Tries to load featuresets from file
	try:
		f = open("./featuresets.pickle", "rb")
		featuresets = pickle.load(f)
		f.close()
		print "Open FeatureSets Pickle"
	except IOError:
		# It can take toooo much time (4000 apps database, +- 8 hours)
		print "Did not Find FeatureSets Pickle"
		num=0
		# Building the featureset
		for info in app_info:
			icons_l = []
			screens = []
			for icon in info[0]:
				try:
					icons_l.append(analyse_explicit(illust2vec, icon))
				except:
					print "Could not resize image"

			for scr in info[1]:
				try:
					screens.append(analyse_explicit(illust2vec, scr))
				except:
					print "Could not resize image"

			desc = text_cat(info[2], len(info[2]), info[3],info[4])
			num+=1
			if (num%100)==0:
				print num
			features = find_features(icons_l, screens, desc)
			featuresets.append((features, info[5]))

		random.shuffle(featuresets)
		save_model = open("./featuresets.pickle", "wb")
		pickle.dump(featuresets, save_model)
		save_model.close()
	
	
	training_set = featuresets[:]
	
	# Training the model and serializing it to be used by the API
	classifier = SklearnClassifier(SVC(probability=True))
	saving_model = classifier.train(training_set)
	save_model = open("./model_apps_info.pickle", "wb")
	pickle.dump(saving_model, save_model)
	save_model.close()


if __name__=='__main__':

	try:
		# Tries to load the illustration2vec model
		illust2vec_f = open("Illustration2Vector/illustration2vec_master/illust2vec.pickle", "rb")
		illust2vec = pickle.load(illust2vec_f)
		illust2vec_f.close()
	except IOError:
		illust2vec = i2v.make_i2v_with_chainer(
	    "Illustration2Vector/illustration2vec-master/illust2vec_tag_ver200.caffemodel", "Illustration2Vector/illustration2vec-master/tag_list.json")
		save_model = open("Illustration2Vector/illustration2vec_master/illust2vec.pickle", "wb")
		pickle.dump(illust2vec, save_model)
		save_model.close()

	icons = []
	screenshots = []
	description = ""
	# Gets all the content from database
	db = sqlite3.connect('./API to download database/app_info_big.db')
	c = db.cursor()

	explicit_content = []
	non_explicit_content = []
	exp_size = 0
	non_size = 0


	c.execute(''' SELECT title,id,description, category, age FROM app_data WHERE mature=1''')

	for d in c.fetchall():
		explicit_content.append(d)
		exp_size += 1


	c.execute(''' SELECT title,id,description, category, age FROM app_data WHERE mature=0''')

	for d in c.fetchall():
		non_explicit_content.append(d)
		non_size += 1

	db.close()

	print "Non-Explicit Size: "+str(non_size)
	print "Explicit Size: "+str(exp_size)

	# Get images from an app id
	def get_images_list(id_int):

		icons = []
		scr = []

		os.chdir("./API to download database/Big_Database/images/screenshot")
		types = [".jpg", ".png"]
		for type_image in types:
			for image in glob.glob(str(id_int)+"*"+type_image):
			    scr.append("./API to download database/Big_Database/images/screenshot/"+image)

		os.chdir("../icon")
		types = [".jpg", ".png"]
		for type_image in types:
			for image in glob.glob(str(id_int)+"*"+type_image):
				icons.append("./API to download database/Big_Database/images/icon/"+image)
		os.chdir("../../../..")

		return icons, scr

	app_info = []

	for d in explicit_content:
		icons, screenshots = get_images_list(d[1])
		description = d[2]
		cat = d[3]
		age = d[4]
		app_info.append((icons, screenshots, description,cat,age,'exp'))

	for d in non_explicit_content:
		icons, screenshots = get_images_list(d[1])
		description = d[2]
		cat = d[3]
		age = d[4]
		app_info.append((icons, screenshots, description, cat, age,'non'))

	analyse_app_train(illust2vec, app_info)


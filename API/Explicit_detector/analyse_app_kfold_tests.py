# Diogo Daniel Soares Ferreira
# diogodanielsoaresferreira@ua.pt
# Aptoide, 2016

# Testing to analyse the percentage of explicitness of an app with k-fold tests

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
from sklearn.linear_model import LogisticRegression, SGDClassifier, Ridge, Lasso, ElasticNet, SGDRegressor
from nltk.classify.scikitlearn import SklearnClassifier
from sklearn.svm import SVC, LinearSVC, NuSVC
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier, ExtraTreesClassifier
from sklearn import tree

# Parameter k of k-fold tests
k=5

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

	# Divide explicit and non_explicit features
	explicit_feat = [feature for feature in featuresets if feature[1]=='exp']
	non_explicit_feat = [feature for feature in featuresets if feature[1]=='non']


	i=0
	while i<k:

		# Creating testing and training set
		testing_set = explicit_feat[int((i*len(explicit_feat)/k)):int(((i+1)*len(explicit_feat)/k))]+non_explicit_feat[int((i*len(non_explicit_feat)/k)):int(((i+1)*len(non_explicit_feat)/k))]
		training_set = [x for j,x in enumerate(explicit_feat) if j<(i*len(explicit_feat)/k) or j>((i+1)*len(explicit_feat)/k)]
		training_set += [x for j,x in enumerate(non_explicit_feat) if j<(i*len(non_explicit_feat)/k) or j>((i+1)*len(non_explicit_feat)/k)]
		random.shuffle(training_set)
		random.shuffle(testing_set)

		def results(classifier, testing_set, training_set):
			now = datetime.now()
			# Training the classifier
			classifier = classifier.train(training_set)
			refsets = collections.defaultdict(set)
			testsets = collections.defaultdict(set)

			tp=0
			fp=0
			tn=0
			fn=0
			# Gets the true/false positives/negatives
			for i, (features, label) in enumerate(testing_set):
				refsets[label].add(i)
				observed = classifier.classify(features)
				testsets[observed].add(i)
				if label =='exp' and observed =='exp':
					tp += 1
				elif label=='non' and observed=='non':
					tn += 1
				elif label=='exp' and observed=='non':
					fn += 1
				else:
					fp += 1

			print "Time training: " + str(datetime.now()-now)
			print "True Positives: " + str(tp)
			print "False Positives: " + str(fp)
			print "True Negatives: " + str(tn)
			print "False Negatives: " + str(fn)
			print 'Explicit Precision: ', precision(refsets['exp'], testsets['exp'])
			print 'Explicit recall: ', recall(refsets['exp'], testsets['exp'])
			print 'Explicit F-Score: ', f_measure(refsets['exp'], testsets['exp'])
			print 'Non-Explicit Precision: ', precision(refsets['non'], testsets['non'])
			print 'Non-Explicit Recall: ', recall(refsets['non'], testsets['non'])
			print 'Non-Explicit F-Score: ', f_measure(refsets['non'], testsets['non'])

			print "Accuracy percent: ", (nltk.classify.accuracy(classifier, testing_set))*100
			return classifier


		try:
			print "\n****** SGD CLASSIFIER ************"
			results(SklearnClassifier(SGDClassifier()), testing_set, training_set)
		except:
			pass
		try:
			print "\n****** ADA BOOST ************"
			results(SklearnClassifier(AdaBoostClassifier()), testing_set, training_set)
		except:
			pass
		try:
			print "\n****** LOGISTIC REGRESSION ************"
			saving_model = results(SklearnClassifier(LogisticRegression()), testing_set, training_set)
		except:
			pass
		try:
			print "\n****** SVC ************"
			results(SklearnClassifier(SVC()), testing_set, training_set)
		except:
			pass
		try:
			print "\n****** LINEAR SVC ************"
			results(SklearnClassifier(LinearSVC()), testing_set, training_set)
		except:
			pass
		
		i+=1


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
	print "Appending all images..."
	now = datetime.now()
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
	print str(datetime.now()-now)
	analyse_app_train(illust2vec, app_info)


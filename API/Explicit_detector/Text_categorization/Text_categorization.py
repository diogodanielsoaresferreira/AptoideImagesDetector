# Diogo Daniel Soares Ferreira
# diogodanielsoaresferreira@ua.pt
# Aptoide, 2016

# Text categorization simple API


from __future__ import division
import sqlite3
import os
from nltk.tokenize import word_tokenize
import nltk
import random
import pickle
import os
import collections
from nltk.metrics import precision, recall, f_measure
from sklearn.naive_bayes import MultinomialNB, BernoulliNB
from sklearn.linear_model import LogisticRegression, SGDClassifier
from nltk.classify.scikitlearn import SklearnClassifier
from sklearn.svm import SVC, LinearSVC, NuSVC
from nltk.classify import ClassifierI
from nltk.corpus import stopwords
from nltk.stem.porter import *
from nltk.util import ngrams
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn import tree
import string
from datetime import datetime, time


def text_cat(description, size, cat, age):
	classifier = ""
	words = []
	word_features = []
	

	try:
		# Loads the model and the features
		filename, file_extension = os.path.splitext(os.path.realpath(__file__))
		fn = os.path.dirname(os.path.abspath(os.path.join(filename, os.pardir)))
		
		f = open(fn+"/Text_categorization/model_info.pickle", "rb")
		classifier = pickle.load(f)
		f.close()

		f = open(fn+"/Text_categorization/word_features.pickle", "rb")
		word_features = pickle.load(f)
		f.close()
	except:
		print "Serialized objects not found"
		exit(0)
	stemmer = PorterStemmer()
	punctuations = list(string.punctuation)
	punctuations.append("''")
	punctuations.append("--")

	def find_features(document, size, cat, age):
		words = word_tokenize(document)
		words = [stemmer.stem(w.lower()) for w in words if not w in stopwords.words('english') and w not in punctuations]
		
		# Features:
		# Title: Not Included
		# Size of description: Not Included
		# Category: Included
		# Description: Included
		# Age : Not Included (It can overfit the model)
		
		features = {}
		for w in word_features:
			features[w] = (w in words)
		#features["size"] = size
		features["category"] = cat
		#features["age"] = age

		return features

	d = find_features(description, size, cat, age)
	#print d
	return classifier.prob_classify(d)

if __name__=="__main__":
	dist = text_cat("blonde", 20 ,"ApplicationsEntertainment", 18)
	print dist.prob('exp')
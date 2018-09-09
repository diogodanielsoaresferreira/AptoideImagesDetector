#!/usr/bin/python
# -*- coding: utf-8 -*-

# Diogo Daniel Soares Ferreira
# diogodanielsoaresferreira@ua.pt
# Aptoide, 2016

# Full training and saving of the model


from __future__ import division
import sqlite3
from nltk.tokenize import word_tokenize
import nltk
import os
import pickle
import random
import collections
from nltk.metrics import precision, recall, f_measure
from sklearn.naive_bayes import MultinomialNB, BernoulliNB
from sklearn.linear_model import LogisticRegression, SGDClassifier, Ridge, Lasso, ElasticNet, SGDRegressor
from nltk.classify.scikitlearn import SklearnClassifier
from sklearn.svm import SVC, LinearSVC, NuSVC
from nltk.classify import ClassifierI
from nltk.corpus import stopwords
from nltk.stem.porter import *
from nltk.util import ngrams
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier, ExtraTreesClassifier
from sklearn import tree
from statistics import mode
import string
from datetime import datetime, time

# Number of most common words used for classifier
n_common_words = 10000

# Stemmer to all words
stemmer = PorterStemmer()

punctuations = list(string.punctuation)
punctuations.append("''")
punctuations.append("--")

# Get the Content and label it
db = sqlite3.connect('../API to download database/app_info_big.db')
c = db.cursor()

explicit_content = []
non_explicit_content = []
documents = []
exp_size = 0
non_size = 0


c.execute(''' SELECT title,description,category,age FROM app_data WHERE mature=1''')

for d in c.fetchall():
	explicit_content.append(d[1])
	documents.append((d[1],len(d[1]),d[2],d[3],'exp'))
	exp_size += 1


c.execute(''' SELECT title,description,category,age FROM app_data WHERE mature=0''')

for d in c.fetchall():
	non_explicit_content.append(d[1])
	documents.append((d[1],len(d[1]),d[2],d[3],'non'))
	non_size += 1


	
print "Explicit descriptions: "+str(exp_size)
print "Non-Explicit descriptions: "+str(non_size)

db.close()

print "Pre-Processing..."

# Tokenize words
print "Tokenizing..."
now = datetime.now()
explicit_content_words = [word_tokenize(w) for w in explicit_content]
non_explicit_content_words = [word_tokenize(w) for w in non_explicit_content]
print str(datetime.now()-now)

# Append all words (lower)

all_words = []
print "Appending all words..."
now = datetime.now()
for w in explicit_content_words:
	for x in w:
		if x not in stopwords.words('english') and x not in punctuations:
			all_words.append(stemmer.stem(x.lower()))

for w in non_explicit_content_words:
	for x in w:
		if x not in stopwords.words('english') and x not in punctuations:
			all_words.append(stemmer.stem(x.lower()))
print str(datetime.now()-now)

print "Creating a frequency distribution..."
now = datetime.now()

# Get FreqDist
all_words = nltk.FreqDist(all_words)
print str(datetime.now()-now)
#print all_words.most_common(25)

print "Get the n most common features..."
now = datetime.now()
# Get n common words as features
word_features = list(all_words.keys())[:n_common_words]
#print word_features

# Check if it finds features in words
def find_features(document, size, cat, age):

	words = word_tokenize(document)
	words = [stemmer.stem(w.lower()) for w in words if not w in stopwords.words('english') and w not in punctuations]
	
	# Features:
	# Title: Not Included
	# Size of description: Not Included
	# Category: Included
	# Description: Included
	# Age: Not Included (can overfit the model)

	
	features = {}
	for w in word_features:
		features[w] = (w in words)
	#features["size"] = size
	features["category"] = cat
	#features["age"] = age

	return features

print str(datetime.now()-now)

print "Create a feature set..."
now = datetime.now()

featuresets = [(find_features(desc, size, cat, age), category) for (desc, size, cat, age, category) in documents]

random.shuffle(featuresets)


training_set = featuresets[:]

classifier = SklearnClassifier(LogisticRegression(penalty='l1',C=1))
saving_model = classifier.train(training_set)
save_model = open("./model_info.pickle", "wb")
pickle.dump(saving_model, save_model)
save_model.close()

save_model = open("./word_features.pickle", "wb")
pickle.dump(word_features, save_model)
save_model.close()
#!/usr/bin/python
# -*- coding: utf-8 -*-

# Diogo Daniel Soares Ferreira
# diogodanielsoaresferreira@ua.pt
# Aptoide, 2016

# Test for classifiers with one training set and one testing set.


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



# Step 0: Define parameters

# Length of test set
number_testing = 500

# Number of most common words used for classifier
n_common_words = 10000

# Number of most informative features
#n_most_informative_features = 25

# Stemmer to all words
stemmer = PorterStemmer()

punctuations = list(string.punctuation)
punctuations.append("''")
punctuations.append("--")

# Step 1: Get the Content and label it
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

# Step 2: Tokenize words
print "Tokenizing..."
now = datetime.now()
explicit_content_words = [word_tokenize(w) for w in explicit_content]
non_explicit_content_words = [word_tokenize(w) for w in non_explicit_content]
print str(datetime.now()-now)

# Step 3: Append all words (lower)

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

# Step 4: Get FreqDist
all_words = nltk.FreqDist(all_words)
print str(datetime.now()-now)
#print all_words.most_common(25)

print "Get the n most common features..."
now = datetime.now()
# Step 5: Get n common words as features
word_features = list(all_words.keys())[:n_common_words]
#print word_features

# Step 6: Check if it finds features in words
def find_features(document, size, cat, age):

	words = word_tokenize(document)
	words = [stemmer.stem(w.lower()) for w in words if not w in stopwords.words('english') and w not in punctuations]
	
	# Features:
	# Title: Not Included
	# Size of description: Not Included
	# Category: Included
	# Description: Included
	# Minimum age: Not Included (Overfitts the model)
	
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
# Step 7: Get feature set
featuresets = [(find_features(desc, size, cat, age), category) for (desc, size, cat, age, category) in documents]

# Step 8: Shuffle feature sets
random.shuffle(featuresets)


# Step 9: Create training set and testing set from feature sets
training_set = featuresets[:exp_size+non_size-number_testing]
#print training_set
testing_set = featuresets[exp_size+non_size-number_testing:]
#print testing_set
print str(datetime.now()-now)


# Step 10: With different classifiers, print Classification and other metrics.
print "Training..."


def results(classifier, testing_set, training_set):
	now = datetime.now()
	classifier = classifier.train(training_set)
	refsets = collections.defaultdict(set)
	testsets = collections.defaultdict(set)

	tp=0
	fp=0
	tn=0
	fn=0

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
	print "\n****** LOGISTIC REGRESSION ************"
	saving_model = results(SklearnClassifier(LogisticRegression(penalty='l1',C=1)), testing_set, training_set)
except:
	pass
'''
try:
	print "\n****** NU SVC ************"
	saving_model=results(SklearnClassifier(NuSVC(nu=0.1, kernel='rbf')), testing_set, training_set)
except:
	pass

try:
	print "\n****** Random Forest ************"
	results(SklearnClassifier(RandomForestClassifier()), testing_set, training_set)
except:
	pass
try:
	print "\n****** ADA BOOST ************"
	results(SklearnClassifier(AdaBoostClassifier()), testing_set, training_set)
except:
	pass


try:
	print "\n****** LINEAR SVC ************"
	results(SklearnClassifier(LinearSVC()), testing_set, training_set)
except:
	pass

try:
	print "\n****** Extra Trees ************"
	results(SklearnClassifier(ExtraTreesClassifier()), testing_set, training_set)
except:
	pass

try:
	print "\n****** NAIVE BAYES ************"
	results(nltk.NaiveBayesClassifier, testing_set, training_set)
except:
	pass

try:
	print "\n****** MULTINOMIAL ************"
	results(SklearnClassifier(MultinomialNB()), testing_set, training_set)
except:
	pass
try:
	print "\n****** DECISION TREE ************"
	results(SklearnClassifier(tree.DecisionTreeClassifier()), testing_set, training_set)
except:
	pass
try:
	print "\n****** BERNOULLI ************"
	results(SklearnClassifier(BernoulliNB()), testing_set, training_set)
except:
	pass

try:
	print "\n****** SGD CLASSIFIER ************"
	results(SklearnClassifier(SGDClassifier()), testing_set, training_set)
except:
	pass
try:
	print "\n****** SVC ************"
	results(SklearnClassifier(SVC()), testing_set, training_set)
except:
	pass

try:
	print "\n****** RIDGE ************"
	results(SklearnClassifier(Ridge()), testing_set, training_set)
except:
	pass
try:
	print "\n****** LASSO ************"
	results(SklearnClassifier(Lasso()), testing_set, training_set)
except:
	pass
try:
	print "\n****** ELASTIC NET **********"
	results(SklearnClassifier(ElasticNet()), testing_set, training_set)
except:
	pass

try:
	print "\n****** SGD Regressor ************"
	results(SklearnClassifier(SGDRegressor()), testing_set, training_set)
except:
	pass
'''
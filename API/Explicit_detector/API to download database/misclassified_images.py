# Diogo Daniel Soares Ferreira
# diogodanielsoaresferreira@ua.pt
# Aptoide, 2016

# This script gets the percentage of misclassified (explicit/non-explicit) images on a database.


from __future__ import division
import os
import glob
import sqlite3

def is_explicit(id_int):

	types = [".jpg", ".png"]

	os.chdir("./Big_Database/images/icons_explicit")
	
	for type_image in types:
		for image in glob.glob(str(id_int)+"*"+type_image):
		    os.chdir("../../..")
		    return True
	

	os.chdir("../screenshot_explicit")
	for type_image in types:
		for image in glob.glob(str(id_int)+"*"+type_image):
		    os.chdir("../../..")
		    return True

	os.chdir("../../..")

	return False


db = sqlite3.connect('app_info_big.db')

c = db.cursor()

tp=0
fp=0
tn=0
fn=0


c.execute(''' SELECT id FROM app_data WHERE mature=1''')

for d in c.fetchall():
	if is_explicit(d[0]):
		tp+=1
	else:
		fn+=1

c.execute(''' SELECT id FROM app_data WHERE mature=0''')

for d in c.fetchall():
	if is_explicit(d[0]):
		fp+=1
	else:
		tn+=1



db.close()

pr = tp/(tp+fp)
rec = tp/(tp+fn)
fsc = 2*(pr*rec)/(pr+rec)
acc = ((tp+tn)/(fp+fn+tn+tp))*100

print "True Positives: "+str(tp)
print "False Positives: "+str(fp)
print "True Negatives: "+str(tn)
print "False Negatives: "+str(fn)
print "Precision: "+str(pr)
print "Recall: "+str(rec)
print "F-Score: "+str(fsc)
print "Accuracy Percent: "+str(acc)


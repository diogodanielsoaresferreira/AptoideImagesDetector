# Diogo Daniel Soares Ferreira
# diogodanielsoaresferreira@ua.pt
# Aptoide, 2016
# This script gets the percentage of misclassified (explicit/non-explicit) text information on a database.

from __future__ import division
import sqlite3

db = sqlite3.connect('app_info_big.db')

c = db.cursor()

tp=0
fp=0
tn=0
fn=0


c.execute(''' SELECT age FROM app_data WHERE mature=1''')

for d in c.fetchall():
	if d[0]==18:
		tp+=1
	else:
		fn+=1

c.execute(''' SELECT age FROM app_data WHERE mature=0''')

for d in c.fetchall():
	if d[0]==18:
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

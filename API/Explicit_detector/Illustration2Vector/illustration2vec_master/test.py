# Diogo Daniel Soares Ferreira
# diogodanielsoaresferreira@ua.pt
# Aptoide, 2016

# This script runs a test on all the images 
# and categorizes the images as false/true positive/negative. It also contains information about the time.

import i2v
from datetime import datetime, time
from PIL import Image
import os
import glob
import pickle


print "Loading Neural Network Model..."
now = datetime.now()

# Tries to load object with database.
# If it does not exist, creates one himself.

try:
	illust2vec_f = open("illust2vec.pickle", "rb")
	illust2vec = pickle.load(illust2vec_f)
	illust2vec_f.close()
except IOError:
	illust2vec = i2v.make_i2v_with_chainer(
    "illust2vec_tag_ver200.caffemodel", "tag_list.json")
	save_model = open("illust2vec.pickle", "wb")
	pickle.dump(illust2vec, save_model)
	save_model.close()

print "Time loading Neural Network Model: "+str(datetime.now()-now)

global_time = datetime.now()

# True/false positive/negative
fp = 0
fn = 0
tp = 0
tn = 0

types = ('*.png', '*.jpg')

# File to save the results.
f = open('test_results.txt','w')

for image_dir in ('../../API to download database/Big_Database/images/icons_explicit',
				'../../API to download database/Big_Database/images/icons_non-explicit'):
	for t in types:
		for image_file in glob.glob(os.path.join(image_dir,t)):
			
			print "Processing image..."+str(image_file)
			try:
				now = datetime.now()

				img = Image.open(image_file)
				list = illust2vec.estimate_specific_tags([img], ["explicit", "safe"])
				print "Time processing image: "+str(datetime.now()-now)
				f.write('\n')
				f.write('\n')
				f.write(image_file)
				f.write('\n')
				if(list[0]['explicit']>list[0]['safe']):
					print "explicit"
					f.write("explicit")
					if(image_dir=='../../API to download database/Big_Database/images/icons_non-explicit'):
						fp+=1
					else:
						tp+=1
				else:
					print "safe"
					f.write("safe")
					if(image_dir=='../../API to download database/Big_Database/images/icons_explicit'):
						fn+=1
					else:
						tn+=1
			except:
				print "Could not open image "+str(image_file)


print "Time processing all icons: "+str(datetime.now()-global_time)
print str(fp)+" false positives"
print str(fn)+" false negatives"
print str(tn)+" true negatives"
print str(tp)+" true positives"

for image_dir in ('../../API to download database/Big_Database/images/screenshot_explicit',
				'../../API to download database/Big_Database/images/screenshot_non-explicit'):
	for t in types:
		for image_file in glob.glob(os.path.join(image_dir,t)):
			
			print "Processing image..."+str(image_file)
			try:
				now = datetime.now()

				img = Image.open(image_file)
				list = illust2vec.estimate_specific_tags([img], ["explicit", "safe"])
				print "Time processing image: "+str(datetime.now()-now)
				f.write('\n')
				f.write('\n')
				f.write(image_file)
				f.write('\n')
				if(list[0]['explicit']>list[0]['safe']):
					print "explicit"
					f.write("explicit")
					if(image_dir=='../../API to download database/Big_Database/images/screenshot_non-explicit'):
						fp+=1
					else:
						tp+=1
				else:
					print "safe"
					f.write("safe")
					if(image_dir=='../../API to download database/Big_Database/images/screenshot_explicit'):
						fn+=1
					else:
						tn+=1
			except:
				print "Could not open image "+str(image_file)


print "Time processing all screenshots: "+str(datetime.now()-global_time)
print str(fp)+" false positives"
print str(fn)+" false negatives"
print str(tn)+" true negatives"
print str(tp)+" true positives"

f.close()

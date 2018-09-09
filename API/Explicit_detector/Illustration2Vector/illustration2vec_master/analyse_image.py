# Diogo Daniel Soares Ferreira
# diogodanielsoaresferreira@ua.pt
# Aptoide, 2016

# This script analyses a list of images, returning a tuple containing safe/explicit and its percentage.
# As argument passed in the command line sould be the name of all files wanted to analyse.
# For example, python analyse_image.py url_of_image

try:
	import Illustration2Vector.illustration2vec_master.i2v
except:
	import i2v
from PIL import Image
from datetime import datetime, time
import os
import glob
import sys
import pickle
import urllib, cStringIO



def analyse_explicit(illust2vec, image_dir):


	try:
		# Get image from file firectory
		img = Image.open(os.path.join(image_dir))
	except:
		try:
			# Get image from url
			print "Getting Images..."#+image_dir
			global_time = datetime.now()
			file = cStringIO.StringIO(urllib.urlopen(image_dir).read())
			img = Image.open(file)
			print "Time downloading the image: "+str(datetime.now()-global_time)
		except:
			print "Could not parse image" + image_dir
			return (('explicit',0.5), ('safe',0.5))

	print "Analysing images..."
	global_time = datetime.now()
	list = illust2vec.estimate_specific_tags([img], ["explicit", "safe"])
	print "Time analysing the image: "+str(datetime.now()-global_time)
    
	return (('explicit',list[0]['explicit']), ('safe',list[0]['safe']))

# Test

if __name__ == "__main__":
	
	print "Loading Neural Network Model..."
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


	for image_dir in sys.argv:
		if image_dir!=sys.argv[0]:
			print "Analysing image..."
			analyse_explicit(illust2vec, image_dir)
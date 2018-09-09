# Diogo Daniel Soares Ferreira
# diogodanielsoaresferreira@ua.pt
# Aptoide, 2016

# Main function to analyse the percentage of explicitness of an app
# Caches the result on a database

from __future__ import division
import json
import sqlite3
import os
import time
import i2v
import pickle
from Illustration2Vector.illustration2vec_master.analyse_image import analyse_explicit
from Text_categorization.Text_categorization import text_cat

# Returns the illustration2vector model

def get_model():
	illust2vec = []

	p = os.path.abspath(os.path.join("../", os.pardir))

	with open(p+"/config.json") as json_data:
		config = json.load(json_data)

	try:
		illust2vec_f = open(config['directories']['ill2vec_ser'], "rb")
		illust2vec = pickle.load(illust2vec_f)
		illust2vec_f.close()
	except IOError:
		illust2vec = i2v.make_i2v_with_chainer(config['directories']['ill2vec_model']
	    , config['directories']['ill2vec_tag_list'])
		save_model = open(config['directories']['ill2vec_ser'], "wb")
		pickle.dump(illust2vec, save_model)
		save_model.close()
	return illust2vec

def analyse_app(app_id, app_md5, illust2vec, icons, screenshots, description, category, age, size, title, cache_reload):

	# Loads configurations from file
	p = os.path.abspath(os.path.join("../", os.pardir))
	tb_id = 0
	with open(p+"/config.json") as json_data:
		config = json.load(json_data)

	# Connect to database
	db = sqlite3.connect(config['directories']['final_database'])
	c = db.cursor()

	# If id exists, app has already been processed.
	c.execute(''' SELECT ID FROM app WHERE app_md5=? ''',(app_md5,))
	res = c.fetchone()

	if res:
		# If is not needed to reload the cache, tries to return the result
		if cache_reload==0:
			c.execute(''' SELECT is_mature FROM final_results WHERE for_id=? ''',(res[0],))
			res2 = c.fetchone()
			if res2:
				db.close()
				return res2[0]
			else:
				tb_id = res[0]
		else:
			tb_id = res[0]
	else:
		c.execute(''' INSERT INTO app(app_md5) VALUES (?) ''',(app_md5,))
		db.commit()
		c.execute(''' SELECT ID FROM app WHERE app_md5=? ''',(app_md5,))
		tb_id = c.fetchone()[0]

	# Tries to load the model for text categorization
	try:
		f = open(config['directories']['text_cat_model'], "rb")
		classifier = pickle.load(f)
		f.close()
	except:
		print "Serialized objects not found"
		exit(0)

	icon_l = []
	screens = []
	for icon in icons:

		# Check if has already been analysed.
		c.execute(''' SELECT image_exp, image_safe FROM image_results WHERE url=?''',(icon,))
		res = c.fetchone()
		
		# If is not needed to reload the cache, tries to return the result saved
		if cache_reload==0:
			if res:
				icon_l.append((('explicit',res[0]), ('safe',res[1])))
			# If there were no previous results, inserts new results
			else:
				res = analyse_explicit(illust2vec, icon)
				exp = False
				if res[0][1]>res[1][1]:
					exp = True
				c.execute(''' INSERT INTO image_results VALUES (?,?,?,?,?,?,?) ''',(int(tb_id), icon, res[0][1], res[1][1], exp, -1,  "icon",))
				db.commit()
				icon_l.append(res)
		else:
			res = analyse_explicit(illust2vec, icon)
			exp = False
			if res[0][1]>res[1][1]:
				exp = True

			# If the image already exists, it is needed to update the result
			if res:
				c.execute(''' UPDATE image_results SET for_id=?, image_exp=?, image_safe=?, is_mature=?, external_validator=?, icon_or_screenshot=? WHERE url=? ''', (int(tb_id), res[0][1], res[1][1], exp, -1, "icon", icon,))
				db.commit()
			# If the image does not exist, insert new result
			else:
				c.execute(''' INSERT INTO image_results VALUES (?,?,?,?,?,?,?) ''',(int(tb_id), icon, res[0][1], res[1][1], exp, -1,  "icon",))
				db.commit()

			icon_l.append(res)

	for scr in screenshots:
		# Check if has already been analysed.
		c.execute(''' SELECT image_exp, image_safe FROM image_results WHERE url=?''',(scr,))
		res = c.fetchone()
		# If is not needed to reload the cache, tries to return the result saved
		if cache_reload==0:
			if res:
				screens.append((('explicit',res[0]), ('safe',res[1])))
			# If there were no previous results, inserts new results
			else:
				res = analyse_explicit(illust2vec, scr)
				exp = False
				if res[0][1]>res[1][1]:
					exp = True
				c.execute(''' INSERT INTO image_results VALUES (?,?,?,?,?,?,?) ''',(int(tb_id), scr, res[0][1], res[1][1], exp, -1,  "screenshot",))
				db.commit()
				screens.append(res)
		else:
			res = analyse_explicit(illust2vec, icon)
			exp = False
			if res[0][1]>res[1][1]:
				exp = True

			# If the image already exists, it is needed to update the result
			if res:
				c.execute(''' UPDATE image_results SET for_id=?, image_exp=?, image_safe=?, is_mature=?, external_validator=?, icon_or_screenshot=? WHERE url=? ''', (int(tb_id), res[0][1], res[1][1], exp, -1, "icon", icon,))
				db.commit()
			# If the image does not exist, insert new result
			else:
				c.execute(''' INSERT INTO image_results VALUES (?,?,?,?,?,?,?) ''',(int(tb_id), icon, res[0][1], res[1][1], exp, -1,  "icon",))
				db.commit()

			icon_l.append(res)

	# Check if has already been analysed.
	c.execute(''' SELECT text_exp FROM text_results WHERE for_id=? ''',(int(tb_id),))
	res = c.fetchone()
	
	# If it was already analysed and it is not needed to reload the cache, just get the result
	if res and cache_reload==0:
		description = res[0]
	
	# If exists a result and cache_reload==1, update the cache
	elif res:
		exp = False
		description = text_cat(description, size, category, age)
		if description.prob('exp')>0.5:
			exp = True
		c.execute(''' UPDATE text_results SET text_exp=?, is_mature=?, external_validator=? WHERE for_id=? ''',(description.prob('exp'), exp, -1, int(tb_id),))
		db.commit()
	
	# If there is no result, just insert a new one
	else:
		exp = False
		description = text_cat(description, size, category, age)
		if description.prob('exp')>0.5:
			exp = True
		c.execute(''' INSERT INTO text_results VALUES (?,?,?,?) ''',(int(tb_id), description.prob('exp'), exp, -1,))
		db.commit()

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
		try:
			features['desc_exp'] = description_result.prob('exp')
		except:
			features['desc_exp'] = description_result
		return features
	features = find_features(icon_l, screens, description)

	# Save and close the database
	c.execute(''' SELECT exp_per FROM final_results WHERE for_id=? ''', (int(tb_id),))
	res = c.fetchone()
	if res and cache_reload==0:
		db.close()
		return res[0]
	elif res:
		exp = False
		res = classifier.prob_classify(features)
		if res.prob('exp')>0.5:
			exp = True
		c.execute(''' UPDATE final_results SET date=?, exp_per=?, is_mature=?, external_validator=? WHERE for_id=? ''', (time.time(), res.prob('exp'),exp,-1, int(tb_id),))
		db.commit()
		db.close()
		return res
	else:
		exp = False
		res = classifier.prob_classify(features)
		if res.prob('exp')>0.5:
			exp = True
		c.execute(''' INSERT INTO final_results VALUES (?,?,?,?,?) ''', (int(tb_id), time.time(), res.prob('exp'),exp,-1,))
		db.commit()
		db.close()
		return res


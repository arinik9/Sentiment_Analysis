#!/usr/bin/python3

import Preprocessing
import Utils
import json

class TermFrequencyProcessing(object):
	"""
		Input:
			pos_path: path to positive reviews
			neg_path: path to negative reviews
			selected_DB: Utils.DB_ONE or Utils.DB_TWO
	"""
	def __init__(self, pos_path, neg_path, selected_DB):
		self.pos_path = pos_path 
		self.neg_path = neg_path
		self.selected_DB = selected_DB
		self.T = {}   # overal term frequency
		self.pos_terms_json_filename = "pos_terms_freq.json"
		self.neg_terms_json_filename = "neg_terms_freq.json"
		

#############################################
# Getter/Setter
#############################################

	def get_overall_terms_frequency(self):
		return self.T

	def get_pos_path(self):
		return self.pos_path
	
	def get_neg_path(self):
		return self.neg_path


	def set_overall_terms_frequency(self, T):
		self.T = T

	def set_pos_path(self, path):
		self.pos_path = path
	
	def set_neg_path(self, path):
		self.neg_path = path



#####################################################################################################
# Read/Write
#####################################################################################################



#### save terms frequency

	"""

		An example of neg_terms_json_file: 
			{"soon": {"nb_review": 1, "reviews": [[-3, 1]]}, "predecessor": {"nb_review": 1, "reviews": [[-2, 3]]}, ...}

		An example of pos_terms_json_file: 
			{"soon": {"nb_review": 2, "reviews": [[1, 1], [2, 1]]}, ...}


		overall_terms_frequency will be:
		{
			"soon": {
				-1: {				===============> negative review
					"nb_review": 1,
					"reviews": [
						[-3, 1]			===========> the word "soon" is in 1 negative review whose the id is -3 and the term frequency is 1
					]
				},
				1: {				===============> positive review
					"nb_review": 2,
					"reviews": [
						[1, 1],
						[2, 1]
					]
				}
			},
			"predecessor": {
				-1: {
					"nb_review": 1,
					"reviews": [
						[-2, 3]
					]
				}
			},
			.
			.
			.
		}

	"""



	"""
		Read from the json files and get preprocessed vocabulary
	"""
	def read_terms_frequency(self):	
		pos_path = None
		neg_path = None

		if self.selected_DB == Utils.DB_ONE:
			pos_path = Utils.get_parent_directory_for_file(self.pos_path)
			neg_path = Utils.get_parent_directory_for_file(self.neg_path)
		elif self.selected_DB == Utils.DB_TWO:
			pos_path = self.pos_path
			neg_path = self.neg_path		

		with open(pos_path + "/" + self.pos_terms_json_filename, 'r') as json_file:
			json_text = json_file.read()
			pos_terms = json.loads(json_text)

		with open(neg_path + "/" + self.neg_terms_json_filename, 'r') as json_file:
			json_text = json_file.read()
			neg_terms = json.loads(json_text)


		# reset overall term frequency
		self.T.clear() # TODO is it usefull?


		# first read terms and their reviews and frequency information corresponding to negative reviews
		for term, tf_val in neg_terms.items():
			self.T[term] = {}
			self.T[term][Utils.NEG] = tf_val

		# first read terms and their reviews and frequency information corresponding to positive reviews
		for term, tf_val in pos_terms.items():
			if term not in self.T.keys():
				self.T[term] = {}
			self.T[term][Utils.POS] = tf_val
					
	


	"""
		Write into 2 json files in order to save vocabulary and not to do preprocessing each time
	"""
	def write_terms_frequency(self):
		pos_path = None
		neg_path = None

		if self.selected_DB == Utils.DB_ONE:
			pos_path = Utils.get_parent_directory_for_file(self.pos_path)
			neg_path = Utils.get_parent_directory_for_file(self.neg_path)
		elif self.selected_DB == Utils.DB_TWO:
			pos_path = self.pos_path
			neg_path = self.neg_path		

		with open(pos_path + "/" + self.pos_terms_json_filename, 'w') as json_file:
			# extract only terms frequency for positive reviews
			pos_T = {key: val[Utils.POS] for key, val in self.T.items() if Utils.POS in val.keys()} 
			json.dump(pos_T, json_file)

		with open(neg_path + "/" + self.neg_terms_json_filename, 'w') as json_file:
			# extract only terms frequency for negative reviews
			neg_T = {key: val[Utils.NEG] for key, val in self.T.items() if Utils.NEG in val.keys()}
			json.dump(neg_T, json_file)



#####################################################################################################
# term frequency methods
#####################################################################################################

	def compute_terms_frequency(self, V):
		if not V:
			print("There is no vocabulary. Can not compute terms frequency")
			return -1

		self.T.clear() # TODO is it useful?
		
		for sentiment_class in [Utils.NEG, Utils.POS]:
			vocabs = V[sentiment_class]
			# _compute_terms_frequency() updates self.T
			self._compute_terms_frequency(vocabs, sentiment_class)


	def _compute_terms_frequency(self, vocabs, sentiment_class):
		reviews = vocabs["reviews"]

		for review in reviews:
			rating = review["rating"]
			nb_word = review["nb_word"]
			review_id = review["id"]

			review_terms = self.merge_terms_frequency_in_review(review)

			# update_overall_terms_frequency() updates self.T at each call
			self.update_overall_terms_frequency(review_terms, review_id, sentiment_class)




	"""

	An example of output for both negative and positive reviews

	{
		"term1": {
			"-1": {			==============> negative review (sentiment class)
				"nb_review": nb,
				"reviews": [
					(review id, term frequency),
					(review id, term frequency)
				]
			},
			"1": {
				"nb_review": nb,
				"reviews": [
					(review id, term frequency),
					(review id, term frequency)
				]
			}
		},
		"term2": {
			"-1": {
				.
				.
			},
			"1": {
				.
				.
			}
		}
	}
	"""
	def update_overall_terms_frequency(self, review_terms, review_id, sentiment_class):
		T = self.get_overall_terms_frequency()
		
		# review_terms contains all the word in a review  whose its id is review_id
		for term, freq in review_terms.items():
			if term not in T.keys():
				T[term] = {}

			if sentiment_class in T[term].keys():
				T[term][sentiment_class]["nb_review"] += 1
				T[term][sentiment_class]["reviews"].append( (review_id, freq) )
			elif sentiment_class not in T[term].keys():
				T[term][sentiment_class] = {
						"nb_review" :  1,
						"reviews" : [
							(review_id, freq)
						]
					}

		self.set_overall_terms_frequency(T)






	"""
		Input: review, i.e. a list of sentence

		Each sentence is a list of tokens(i.e terms or words).
		The term frequency is associated with the terms.
		It is possible that such a word, let's say "hello", is both in 1st sentence and 2nd sentence.
		In this case, it needs to sum up the frequencies of the word "hello"
		 to use term frequency in review level instead of sentence level.
		This method computes the terms frequency in review level


		An example of output:

		terms: {
				"good" : freq,
				"bad" : freq
			}
		
	"""
	def merge_terms_frequency_in_review(self, review):
		terms = {}
		sentences = review["sentences"]

		for sentence in sentences:
			for word, freq in sentence.items():
				if word in terms.keys():
					terms[word] += freq
				else:
					terms[word] = freq

		return terms



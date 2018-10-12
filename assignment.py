"""	Author: Kei Sum Wang -id:19126089
	Data mining COMP3009 assignment
"""
import numpy as np
import weka.core.jvm as jvm
import weka.core.converters as converters
from weka.filters import Filter
from weka.core.converters import Loader, Saver
from weka.classifiers import Classifier, PredictionOutput, Evaluation
from weka.core.classes import Random


"""function to return index of attribute with significant num of missing values"""
def mostMissing(data):
	strang = ""
	num_attr = data.num_attributes
	num_instances = data.num_instances
	all_attribute_stats = data.attribute_stats
	
	for att in range(0,num_attr):
		stats = all_attribute_stats(att)
		attribute = data.attribute(att)
		
		pctMiss = float(stats.missing_count) / float(num_instances)
		if pctMiss > 0.8:
			strang += str(attribute.index+1) + ','

	strang = strang[:-1] #remove last comma from string
	
	return strang

"""function to return index of attributes that do not have many distinct values"""
#distinct values make up only 1% of the attribute	
def notDistinct(data):
	strang = ""
	num_attr = data.num_attributes
	num_instances = data.num_instances
	all_attribute_stats = data.attribute_stats
	
	for att in range(0,num_attr):
		stats = all_attribute_stats(att)
		attribute = data.attribute(att)
		
		pctNotDist = float(stats.distinct_count) / float(num_instances)
		if pctNotDist < 0.01:
			strang += str(attribute.index+1) + ','

	strang = strang[:-1] #remove last comma from string
	print(strang)
	
	return strang

"""function handling unsupervised filters"""
def unsupFilters(data, fType, ops):

	filt = Filter(classname="weka.filters.unsupervised." + fType, options = ops)
	filt.inputformat(data)     # let the filter know about the type of data to filter
	filtered = filt.filter(data)   # filter the data
	
	return filtered 

"""function handling supervised filters"""
def supFilters(data, fType, ops):

	filt = Filter(classname="weka.filters.supervised." + fType, options = ops)
	filt.inputformat(data)     # let the filter know about the type of data to filter
	filtered = filt.filter(data)   # filter the data
	
	return filtered
	
def naiveBayes(data):
	
	classifier = Classifier(classname="weka.classifiers.bayes.NaiveBayes")
	nfolds=5
	rnd = Random(0)
	evaluation = Evaluation(data)
	evaluation.crossvalidate_model(classifier, data,
	nfolds, rnd)
	print(" Cross-validation information")
	print(evaluation.summary())
	
		
def IBK(data):
	
	classifier = Classifier(classname="weka.classifiers.lazy.IBk")
	nfolds=5
	rnd = Random(0)
	evaluation = Evaluation(data)
	evaluation.crossvalidate_model(classifier, data,
	nfolds, rnd)
	print(" Cross-validation information")
	print(evaluation.summary())
	
def treeJ48(data):
	
	classifier = Classifier(classname="weka.classifiers.trees.J48")
	nfolds=5
	rnd = Random(0)
	evaluation = Evaluation(data)
	evaluation.crossvalidate_model(classifier, data,
	nfolds, rnd)
	print(" Cross-validation information")
	print(evaluation.summary())	


"""function to prepare test and train"""	
def preparation():
	data_file="csvfiles/data.csv"

	try:
		#Load data
		loader=Loader(classname="weka.core.converters.CSVLoader")
		data=loader.load_file(data_file)
		data.class_is_last()
		
		miss = mostMissing(data)#find attributes with significant missing data
		data = unsupFilters(data, "attribute.Remove", ["-R", "1,"+ miss])#remove id and most mising value attributes
		data = unsupFilters(data, "attribute.RemoveUseless", [])#remove use less attributes
		
		nonDistinct = notDistinct(data)#find attributes that are not distinct and convert them to nominal
		data = unsupFilters(data, "attribute.NumericToNominal", ["-R", "last," + nonDistinct])#class convert to nominal
		data = unsupFilters(data, "attribute.ReplaceMissingValues", [])#replace missing values
		data = unsupFilters(data, "attribute.Normalize", [])#normalize attributes to create less bias
		
		#split data into test and training set
		test = unsupFilters(data, "instance.RemoveRange", ["-V", "-R", "901-1000"])
		train = unsupFilters(data, "instance.RemoveRange", ["-R", "901-1000"])
		train = supFilters(train, "instance.SMOTE", ["-P", "160.0"])
		#print(data)
		
		saver = Saver(classname="weka.core.converters.ArffSaver")
		saver.save_file(test, "test.arff")
		saver.save_file(train, "train.arff")
		
		#Performing cross validation using naiveBayes, IBk and j48 tree
		print("Naive Bayes")
		naiveBayes(train)
		print("IBK")
		IBK(train)
		print("J48 tree")
		treeJ48(train)
		
		print("Data loaded successfully")
	except IOError:
		print("Error loading file " + data_file)

#Main method
if __name__ == '__main__':
	#Start java VM with 1GB heap memory, use system classpath and additional packages
	jvm.start(system_cp=True, packages=True,max_heap_size="1024m")	
	
	#Implement question 1
	preparation()
	
	#Terminate JVM
	jvm.stop()

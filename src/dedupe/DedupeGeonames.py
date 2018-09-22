# -*- coding: utf-8 -*-
"""
Created on Sat Sep 15 19:19:15 2018

@author: Developer
"""

from future.builtins import next
import os
import csv
import re
import logging
import sys

import argparse as ag
import dedupe
from unidecode import unidecode
import traceback as tb
import psutil as pu
#import objgraph as og

# ## Logging
logger = logging.getLogger('dedupe')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger.setLevel(logging.INFO)
fileLogger = logging.FileHandler('dedupe.log')
fileLogger.setFormatter(formatter)
fileLogger.setLevel(logging.INFO)
logger.addHandler(fileLogger)

def preProcess(column):
    """
    Do a little bit of data cleaning with the help of Unidecode and Regex.
    Things like casing, extra spaces, quotes and new lines can be ignored.
    """
    # If data is missing, indicate that by setting the value to `None`
    if not column:
        column = None
    return column
    
    """
    try : # python 2/3 string differences
        column = column.decode('utf8')
    except AttributeError:
        pass
    """
    column = unidecode(column)
    column = re.sub('  +', ' ', column)
    column = re.sub('\n', ' ', column)
    column = column.strip().strip('"').strip("'").lower().strip()
    # If data is missing, indicate that by setting the value to `None`
    if not column:
        column = None
    return column

def readData(filename, encoding, delimiter, header, keyfield, maxRecordCount=None):
    """
    Read in our data from a CSV file and create a dictionary of records, 
    where the key is a unique record ID and each value is dict
    If no latitude or longitude exists the record is thrown away.
    """

    data_d = {}
    recordCount = 0
    with open(filename, encoding=encoding) as f:
        reader = csv.DictReader(f, fieldnames=header, delimiter=delimiter, quoting=csv.QUOTE_NONE)
        for row in reader:
            clean_row = [(k, preProcess(v)) for (k, v) in row.items()]
            latitude = None
            longitude = None
            for (k, v) in clean_row:
                if 'latitude' == k:
                    latitude = float(v)
                if 'longitude' == k:
                    longitude = float(v)
            if latitude and longitude:
                clean_row.append(('geometry', (latitude, longitude)))
                row_id = int(row[keyfield])
                data_d[row_id] = dict(clean_row)
                recordCount += 1
                if (maxRecordCount and maxRecordCount == recordCount):
                    return data_d

    return data_d

# ## Parsing arguments
argParser = ag.ArgumentParser(description='Train a deduplication model for record linkage using Geonames')
argParser.add_argument('--input', default='D:/Geonames/geonames_modifications_sorted.tsv', nargs='?', type=str, help='Path to the labeled geonames file containing duplicates.')
argParser.add_argument('--train', default='D:/Geonames/train.json', nargs='?', type=str, help='Output path to training file.')
argParser.add_argument('--settings', default='D:/Geonames/train.settings', nargs='?', type=str, help='Output path to settings file.')
arguments = argParser.parse_args(sys.argv[1:])
if (arguments.input and arguments.train and arguments.settings):
    pass
else:
    argParser.print_help()
    sys.exit(1)

try:
    # ## Log memory infos
    process = pu.Process(os.getpid())
    memInfo = process.memory_info()
    logger.info('Memory usage rss: {} MB, vms: {} MB'.format(memInfo.rss/1024/1024, memInfo.vms/1024/1024))

    # ## Import training data
    logger.info('Reading training data')
    filename = arguments.input
    header = ['id', 'geonameid','name','asciiname','alternatenames','latitude','longitude','feature class','feature code','country code','cc2','admin1 code','admin2 code','admin3 code','admin4 code','population','elevation','dem','timezone','modification date']
    keyfield = 'id'
    maxRecordCount = 50000
    trainingData = readData(filename, 'utf-8', '\t', header, keyfield, maxRecordCount)
    
    # ## Training
    fields = [
        { 'field':'name', 'type':'String' },
        { 'field':'asciiname', 'type':'String' },
        { 'field':'geometry', 'type':'LatLong', 'has missing':True },
        { 'field':'country code', 'type':'Exact', 'has missing':True }
    ]
    commonField = 'geonameid'
    
    # Create labeled data
    trainingSize = int(0.8*len(trainingData))
    labeledData = dedupe.trainingDataDedupe(trainingData, commonField, training_size=trainingSize)
    
    # Create the matcher
    logger.info('Train using the labeled data')
    matcher = dedupe.Dedupe(fields)
    sampleSize = int(0.2*len(trainingData))
    matcher.sample(trainingData, sample_size=sampleSize)
    matcher.markPairs(labeledData)
    matcher.train()
    logger.info('Training finished')
    
    # When finished, save our training to disk
    trainingFile = arguments.train
    with open(trainingFile, 'w') as tf:
        matcher.writeTraining(tf)
        
    # Save our weights and predicates to disk. If the settings file
    # exists, we will skip all the training and learning next time we run
    # this file.
    settingsFile = arguments.settings
    with open(settingsFile, 'wb') as sf:
        matcher.writeSettings(sf)
        
    memInfo = process.memory_info()
    logger.info('Memory usage rss: {} MB, vms: {} MB'.format(memInfo.rss/1024/1024, memInfo.vms/1024/1024))
    
    matcher.cleanupTraining()
    del matcher
except Exception as e:
    logger.exception("Dedupe failed badly!")
    memInfo = process.memory_info()
    logger.info('Memory usage rss: {} MB, vms: {} MB'.format(memInfo.rss/1024/1024, memInfo.vms/1024/1024))
    #og.show_most_common_types(file=open('leaks.txt', 'w+'))
    
    
    # ## Import real data
    '''
    filename = r'D:/Geonames/cities1000.txt'
    header = ['geonameid','name','asciiname','alternatenames','latitude','longitude','feature class','feature code','country code','cc2','admin1 code','admin2 code','admin3 code','admin4 code','population','elevation','dem','timezone','modification date']
    keyfield = 'geonameid'
    geonames = readData(filename, 'utf-8', '\t', header, keyfield)
    
    # Create the matcher from the settings file
    with open(settingsFile, 'rb') as f:
        matcher = dedupe.StaticDedupe(f)
        threshold = matcher.threshold(geonames)
        matches = matcher.match(geonames, threshold)
        print('%s duplicates found.' % len(matches))
    
        del matcher
    
    def printMatches(matches):
        for (clusterId, cluster) in enumerate(matches):
            ids, scored = cluster
            print(clusterId)
            for id in ids:
                print (geonames[id]['name'])
    '''
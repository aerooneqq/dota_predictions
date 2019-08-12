from Learn import Learn

from DataCollector import DataCollector

learn = Learn("outputdata_extended.csv")

learn.prepareData()
learn.learn()
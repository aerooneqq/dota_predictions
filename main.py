
from Learn import Learn
from CsvService import CSVService
from DataCollector import DataCollector

tiMatches =  DataCollector().getTIMatches()

learn = Learn()
learn.prepareData()
learn.learnLogisticRegression()



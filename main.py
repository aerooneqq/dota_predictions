import os

from Learn import Learn
from CsvService import CSVService
from DataCollector import DataCollector

CURR_DIR = str(os.getcwd())

learn = Learn()

#learn.addMatchesToData()

#learn.getAccuracy(5)

#learn.prepareData().addGroupMatchesToData(1).addGroupMatchesToData(2).addGroupMatchesToData(3)
#learn.addGroupMatchesToData(4).addTiMatchesToData(1).addTiMatchesToData(2).addTiMatchesToData(3).addTiMatchesToData(4)
#learn.addTiMatchesToData(5)

#learn.learnMLP()

matchesDataFile = os.path.join(CURR_DIR, 'matches_data', 'main_event_day_6.txt')
predictionsFilePath = os.path.join(CURR_DIR, 'predictions_data', 'main_event_day_6_predictions.txt')

learn.predictMatches(matchesDataFile, predictionsFilePath)
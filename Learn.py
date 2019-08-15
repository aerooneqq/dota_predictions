import json
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import RidgeClassifier
from sklearn import preprocessing
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GridSearchCV

from sklearn.feature_selection import RFE
from sklearn.model_selection import train_test_split

import pandas as pd
import numpy as np

class Learn:
    def __init__(self):
        self.X = []
        self.Y = []
        self.idNumDict = {}
        
        #learning properties:
        self._iterCount = 100


    def prepareData(self):
        with open("outputdata_extended.csv", 'r') as fin, open("ligaments.json", 'r') as ligamentsFile:
            ligaments = json.load(ligamentsFile)
            lines = fin.readlines()

            ids = set()

            for i in range(1, len(lines)):
                data = list(map(float, lines[i].split(";")))

                if (not(int(data[0]) in ids)):
                    ids.add(int(data[0]))

                    clearedData = []
                    for i in range(6, 66):
                        clearedData.append(data[i])
                    
                    for i in range(len(data) - 26, len(data) - 1):
                        clearedData.append(data[i])
                    
                    self.X.append(clearedData)
                    self.Y.append(int(data[len(data) - 1]))
        
        print(len(ids))
        self.X = np.array(self.X)
        

    def prepareMatchMakingData(self):
        with open("public_matches_data.csv", 'r') as fin, open("ligaments.json", 'r') as ligamentsFile:
            lines = fin.readlines()
            ligaments = json.load(ligamentsFile)
        
            for i in range(1, 500):
                data = lines[i].split(';')
                
                radiantPick = list(map(int, data[3].split(',')))
                direPick = list(map(int, data[4].split(',')))

                radiantPickList = self._getPickList(radiantPick)
                direPickList = self._getPickList(direPick)

                dataList = []

                for rPick in radiantPick:
                    for dPick in direPick:
                        dataList.append(self._getMatchUp(rPick, dPick))

                self.X.append(dataList)
                self.Y.append(1 if data[2] == "True" else 0)
                

    def _getMatchUp(self, firstHero, secondHero):
        with open("matchups/hero_" + str(firstHero) + ".json", 'r') as fin:
            jsonData = (fin.read()).replace("\\", "")[1:]
            jsonData = jsonData[:len(jsonData) - 1]

            matchups = json.loads(jsonData)

            for matchup in matchups:
                if (matchup["hero_id"] == secondHero): 
                    return matchup["wins"] / matchup["games_played"]
        return 0.5

    def _createPickList(self):
        return [0 for _ in range(117)]

    def _getPickList(self, pick):
        pickList = self._createPickList()
        heroesIDNumDict = self._getIdNumDict()

        for i in range(len(pick)):
            pickList[heroesIDNumDict[pick[i]]] = 1

        return pickList


    def _getIdNumDict(self):
        heroesIDNumDic = {}
        with open("heroes.json", 'r') as fin:
            heroes = json.load(fin)

            currId = 0
            for hero in heroes:
                heroesIDNumDic[hero["id"]] = currId
                currId += 1
        
        return heroesIDNumDic


    def _getSamples(self):
        xTrain, xTest, yTrain, yTest = train_test_split(self.X, self.Y)

        return xTrain, xTest, yTrain, yTest

    
    def learnLogisticRegression(self):
        xTrain, xTest, yTrain, yTest = self._getSamples()

        paramGrid = { 
            'solver': ['newton-cg', 'lbfgs', 'liblinear', 'sag', 'saga'],
            'C': np.linspace(0.001, 1, num = 5),
            'max_iter': [1000, 1600, 1800, 2000]
        }

        logisticRegression = LogisticRegression()
        optimizer = GridSearchCV(logisticRegression, paramGrid, cv=3)

        optimizer.fit(xTrain, yTrain)

        print("Best model params: ")
        print(optimizer.best_params_)

        print('Train score: ' + str(optimizer.score(xTrain, yTrain)))
        print('Test score: ' + str(optimizer.score(xTest, yTest)))




import json
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import RidgeClassifier

from sklearn.model_selection import train_test_split

import pandas as pd
import numpy as np

class Learn:
    def __init__(self, filePath):
        self.filePath = filePath
        self.X = []
        self.Y = []
        self.idNumDict = {}

    def _createPickList(self):
        return [0 for _ in range(117)]

    def prepareData(self):
        with open("heroes.json", 'r') as fin:
            heroes = json.load(fin)
            
            index = 0
            for hero in heroes: 
                self.idNumDict[hero["id"]] = index
                index += 1
        
        with open(self.filePath, 'r') as fin, open("matchWinners.txt", "r") as fInMatches:
            lines = fin.readlines()
            matchesResults = fInMatches.readlines()
            ids = set()
            index = 0

            for i in range(len(lines)): 
                line = lines[i]
                if (len(line) > 3):
                    matchRes = matchesResults[index]
                    index += 1
                    data = list(map(float, line.split(";")))
                    if (not(int(data[0]) in ids)):
                        ids.add(int(data[0]))
                        clearedData = []

                        firstPick = self._createPickList()

                        for i in range(1, 6):
                            firstPick[self.idNumDict[data[i]]] = 1
                        
                        secondPick = self._createPickList()

                        for i in range(len(data) - 5, len(data)):
                            secondPick[self.idNumDict[data[i]]] = 1
                        
                        #for pick in firstPick:
                            #data.append(pick)
                        
                        #for pick in secondPick: 
                            #data.append(pick)

                        for i in range(6, len(data) - 5):
                            clearedData.append(data[i])


                        self.X.append(np.array(clearedData))

                        if (matchRes[:len(matchRes) -1] == "True"):
                            self.Y.append(1)
                        else:
                            self.Y.append(0)

            self.X = np.array(self.X)
            print(self.X.shape)
            
            self.Y = np.array(self.Y)
            print(self.Y.shape)
        
                    
    def _getSamples(self):
        xTrain, xTest, yTrain, yTest = train_test_split(self.X, self.Y)

        return xTrain, xTest, yTrain, yTest

    
    def learn(self):
        iterCount = 100
        avg = 0
        numberLessThanFifty = 0

        for _ in range(iterCount):
            xTrain, xTest, yTrain, yTest = self._getSamples()       


            clf = LogisticRegression(C = 1, penalty="l2")
            #clf = MLPClassifier(solver='sgd', alpha=1e-3, hidden_layer_sizes=(50, 20), max_iter=1000, activation="logistic")

            clf.fit(xTrain, yTrain)

            score = clf.score(xTest, yTest)
            print(str(clf.score(xTrain, yTrain)) + " " + str(clf.score(xTest, yTest)))
            avg += score
            if (score < 0.5):
                numberLessThanFifty += 1
        
        print(avg/iterCount, numberLessThanFifty)
         

import json
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import RidgeClassifier
from sklearn import preprocessing

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
        with open(self.filePath, 'r') as fin:
            lines = fin.readlines()

            for i in range(1, len(lines)):
                data = list(map(float, lines[i].split(";")))

                clearedData = []
                for i in range(6, 66):
                    clearedData.append(data[i])
                
                for i in range(len(data) - 26, len(data) - 1):
                    clearedData.append(data[i])
                
                self.X.append(clearedData)
                self.Y.append(int(data[len(data) - 1]))

                    
    def _getSamples(self):
        xTrain, xTest, yTrain, yTest = train_test_split(self.X, self.Y)

        return xTrain, xTest, yTrain, yTest

    
    def learn(self):
        iterCount = 100
        avg = 0
        numberLessThanFifty = 0

        for _ in range(iterCount):
            #self.X = preprocessing.scale(self.X)

            xTrain, xTest, yTrain, yTest = self._getSamples()       

            clf = LogisticRegression(C = 200, penalty="l2", solver="lbfgs", max_iter=1000)
            #clf = MLPClassifier(solver='sgd', alpha=1e-3, hidden_layer_sizes=(100, 100, 20), max_iter=1000, activation="logistic")

            clf.fit(xTrain, yTrain)

            score = clf.score(xTest, yTest)
            print(str(clf.score(xTrain, yTrain)) + " " + str(clf.score(xTest, yTest)))
            avg += score
            if (score < 0.5):
                numberLessThanFifty += 1
        
        print(avg/iterCount, numberLessThanFifty)
         

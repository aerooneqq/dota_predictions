import json
import os
import pickle
import math

import pandas as pd
import numpy as np

from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LogisticRegression
from sklearn import preprocessing
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GridSearchCV

from sklearn.model_selection import train_test_split


CURR_DIR = os.getcwd()
MAIN_EVENT_FILE_PREFIX = 'main_event_day_'
GROUP_STAGE_FILE_PREFIX = 'group_day_'

class Learn:

    def __init__(self):
        self.X = []
        self.Y = []
        self.idNumDict = {}
        
        #learning properties:
        self._iterCount = 100

            
    def addMatchesToData(self):
        matches = [ ]

        with open(os.path.join(CURR_DIR, 'matches_data', 'main_event_day_6.txt'), 'a') as fout:
            for match in matches:
                firstPick = match[3:8]
                secondPick = match[len(match) - 5 : len(match)]

                for fp in firstPick:
                    for sp in secondPick: 
                        match.append(self._getMatchUp(fp, sp))
            
                fout.write(";".join(list(map(str,match))) + "\n")


    def prepareData(self):
        with open(os.path.join(CURR_DIR, 'matches_data', 'learning_data.csv'), 'r') as fin:

            lines = fin.readlines()
            ids = set()

            for i in range(1, len(lines)):
                data = lines[i].split(";")

                if (not(int(data[0]) in ids)):
                    ids.add(int(data[0]))

                    clearedData = []
                    for i in range(6, 66):
                        clearedData.append(self._getNumericalFeatureRepresentation(data[i]))
                    
                    for i in range(len(data) - 26, len(data) - 1):
                        clearedData.append(self._getNumericalFeatureRepresentation(data[i]))
                    
                    self.X.append(clearedData)
                    self.Y.append(int(data[len(data) - 1]))
                
        return self


    def _getNumericalDataRepresentation(self, dataString):
        return list(map(lambda feature: self._getNumericalFeatureRepresentation(feature), dataString.split(';')))

    
    def _getNumericalFeatureRepresentation(self, featureString):
        return math.pow(float(featureString), 1)


    def addGroupMatchesToData(self, groupDay):
        with open(os.path.join(CURR_DIR, 'matches_data', 'group_day_' + str(groupDay) + ".txt"), 'r') as matchesFile:
            with open(os.path.join(CURR_DIR, 'results_data', 'group_day_' + str(groupDay) + '_results.txt'), 'r') as resultsFile:
                matches = matchesFile.readlines()
                results = list(map(int, resultsFile.readlines()))

                for i in range(len(matches)):
                    self.X.append(self._getXSampleFromRawData(matches[i].split(';')))
                    self.Y.append(results[i])
        
        return self

    def addTiMatchesToData(self, mainEventDay):
        with open(os.path.join(CURR_DIR, 'matches_data', MAIN_EVENT_FILE_PREFIX + str(mainEventDay) + ".txt")) as matchesFile:
            with open(os.path.join(CURR_DIR, 'results_data', MAIN_EVENT_FILE_PREFIX + str(mainEventDay) + "_results.txt")) as resultsFile:
                matches = matchesFile.readlines()
                results = list(map(int, resultsFile.readlines()))

                for i in range(len(matches)):
                    self.X.append(self._getXSampleFromRawData(matches[i].split(';')))
                    self.Y.append(results[i])

        return self


    def _getXSampleFromRawData(self, data):
        xSample = []

        #append team hero winrate and player-hero winrate
        for feature in data[8:68]:
            xSample.append(self._getNumericalFeatureRepresentation(feature))
        
        #append the heroes matchups
        for feature in data[len(data) - 25 : len(data)]:
            xSample.append(self._getNumericalFeatureRepresentation(feature))

        return xSample


    def prepareMatchMakingData(self):
        with open(os.path.join(CURR_DIR, 'matches_data', 'public_matches_data.csv'), 'r') as fin:
            lines = fin.readlines()
        
            for i in range(1, 500):
                data = lines[i].split(';')
                
                radiantPick = list(map(int, data[3].split(',')))
                direPick = list(map(int, data[4].split(',')))

                dataList = []

                for rPick in radiantPick:
                    for dPick in direPick:
                        dataList.append(self._getMatchUp(rPick, dPick))

                self.X.append(dataList)
                self.Y.append(1 if data[2] == "True" else 0)

        return self
                

    def _getMatchUp(self, firstHero, secondHero):
        with open(os.path.join(CURR_DIR, 'json_data', 'matchups', 'hero_' + str(firstHero) + ".json"), 'r') as fin:
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
        with open(os.path.join(CURR_DIR, 'json_data', 'heroes.json'), 'r') as fin:
            heroes = json.load(fin)

            currId = 0
            for hero in heroes:
                heroesIDNumDic[hero["id"]] = currId
                currId += 1
        
        return heroesIDNumDic


    def _getSamples(self):
        xTrain, xTest, yTrain, yTest = train_test_split(self.X, self.Y, train_size=0.8)

        return xTrain, xTest, yTrain, yTest

    
    def learnLogisticRegression(self):
        xTrain, xTest, yTrain, yTest = self._getSamples()

        logisticRegression = LogisticRegression(C = 0.1, max_iter=1000, solver='lbfgs')

        logisticRegression.fit(xTrain, yTrain)

        print('Train score: ' + str(logisticRegression.score(xTrain, yTrain)))
        print('Test score: ' + str(logisticRegression.score(xTest, yTest)))

        with open(os.path.join(CURR_DIR, 'models', 'LogisticRegressionModel.pkl'), 'wb') as modelFile:
            pickle.dump(logisticRegression, modelFile)

        return self

    
    def learnMLP(self):
        xTrain, xTest, yTrain, yTest = self._getSamples()

        mlp = MLPClassifier(hidden_layer_sizes=(85, 85), activation="tanh", solver='sgd', max_iter = 2000)
        mlp.fit(xTrain, yTrain)

        print('Train score: ' + str(mlp.score(xTrain, yTrain)))
        print('Test score: ' + str(mlp.score(xTest, yTest)))

        with open(os.path.join(CURR_DIR, 'models', 'MLPModel.pkl'), 'wb') as modelFile:
            pickle.dump(mlp, modelFile)

        return self
    

    #Predicts the result of the matches with give estimator which are written in the file with a filePath 
    def predictMatches(self, matchesFilePath, predictionsFilePath):
        estimator = self._getDefaultModel()

        with open(matchesFilePath, 'r') as matchesFile:
            with open(predictionsFilePath, 'w') as predictionsFile:
                matches = matchesFile.readlines()

                for match in matches:
                    rawData = match.split(';')
                    xSample = self._getXSampleFromRawData(rawData)

                    prediction = estimator.predict([xSample])[0]
                    predictedTeamName = rawData[1] if prediction == 1 else rawData[2]

                    predictionsFile.write(str(prediction) + '\n')

                    print(rawData[1] + " vs " + rawData[2] + ". Prediction: " + predictedTeamName + 
                            '. Confidence rate: ' + str(estimator.predict_proba([xSample])[0]))


    def _getDefaultModel(self):
        with open(os.path.join(CURR_DIR, 'models', 'MLPModel.pkl'), 'rb') as modelFile:
            return pickle.load(modelFile)


    def _fitPartialData(self, mlp, xTrain, yTrain):
        mlp.partial_fit([xTrain], [yTrain])


    def _getTeamNameByID(self, teamID):
        with open('teams.json', 'r', encoding="UTF8") as fin:
            teams = json.load(fin)

            for team in teams:
                if (team["team_id"] == teamID):
                    return team["name"]

        return ""

    
    def getAccuracy(self, dayNumber):
        print("Accuracy for day " + str(dayNumber) + ': ')

        predictionsPath = os.path.join(CURR_DIR, 'predictions_data', MAIN_EVENT_FILE_PREFIX + str(dayNumber) + '_predictions.txt')
        resultsPath = os.path.join(CURR_DIR, 'results_data', MAIN_EVENT_FILE_PREFIX + str(dayNumber) + '_results.txt')

        with open(predictionsPath, 'r') as predictionsFile:
            with open(resultsPath, 'r') as resultsFile:
                results = resultsFile.readlines()
                predictions = predictionsFile.readlines()
                rightPredictionsCount = 0

                for i in range(len(results)):
                    if (int(results[i]) == int(predictions[i])):
                        rightPredictionsCount+=1
                
                print("RIGHT PREDICTIONS COUNT: " + str(rightPredictionsCount) + ' out of ' + str(len(results)))
                print("RIGHT PREDICTIONS PERCENTAGE " + str(rightPredictionsCount/len(results)))

        return self 
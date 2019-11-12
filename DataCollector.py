import requests
import json
import datetime
import time
import CsvService
import os
from CsvService import CSVService
from random import *

CURR_DIR = os.getcwd()
FILE_PREFIX = 'main_event_day_1.txt'

class DataCollector:
    def __init__(self):
        self.heroesUrl = "https://api.opendota.com/api/heroes/"
        self.teamsUrl = "https://api.opendota.com/api/teams/"
        self.playersUrl = "https://api.opendota.com/api/players/"
        self.matchesUrl = "https://api.opendota.com/api/matches/"
        self._liveGamesURL = "https://api.opendota.com/api/live/"
        self._matchDataURL = "https://api.opendota.com/api/matches/"

        self._tiLeagueID = 10749

        self.requestsCount = 0

        self.tiTeamsId = [
            #vp
            1883502,
            #secret
            1838315,
            #eg
            39,
            #fnatic
            350190,
            #vici
            726228,
            #psg lgd
            15,
            #nip
            2085365,
            #liquid
            2163,
            #og
            2586976,
            #keen
            2626685,
            #tnc
            2108395,
            #alliance
            111474,
            #navi
            36,
            #mineski
            543897,
            #infamous
            2672298,
            #rng
            6209804,
            #chaos
            6666989,
            #fwd (newbee na)
            6214538
        ]

    def getClearedData(self, data):
        return data.replace("\\", "")

    def collectHeroesData(self):
        data = json.loads(self.getClearedData(requests.get(self.heroesUrl).text))
        jsonText = json.dumps(data)

        with open(os.path.join(CURR_DIR, 'json_data', 'heroes.json'), 'w') as fout:
            fout.write(jsonText)

    def _getMatchWinnerWithMatchID(self, matchID, index):
        url = self.matchesUrl + str(matchID)
        data = json.loads(self.getClearedData(requests.get(url).text))
        return self._getMatchWinner(data, int(index / 38))
    
    def _getMatchWinner(self, data, index):
        print(index)
        teamID = self.tiTeamsId[index]

        if (int(data["radiant_team"]["team_id"]) == teamID):
            return data["radiant_win"]
        
        if (data["radiant_win"] == True):
            return False

        return True

    def collectData(self):
        
        for i in range(16, len(self.tiTeamsId)):
            matchesID = self._getTeamMatches(self.tiTeamsId[i])

            if (i == 16):
                start = 39
            else:
                start = 38
            for j in range(start, 50):
                startTime = datetime.datetime.now()
                print("Current step: ", i, j)

                resultMatchData = [matchesID[j]]

                print("Getting the match data...")
                matchData = self._getMatchData(matchesID[j])

                #Get ids of the teams
                firstTeamId = self.tiTeamsId[i]
                secondTeamId = self._getSecondTeamId(matchData, firstTeamId)

                print("Getting the heroes data of the first team...")
                firstTeamHeroesData = self._getTeamHeroData(firstTeamId)

                print("Getting the heroes data of the second team...")
                secondTeamHeroesData = self._getTeamHeroData(secondTeamId)

                firstTeamPlayerHeroDict, secondTeamPlayerHeroDict = self._getPlayersHeroesDicts(matchesID[j], 
                    self.tiTeamsId[i], matchData)
                
                print("Filling first team players-heroes data...")
                for playerID in firstTeamPlayerHeroDict:
                    resultMatchData.append(firstTeamPlayerHeroDict[playerID])

                print("Filling first team heroes winrate...")
                for playerID in firstTeamPlayerHeroDict:
                    heroID = firstTeamPlayerHeroDict[playerID] 
                    resultMatchData.append(self._getTeamsHeroWinrate(heroID, firstTeamHeroesData))


                print("Filling first players winrate against enemy heroes...")
                for playerID in firstTeamPlayerHeroDict:
                    for enemyPlayerId in secondTeamPlayerHeroDict:
                        heroID = secondTeamPlayerHeroDict[enemyPlayerId]
                        resultMatchData.append(self._getPlayersHeroAgainstWinrate(playerID, heroID))

                print("Filling second players winrate against enemy heroes...")
                for playerID in secondTeamPlayerHeroDict:
                    for enemyPlayerId in firstTeamPlayerHeroDict:
                        heroID = firstTeamPlayerHeroDict[enemyPlayerId]
                        resultMatchData.append(self._getPlayersHeroAgainstWinrate(playerID, heroID))

                print("Filling the second team heroes winrate")
                for playerID in secondTeamPlayerHeroDict:
                    heroID = secondTeamPlayerHeroDict[playerID]
                    resultMatchData.append(self._getTeamsHeroWinrate(heroID, secondTeamHeroesData))
                                
                print("Filling second team players-heroes data...")
                for playerID in secondTeamPlayerHeroDict:
                    resultMatchData.append(secondTeamPlayerHeroDict[playerID])

                print("Writing data to file: ")
                csvService = CsvService.CSVService("outputdata_new.csv")
                csvService.writeToFile(resultMatchData, mode = 'a')

                with open("matchWinners_new.txt", 'a') as fout:
                    fout.write(str(self._getMatchWinner(matchData, i)) + "\n")

                processTime = datetime.datetime.now() - startTime
                print("Process time (second): ", processTime.seconds)
    
    def _getMatchData(self, matchID):
        url = self.matchesUrl + str(matchID)
        return json.loads(self.getClearedData(requests.get(url).text))

    def _getTeamHeroData(self, teamID):
        url = self.teamsUrl + str(teamID)
        return json.loads(self.getClearedData(requests.get(url).text))

    def _getSecondTeamId(self, data, firstTeamId):
        if (int(data["radiant_team"]["team_id"]) == firstTeamId):
            return int(data["dire_team"]["team_id"])

        return int(data["radiant_team"]["team_id"])

    def _getTeamMatches(self, teamId):
        url = self.teamsUrl + str(teamId)
        data = json.loads(self.getClearedData(requests.get(url).text))

        return list(map(lambda x : x["match_id"], data))

    def _getPlayersHeroesDicts(self, matchID, firstTeamId, data):
        playersData = data["players"]

        radiantTeamPlayersHeroersDict = {}
        direTeamPlayersHeroesDict = {}

        for playerData in playersData:
            if (playerData["team_id"] == firstTeamId):
                radiantTeamPlayersHeroersDict[int(playerData["account_id"])] = int(playerData["hero_id"])
            else:
                direTeamPlayersHeroesDict[int(playerData["account_id"])] = int(playerData["hero_id"])
        
        return radiantTeamPlayersHeroersDict, direTeamPlayersHeroesDict

    def _getPlayersHeroWinrate(self, playerID, heroID):
        url = self.playersUrl + str(playerID) + "/heroes"
        data =  json.loads(self.getClearedData(requests.get(url).text))

        for hero in data:
            if (int(hero["hero_id"]) == heroID):
                if (int(hero["games"] == 0)):
                    return -1

                return int(hero["win"]) / int(hero["games"])
        
        return -1
    
    def _getPlayersHeroAgainstWinrate(self, playerID, heroID):
        url = self.playersUrl + str(playerID) + "/heroes"
        data = json.loads(self.getClearedData(requests.get(url).text))

        for hero in data:
            if (int(hero["hero_id"]) == heroID):
                if (int(hero["against_games"]) == 0):
                    return -1
                
                return int(hero["against_win"]) / int(hero["against_games"])
        
        return -1

    def _getTeamsHeroWinrate(self, heroID, data):
        for hero in data:
            if (int(hero["hero_id"]) == heroID):
                if (int(hero["games_played"]) == 0):
                    return -1
                return int(hero["wins"])/ int(hero["games_played"])
            
        return -1

    
    def extendData(self):
        with open("outputdata_cleared_new .csv", 'r') as fin, open("outputdata_extended_new.txt", 'w') as fout:
            ids = set()

            lines = fin.readlines()
            newLines = [";".join(CSVService({"asd"}).fileHeader) + "\n"]

            for i in range(1, len(lines)):
                line = lines[i]
                data = list(map(float, line.split(';')))

                if (not(int(data[0]) in ids)):
                    ids.add(int(data[0]))
                    firstPick = list(map(int, data[1:6]))
                    secondPick = list(map(int, data[(len(data)-6) : (len(data) - 1)]))
                    
                    heroesWinrate = ""

                    for firstHero in firstPick:
                        for secondHero in secondPick:
                            heroesWinrate += str(self._getHeroesMatchUp(firstHero, secondHero)) + ";"
                
                    newLines.append(line[:len(line) - 2] + heroesWinrate + str(int(data[len(data) - 1])) + "\n")

            
            fout.writelines(newLines)

                
    def _getHeroesMatchUp(self, firstHero, secondHero):
        with open(os.path.join(CURR_DIR, 'json_data', 'matchups', 'hero_' + str(int(firstHero)) + ".json"), 'r', encoding = "UTF8") as fin:
            data = fin.read()
            data = data.replace("\\", "")[1:]
            data = data[:len(data) - 1]
            data = json.loads(data)

            for hero in data: 
                if (hero["hero_id"] == secondHero): 
                    return hero["wins"]/hero["games_played"]

        return -1

    
    def _getPlayersWinrateWithLigament(self, heroID, playerID, ligament):
        url = self.playersUrl + str(playerID) + "/wl?limit=10000" + "&against_hero_id=" + str(ligament[1]) + "&against_hero_id=" + str(ligament[0])

        done = False

        while (not(done)): 
            try:
                data = requests.get(url)

                return data.text
            except Exception as ex:
                print(ex)


    def _getHeroesLigaments(self, pick):
        ligaments = []

        for i in range(len(pick)):
            for j in range(i+1, len(pick)):
                ligaments.append([int(pick[i]), int(pick[j])])
        
        return ligaments


    def _getHeroesMatchUps(self, fileName): 
        with open(os.path.join(CURR_DIR, 'json_data', 'heroes.json'), 'r') as fin:
            heroes = json.load(fin)

            for hero in heroes:
                done = False

                while (not(done)): 
                    try:
                        data = requests.get(self.heroesUrl + str(hero["id"]) + "/matchups")
                        if (data.status != 200):
                            raise Exception("NOT OK RESULT")

                        with open("matchups/hero_" + str(hero["id"]) + ".json", 'w') as fout: 
                            json.dump(data.text, fout)
                        done = True

                        print("Wrote hero %i", hero["id"])

                        time.sleep(1)
                    except Exception as ex:
                        print(ex)
    
    def collectHeroesLigaments(self):
        ligaments = dict()

        with open("heroes.json") as fin:
            data = json.load(fin)

            for i in range(len(data)):
                hero = data[i]
                ligaments[hero["id"]] = dict()
                for j in range(i + 1, len(data)):
                    second_hero = data[j]
                    ligaments[hero["id"]][second_hero["id"]] = {}
                    ligaments[hero["id"]][second_hero["id"]]["games_with"] = 0
                    ligaments[hero["id"]][second_hero["id"]]["win"] = 0
                    
        print(ligaments)

        try:
            a = 0
            while (a==0):
                data = []
                with open("public_matches_data", 'r') as fin:
                    lines = fin.readlines()

                    for line in lines:
                        line = line.split(';')
                        data.append({ 
                            "radiant_team": line[3],
                            "dire_team": line[4][:len(line[4]) - 1],
                            "radiant_win": bool(line[2])
                        })

                for match in data:
                    radiantPickLigaments = self._getHeroesLigaments(list(map(int, match["radiant_team"].split(','))))
                    direPickLigaments =  self._getHeroesLigaments(list(map(int, match["dire_team"].split(','))))

                    if (match["radiant_win"] == True):
                        for ligament in radiantPickLigaments:
                            ligaments[min(ligament[0], ligament[1])][max(ligament[0], ligament[1])]["games_with"] += 1
                            ligaments[min(ligament[0], ligament[1])][max(ligament[0], ligament[1])]["win"] += 1
                                
                        for ligament in direPickLigaments:
                            ligaments[min(ligament[0], ligament[1])][max(ligament[0], ligament[1])]["games_with"] += 1

                    else: 
                        for ligament in radiantPickLigaments:
                                    ligaments[min(ligament[0], ligament[1])][max(ligament[0], ligament[1])]["games_with"] += 1
                                
                        for ligament in direPickLigaments:
                            ligaments[min(ligament[0], ligament[1])][max(ligament[0], ligament[1])]["games_with"] += 1
                            ligaments[min(ligament[0], ligament[1])][max(ligament[0], ligament[1])]["win"] += 1
                a = 1

        except Exception as ex:
            print(ex)
            with open("ligaments.json", 'w') as fout:
                json.dump(ligaments, fout)
        
        with open("ligaments.json", 'w') as fout:
            json.dump(ligaments, fout)



    def _getLigamentIndex(self, ligament):
        return str(min(ligament[0], ligament[1])) + "," + str(max(ligament[0], ligament[1]))

    def _getTwoLigamentsIndexes(self, firstLigament, secondLigament):
        firstLigamentSum = firstLigament[0] + firstLigament[1]
        secondLigamentSum = secondLigament[0] + secondLigament[1]

        if (firstLigamentSum > secondLigamentSum):
            return str(self._getLigamentIndex(firstLigament)), str(self._getLigamentIndex(secondLigament))
        else: 
            return str(self._getLigamentIndex(secondLigament)), str(self._getLigamentIndex(firstLigament))

    def getTIMatches(self):
        liveGames = json.loads(requests.get(self._liveGamesURL).text)
        data = []
        ids = set()
        matchesDataPath = os.path.join(CURR_DIR, 'matches_data', 'main_event_day_3.txt')

        with open(matchesDataPath, 'r') as fin:
            lines = fin.readlines()

            for line in lines:
                ids.add(int(line.split(';')[0]))
        
        for game in liveGames:
            if (game["league_id"] == self._tiLeagueID and not(game["match_id"] in ids)):
                matchID = game["match_id"]
                print(matchID)

                if (not(game["players"][0]["hero_id"] == 0)):
                    resultMatchData = [matchID, game["team_name_radiant"], game["team_name_dire"]]

                    print("Getting the match data...")

                    #Get ids of the teams
                    firstTeamId = game["team_id_radiant"]
                    secondTeamId = game["team_id_dire"]

                    print("Getting the heroes data of the first team...")
                    firstTeamHeroesData = self._getTeamHeroData(firstTeamId)

                    print("Getting the heroes data of the second team...")
                    secondTeamHeroesData = self._getTeamHeroData(secondTeamId)

                    firstTeamPlayerHeroDict, secondTeamPlayerHeroDict = self._getPlayersHeroesDicts(matchID, 
                        firstTeamId, game)
                    
                    print("Filling first team players-heroes data...")
                    for playerID in firstTeamPlayerHeroDict:
                        resultMatchData.append(firstTeamPlayerHeroDict[playerID])

                    print("Filling first team heroes winrate...")
                    for playerID in firstTeamPlayerHeroDict:
                        heroID = firstTeamPlayerHeroDict[playerID] 
                        resultMatchData.append(self._getTeamsHeroWinrate(heroID, firstTeamHeroesData))


                    print("Filling first players winrate against enemy heroes...")
                    for playerID in firstTeamPlayerHeroDict:
                        for enemyPlayerId in secondTeamPlayerHeroDict:
                            heroID = secondTeamPlayerHeroDict[enemyPlayerId]
                            resultMatchData.append(self._getPlayersHeroAgainstWinrate(playerID, heroID))

                    print("Filling second players winrate against enemy heroes...")
                    for playerID in secondTeamPlayerHeroDict:
                        for enemyPlayerId in firstTeamPlayerHeroDict:
                            heroID = firstTeamPlayerHeroDict[enemyPlayerId]
                            resultMatchData.append(self._getPlayersHeroAgainstWinrate(playerID, heroID))

                    print("Filling the second team heroes winrate")
                    for playerID in secondTeamPlayerHeroDict:
                        heroID = secondTeamPlayerHeroDict[playerID]
                        resultMatchData.append(self._getTeamsHeroWinrate(heroID, secondTeamHeroesData))
                                    
                    print("Filling second team players-heroes data...")
                    for playerID in secondTeamPlayerHeroDict:
                        resultMatchData.append(secondTeamPlayerHeroDict[playerID])

                    for firstPlayerID in firstTeamPlayerHeroDict:
                        firstHero = firstTeamPlayerHeroDict[firstPlayerID]
                        for secondPlayerID in secondTeamPlayerHeroDict:
                            secondHero = secondTeamPlayerHeroDict[secondPlayerID]
                            resultMatchData.append(self._getHeroesMatchUp(firstHero, secondHero))

                    with open(matchesDataPath, 'a') as fin:
                        fin.write(";".join(list(map(str, resultMatchData))) + "\n")

                    data.append(resultMatchData)
        
        return data   
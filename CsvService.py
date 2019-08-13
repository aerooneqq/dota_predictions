import csv

class CSVService:
    def __init__(self, filePath):
        self.filePath = filePath
        self.fileHeader = ["ID",  "pick_0_0", "pick_0_1", "pick_0_2", "pick_0_3", "pick_0_4",
                            "team_0_wr_hero_0", "team_0_wr_hero_1", "team_0_wr_hero_2", "team_0_wr_hero_3", "team_0_wr_hero_4",  
                            "player_wr_0_0_0", "player_wr_0_0_1", "player_wr_0_0_2", "player_wr_0_0_3", "player_wr_0_0_4",
                            "player_wr_0_1_0", "player_wr_0_1_1", "player_wr_0_1_2", "player_wr_0_1_3", "player_wr_0_1_4",
                            "player_wr_0_2_0", "player_wr_0_2_1", "player_wr_0_2_2", "player_wr_0_2_3", "player_wr_0_2_4",
                            "player_wr_0_3_0", "player_wr_0_3_1", "player_wr_0_3_2", "player_wr_0_3_3", "player_wr_0_3_4",
                            "player_wr_0_4_0", "player_wr_0_4_1", "player_wr_0_4_2", "player_wr_0_4_3", "player_wr_0_4_4",
                            "player_wr_1_0_0", "player_wr_1_0_1", "player_wr_1_0_2", "player_wr_1_0_3", "player_wr_1_0_4",
                            "player_wr_1_1_0", "player_wr_1_1_1", "player_wr_1_1_2", "player_wr_1_1_3", "player_wr_1_1_4",
                            "player_wr_1_2_0", "player_wr_1_2_1", "player_wr_1_2_2", "player_wr_1_2_3", "player_wr_1_2_4",
                            "player_wr_1_3_0", "player_wr_1_3_1", "player_wr_1_3_2", "player_wr_1_3_3", "player_wr_1_3_4",
                            "player_wr_1_4_0", "player_wr_1_4_1", "player_wr_1_4_2", "player_wr_1_4_3", "player_wr_1_4_4",
                            "team_1_wr_hero_0", "team_1_wr_hero_1", "team_1_wr_hero_2", "team_1_wr_hero_3", "team_1_wr_hero_4",
                            "pick_1_0", "pick_1_1", "pick_1_2", "pick_1_3", "pick_1_4",
                            "hero_matchup_0_0", "hero_matchup_0_1", "hero_matchup_0_2", "hero_matchup_0_3", "hero_matchup_0_4",
                            "hero_matchup_1_0", "hero_matchup_1_1", "hero_matchup_1_2", "hero_matchup_1_3", "hero_matchup_1_4",
                            "hero_matchup_2_0", "hero_matchup_2_1", "hero_matchup_2_2", "hero_matchup_2_3", "hero_matchup_2_4",
                            "hero_matchup_3_0", "hero_matchup_3_1", "hero_matchup_3_2", "hero_matchup_3_3", "hero_matchup_3_4",
                            "hero_matchup_4_0", "hero_matchup_4_1", "hero_matchup_4_2", "hero_matchup_4_3", "hero_matchup_4_4",
                            "team_0_win"]

    def prepareFile(self): 
        with open ("outputdata_new.csv", 'r') as fin, open("matchWinners_new.txt", "r") as matchFile, open("outputdata_cleared_new .csv", 'w') as fout:
            matchesIDs = set()
            matchResults = list(map(lambda x : 1 if (x == "True\n") else 0, matchFile.readlines()))

            matchesData = [self.fileHeader]

            for row in csv.reader(fin):
                if (len(row) > 0 and not(row[0] in matchesIDs)):
                    matchesIDs.add(int(row[0][:row[0].find(";")]))
                    matchesData.append(row)
            
            for i, result in enumerate(matchResults):
                matchesData[i+1][0] += ";" + str(result)

            fout.writelines(list(map(lambda x : (";".join(x)) + "\n", matchesData)))

    
    def writeToFile(self, data, mode = 'a'):
        with open(self.filePath, mode) as fout:
            csvWriter = csv.writer(fout, delimiter = ";", quotechar='"', quoting=csv.QUOTE_MINIMAL)
            csvWriter.writerow(list(map(str, data)))
    
    def readFile(self):
        data = []
        currLine = 0

        with open(self.filePath, mode = 'r') as fin:
            csvReader = csv.reader(fin)

            for row in csvReader:
                rowData = []
                for el in row:
                    rowData.append(el)
                currLine+=1
                data.append(rowData)
        
        return data, currLine

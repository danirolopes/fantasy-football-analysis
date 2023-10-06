from sleeper_wrapper import League, Players, Stats
from supabase import create_client

def getPlayerAvgProjectionsDict():
    statsFetcher = Stats()
    weekProjectionsDict = {}
    for week in range(1, 18):
        weekProjections = statsFetcher.get_week_projections("regular", 2023, week)
        for playerId, player in weekProjections.items():
            if "pts_half_ppr" in player:
                if playerId not in weekProjectionsDict:
                    weekProjectionsDict[playerId] = []
                weekProjectionsDict[playerId].append(player["pts_half_ppr"])
    
    avgProjectionDict = {}
    for playerId, projections in weekProjectionsDict.items():
        avgProjectionDict[playerId] = sum(projections) / len(projections)
    return avgProjectionDict

teamByes = {
    "ARI": 14,
    "ATL": 11,
    "BAL": 13,
    "BUF": 13,
    "CAR": 7,
    "CHI": 13,
    "CIN": 7,
    "CLE": 5,
    "DAL": 7,
    "DEN": 9,
    "DET": 9,
    "GB": 6,
    "HOU": 7,
    "IND": 11,
    "JAX": 9,
    "KC": 10,
    "LV": 13,
    "LAC": 5,
    "LAR": 10,
    "MIA": 10,
    "MIN": 13,
    "NE": 11,
    "NO": 11,
    "NYG": 13,
    "NYJ": 7,
    "PHI": 10,
    "PIT": 6,
    "SF": 9,
    "SEA": 5,
    "TB": 5,
    "TEN": 7,
    "WAS": 14,
}

def getBye(playerId):
    global players
    global teamByes
    if playerId not in players:
        print("Player not found: " + playerId)
        return False
    if "team" not in players[playerId]:
        print("Player has no team: " + playerId)
        return False
    return teamByes[players[playerId]["team"]]


def getTeamByePointsPerWeek(roster, playerPointsDict):
    byePointsPerWeek = {}
    for week in range(1, 18):
        byePointsPerWeek[week] = 0
    for playerId in roster['players']:
        if playerId in playerPointsDict:
            byePointsPerWeek[getBye(playerId)] += playerPointsDict[playerId]
    return byePointsPerWeek

def getMatchupPerWeekDict():
    global leagueFetcher
    matchupPerWeekDict = {}
    for week in range(1, 18):
        weekMatchups = leagueFetcher.get_matchups(week)
        weekMatchupsAuxDict = {}
        for matchup in weekMatchups:
            if week not in weekMatchupsAuxDict:
                weekMatchupsAuxDict[week] = {}
            if matchup['matchup_id'] not in weekMatchupsAuxDict[week]:
                weekMatchupsAuxDict[week][matchup['matchup_id']] = []
            weekMatchupsAuxDict[week][matchup['matchup_id']].append(matchup['roster_id'])

        for week, matchups in weekMatchupsAuxDict.items():
            for _, matchup in matchups.items():
                if week not in matchupPerWeekDict:
                    matchupPerWeekDict[week] = {}
                matchupPerWeekDict[week][matchup[0]] = matchup[1]
                matchupPerWeekDict[week][matchup[1]] = matchup[0]

    return matchupPerWeekDict

def calculateByeAdvantage(rosterBye, matchups):
    totalByePoints = {}
    for rosterId in rosterBye.keys():
        for week in range(1, 18):
            if rosterId not in totalByePoints:
                totalByePoints[rosterId] = 0
            totalByePoints[rosterId] += rosterBye[matchups[week][rosterId]][week]
    return totalByePoints

def rosterToTeamNameDict():
    global leagueFetcher
    teamNameDict = {}
    rostersResp = leagueFetcher.get_rosters()
    ownersResp = leagueFetcher.get_users()
    ownersDict = {}
    for owner in ownersResp:
        ownersDict[owner['user_id']] = owner['metadata']['team_name'] 
    for roster in rostersResp:
        teamNameDict[roster['roster_id']] = ownersDict[roster['owner_id']]
    return teamNameDict

def sendDataToAnalysis(byeAdvantage):
    global leagueId
    global supabase_url
    global supabase_anon_key
    supabase = create_client(supabase_url, supabase_anon_key)
    data = []
    for rosterId, byePoints in byeAdvantage.items():
        data.append({"league_id": leagueId, "team_id": rosterId, "bye_advantage": byePoints})
    try:
        success = supabase.table("team").insert(data).execute()
        if not success:
            print("Error sending data to analysis")
    except:
        print("Error sending data to analysis")

    

leagueId = ""
supabase_url = "https://mmqujmwyrmtujizatbkl.supabase.co"
supabase_anon_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1tcXVqbXd5cm10dWppemF0YmtsIiwicm9sZSI6ImFub24iLCJpYXQiOjE2OTI1MTAxOTQsImV4cCI6MjAwODA4NjE5NH0.ePpDdJLqQBGiHI0VH-jTnwzUMb7d6_JAfg_6nsBOtnU"

if __name__ == "__main__":
    print("Welcome to the Bye Advantage Calculator!\n")
    print("This tool will calculate the Bye Advantage for each team in your league")
    print("The Bye Advantage is the total points scored by the oponent players that are on bye weeks\n")
    print("The HIGHER the Bye Advantage, the LUCKIER you are with byes. The LOWER, the UNLUCKIER\n")
    leagueId = input("Type your Sleeper LeagueID: ")
    try:
        leagueFetcher = League(leagueId)
    except:
        print("Invalid LeagueID")
        exit()

    canSendAnalytics = input("Do you want to share anonymous results for further analysis that will be posted on reddit? (y/n): ") == "y"
    print("\nCalculating... (Might take some minutes)\n")
    
    playersFetcher = Players()
    players = playersFetcher.get_all_players()

    playerAvgProjectionsDict = getPlayerAvgProjectionsDict()
    rostersResp = leagueFetcher.get_rosters()

    rosterBye = {}
    for roster in rostersResp:
        rosterBye[roster['roster_id']] = getTeamByePointsPerWeek(roster, playerAvgProjectionsDict)

    matchups = getMatchupPerWeekDict()
    totalByePoints = calculateByeAdvantage(rosterBye, matchups)

    rosterToTeamName = rosterToTeamNameDict()

    for rosterId, points in totalByePoints.items():
        print(rosterToTeamName[rosterId] + ": " + "{:.1f}".format(points))
    print("\n")
    if canSendAnalytics:
        sendDataToAnalysis(totalByePoints)


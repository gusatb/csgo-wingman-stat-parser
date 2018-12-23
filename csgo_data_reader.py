filename = "csgo_wingman_data"
with open(filename) as f:
    content = f.readlines()


class Player:
    def __init__(self):
        self.name = None
        self.ping = None
        self.kills = None
        self.assists = None
        self.deaths = None
        self.stars = 0
        self.hsp = 0
        self.score = None
        self.team = None

    def __str__(self):
        return "{}: {}, {}, {}, {}, {}, {}, {}, {}".format(self.name, self.ping, self.kills, self.assists, self.deaths, self.stars, self.hsp, self.score, self.team)


class Match:
    def __init__(self):
        self.map = None
        self.date = None
        self.wait = None # in seconds
        self.duration = None
        self.score = None
        self.players = []

    def __str__(self):
        playersString = ""
        for player in self.players:
            playersString += player.__str__() + ", "
        playersString = playersString[:-2]
        return "{}, {}, {}, {}, {}, [{}]".format(self.map, self.date, self.wait, self.duration, self.score, playersString)


matches = []
currentMatch = None
currentPlayer = Player()
lastLine = None
player_parse_state = -1
for line in content:
    if player_parse_state == -1:
        if line.startswith("Wingman"):
            if currentMatch:
                matches.append(currentMatch)
            currentMatch = Match()
            currentMatch.map = line[8:-1]
        elif line[-4:-1] == "GMT":
            currentMatch.date = line[:-1]
        elif line.startswith("Wait"):
            currentMatch.wait = int(line[-6:-4]) * 60 + int(line[-3:-1])
        elif line.startswith("Match"):
            currentMatch.duration = int(line[-6:-4]) * 60 + int(line[-3:-1])
        elif line.startswith("Player"):
            player_parse_state = 0
    elif player_parse_state >= 0:
        if len(line) > 3 and line[2] == ":":
            currentMatch.score = (int(line[0]), int(line[4]))
        elif line.count("\t") == 6:
            currentPlayer.name = lastLine[:-1]
            currentPlayer.team = player_parse_state / 2
            stats = line.split()
            currentPlayer.ping = int(stats[0])
            currentPlayer.kills = int(stats[1])
            currentPlayer.assists = int(stats[2])
            currentPlayer.deaths = int(stats[3])
            lastStats = stats[4:]
            if lastStats and ord(lastStats[0][0]) > 127:
                if len(lastStats[0]) == 3:
                    currentPlayer.stars = 1
                else:
                    currentPlayer.stars = int(lastStats[0][3])
                lastStats.pop(0)
            if lastStats and len(lastStats) >= 1 and lastStats[0][-1] == "%":
                currentPlayer.hsp = int(lastStats[0][:-1])
                lastStats.pop(0)
            currentPlayer.score = int(lastStats[0])
            currentMatch.players.append(currentPlayer)
            currentPlayer = Player()
            player_parse_state += 1
            if player_parse_state == 4:
                player_parse_state = -1
    lastLine = line

matches.append(currentMatch)

unique_matches = {}

for match in matches:
    matchString = match.__str__()
    unique_matches[matchString] = match

matches = []

for k, v in unique_matches.iteritems():
    matches.append(v)

gus_name = "Acid The Bear"
aaron_name = "Bird Up"

gus_hsp = 0
gus_kills = 0
gus_deaths = 0
gus_map_kd = {}
aaron_hsp = 0
aaron_kills = 0
aaron_deaths = 0
aaron_map_kd = {}

both_matches = 0

maps_played = {}
maps_team_wl = {}

enemies_played = {}

perfect_wins = 0
perfect_losses = 0

wins = 0
losses = 0

for match in matches:
    gus_player = None
    aaron_player = None
    for player in match.players:
        if player.name == gus_name:
            gus_player = player
        elif player.name == aaron_name:
            aaron_player = player
    if gus_player is not None and aaron_player is not None:
        winning_team = 0 if match.score[0] > match.score[1] else 1
        wl_add_index = 0 if gus_player.team == winning_team else 1
        if match.score[0] == match.score[1]:
            wl_add_index = -1
        if  wl_add_index == 0:
            wins += 1
        elif wl_add_index == 1:
            losses += 1
        if 0 in match.score:
            if wl_add_index == 0:
                perfect_wins += 1
            elif wl_add_index == 1:
                perfect_losses += 1
        if match.map in maps_played:
            maps_played[match.map] += 1
        else:
            maps_played[match.map] = 0
            maps_team_wl[match.map] = [0, 0]
            gus_map_kd[match.map] = [0, 0]
            aaron_map_kd[match.map] = [0, 0]
        for player in match.players:
            if player.team != gus_player.team:
                if player.name in enemies_played:
                    enemies_played[player.name].append(match)
                else:
                    enemies_played[player.name] = [match]
        if match.score[0] != match.score[1] and wl_add_index != -1:
            maps_team_wl[match.map][wl_add_index] += 1
        gus_map_kd[match.map][0] += gus_player.kills
        gus_map_kd[match.map][1] += gus_player.deaths
        aaron_map_kd[match.map][0] += aaron_player.kills
        aaron_map_kd[match.map][1] += aaron_player.deaths
        both_matches += 1
        gus_hsp += gus_player.hsp
        gus_kills += gus_player.kills
        gus_deaths += gus_player.deaths
        aaron_hsp += aaron_player.hsp
        aaron_kills += aaron_player.kills
        aaron_deaths += aaron_player.deaths

print(gus_kills*1.0/both_matches, gus_deaths*1.0/both_matches, gus_kills*1.0/gus_deaths, gus_hsp*1.0/both_matches)
print(aaron_kills*1.0/both_matches, aaron_deaths*1.0/both_matches, aaron_kills*1.0/aaron_deaths, aaron_hsp*1.0/both_matches)

print(maps_played)
for k, v in gus_map_kd.iteritems():
    print("{}: {}".format(k, v[0]*1.0/v[1]))
for k, v in aaron_map_kd.iteritems():
    print("{}: {}".format(k, v[0]*1.0/v[1]))

print(both_matches)

for enemy_name, matches in enemies_played.iteritems():
    if len(matches) >= 2:
        print(enemy_name)
        for match in matches:
            print(match)
            print("")

print(perfect_wins, perfect_losses)
print(maps_team_wl)
print(wins, losses)

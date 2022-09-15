import json
import pandas as pd
import newTeamInput
import sys
from dataManage import playersData
import random
import optimization
from copy import deepcopy


class team:
    
    def __init__(self, name, players) -> None:
        self.name = name
        self.players = players
        self.playerAttributes = deepcopy({key : playersData[key] for key in self.players[self.name]})
        self.bowlingOrder = []
        self.wins = 0
        self.matchStats = {}

        for pl in self.players[self.name]:
            self.matchStats[pl] = {'runs' : 0, 'balls' : 0, 'out' : 'DNB', 'overs' : 0, 'ball': 0.0, 'runs_given' : 0, 'wkts' : 0, '4s' : 0, '6s' : 0, 'MVP':0.0}

    def attrUpdate(self):
        if pitch['pace'] == 1.0:
            # print('no change')
            pass
        elif pitch['pace'] > 1.0:
            p1 = pitch['pace']
            p2 = 1 + ((p1-1)/2)
            for pl in self.playerAttributes.keys():
                if self.playerAttributes[pl].get('role', None) == 'FAST':
                    # print(pl)
                    self.playerAttributes[pl]['bowl']['pp']['wkt'] = round(self.playerAttributes[pl]['bowl']['pp']['wkt']*p1, 4)
                    self.playerAttributes[pl]['bowl']['mid']['wkt'] = round(self.playerAttributes[pl]['bowl']['mid']['wkt']*p2, 4)
                elif self.playerAttributes[pl].get('role', None) == 'MEDIUM':
                    # print(pl)
                    self.playerAttributes[pl]['bowl']['pp']['wkt'] = round(self.playerAttributes[pl]['bowl']['pp']['wkt']*p2, 4)
                    self.playerAttributes[pl]['bowl']['mid']['wkt'] = round(self.playerAttributes[pl]['bowl']['mid']['wkt']*p2, 4)
        elif pitch['pace'] < 1.0:
            p3 = pitch['pace']
            for pl in self.playerAttributes.keys():
                if ((self.playerAttributes[pl].get('role', None) == 'FAST') or (self.playerAttributes[pl].get('role', None) == 'MEDIUM')):
                    # print(pl)
                    self.playerAttributes[pl]['bowl']['pp']['wkt'] = round(self.playerAttributes[pl]['bowl']['pp']['wkt']*p3, 4)
                    self.playerAttributes[pl]['bowl']['mid']['wkt'] = round(self.playerAttributes[pl]['bowl']['mid']['wkt']*p3, 4)
        
        if pitch['spin'] == 1.0:
            # print('no change')
            pass
        elif pitch['spin'] > 1.0:
            s1 = pitch['spin']
            s2 = 1 + ((s1-1)/2)
            for pl in self.playerAttributes.keys():
                # print(pl)
                # print()
                if self.playerAttributes[pl].get('role', None) == 'SPIN':
                    # print(pl)
                    self.playerAttributes[pl]['bowl']['pp']['wkt'] = round(self.playerAttributes[pl]['bowl']['pp']['wkt']*s2, 4)
                    self.playerAttributes[pl]['bowl']['mid']['wkt'] = round(self.playerAttributes[pl]['bowl']['mid']['wkt']*s1, 4)
                elif self.playerAttributes[pl].get('role', None) == 'PARTSPIN':
                    # print(pl)
                    self.playerAttributes[pl]['bowl']['pp']['wkt'] = round(self.playerAttributes[pl]['bowl']['pp']['wkt']*s2, 4)
                    self.playerAttributes[pl]['bowl']['mid']['wkt'] = round(self.playerAttributes[pl]['bowl']['mid']['wkt']*s2, 4)
        elif pitch['spin'] < 1.0:
            s3 = pitch['spin']
            for pl in self.playerAttributes.keys():
                if ((self.playerAttributes[pl].get('role', None) == 'SPIN') or (self.playerAttributes[pl].get('role', None) == 'PARTSPIN')):
                    self.playerAttributes[pl]['bowl']['pp']['wkt'] = round(self.playerAttributes[pl]['bowl']['pp']['wkt']*s3, 4)
                    self.playerAttributes[pl]['bowl']['mid']['wkt'] = round(self.playerAttributes[pl]['bowl']['mid']['wkt']*s3, 4)
                    self.playerAttributes[pl]['bowl']['death']['wkt'] = round(self.playerAttributes[pl]['bowl']['death']['wkt']*s3, 4)
        
    def __repr__(self) -> str:
        pass

def avg(*a):
    return round(sum(a)/len(a), 4)

class matchStatus:
    def __init__(self, team1, team2, target) -> None:
        self.team1 = team1
        self.team2 = team2

        self.inn = 1
        self.score = 0
        self.wickets = 0
        self.overs = 0
        self.target = target
        self.phase = 'pp'
        self.ball = 0.1
        self.pitch = pitch
        self.freeHit = False
        self.extras = 0

        self.onStrike = team1.players[team1.name][0]
        self.offStrike = team1.players[team1.name][1]

        self.team1.matchStats[self.onStrike]['out'] = 'Not Out'
        self.team1.matchStats[self.offStrike]['out'] = 'Not Out'

        self.draws = draws

    @property
    def bowler(self):
        return self.team2.bowlingOrder[self.overs]
    
    @property
    def balls(self):
        return (self.overs*6 + (self.ball-0.1)*10)

    @property
    def sp_death(self):
        if self.phase != 'death':
            return 1
        elif ((self.team2.playerAttributes[self.bowler].get('role', None) != 'SPIN') and (self.team2.playerAttributes[self.bowler].get('role', None) != 'PARTSPIN')):
            return 1
        else:
            k = 0.35 * (self.overs - 16)
            return k

    @property
    def agg(self):
        b = self.balls
        for pl in self.team1.players[self.team1.name][self.wickets+2:]:
            b += 1/self.team1.playerAttributes[pl]['bat'][self.phase]['wkt']
        if self.inn == 2:
            if self.overs >= 10 and self.overs < 20:
                if self.score>0:
                    rr = (((self.target - self.score)/(120 - self.balls))/(self.score/self.balls))
                else:
                    rr = self.target/(120 - self.balls)
            else:
                rr = 1
        else:
            rr =1
        if rr == 0:
            rr = 1
        return round(rr * (b/120), 4)
    
    @property
    def set_factor(self):
        batter = self.onStrike
        ph = self.phase
        bls = self.team1.matchStats[batter]['balls']
        ph_sr = self.team1.playerAttributes[batter]['bat'][ph]['sr']
        if bls >= 40:
            sf = max(self.team1.playerAttributes[batter]['bat']['SRper10Balls'][-1], ph_sr)
        else:
            idx = bls//10
            if ((ph == 'death') and (self.team1.playerAttributes[batter]['bat'].get('PF', None))):
                sf = max(self.team1.playerAttributes[batter]['bat']['SRper10Balls'][idx], self.team1.playerAttributes[batter]['bat']['SRper10Ballsdeath'][idx])
            else:
                sf = self.team1.playerAttributes[batter]['bat']['SRper10Balls'][idx]
        r = round(sf/ph_sr, 4)
        if r == 0:
            r == 1
        return r

    def scorecard(self):
        bat_str = '\nInnings {}\n'.format(self.inn)
        bat_str += '\nBatting Scorecard\n'
        bat_str += '{:^20}\t\tRuns Balls\n'.format(self.team1.name)
        for pl in self.team1.matchStats.keys():
            batter = self.team1.matchStats[pl]
            bat_str += '{:^20}{:^10} {:^4}({:^4})\n'.format(pl, batter['out'], batter['runs'], batter['balls'])
        bat_str += 'Extras : {}\n\n'.format(self.extras)
        bowl_str = 'Bowling Scorecard\n'
        bowl_str += '{:^20}\tOvers\tRuns\tWickets\n'.format(self.team2.name)
        for pl in self.team2.matchStats.keys():
            bowler = self.team2.matchStats[pl]
            ovrs = bowler['overs'] + bowler['ball']
            if ovrs > 0.0:
                bowl_str += '{:^20}\t{:^5}\t{:^4}\t{:^7}\n'.format(pl, ovrs, bowler['runs_given'], bowler['wkts'])
        bowl_str += '\n'
        return (bat_str + bowl_str)

    def __repr__(self) -> str:
        if self.inn <= 1:
            return ('{}\t{}/{}\tin\t{} overs'.format(self.team1.name, self.score, self.wickets, self.overs))
        else:
            return ('{}\t{}/{}\tin\t{} overs \tTARGET : {}'.format(self.team1.name, self.score, self.wickets, self.overs, self.target))

    def secondInn(self):
        self.inn = 2

    def endInn(self):
        if (self.overs == 20 or self.wickets == 10 or (self.inn == 2 and self.score >= self.target)):
            return True

    def ballOutCome(self):

        outcomes = ['wide', 'noball', 'wkt', '0', '1', '2', '3', '4', '6']

        zero_f = self.agg
        if self.phase == 'death':
            zero_f = max(self.agg, 1) 
        #print(self.team2.playerAttributes[self.bowler]['bowl'][self.phase])
        wide = self.team2.playerAttributes[self.bowler]['bowl'][self.phase]['wide']
        noball = self.team2.playerAttributes[self.bowler]['bowl'][self.phase]['noball']
        wkt = avg(self.team2.playerAttributes[self.bowler]['bowl'][self.phase]['wkt'], self.team1.playerAttributes[self.onStrike]['bat'][self.phase]['wkt'] * self.agg)
        zero = avg(self.team2.playerAttributes[self.bowler]['bowl'][self.phase]['0'], self.team1.playerAttributes[self.onStrike]['bat'][self.phase]['0']*(1/zero_f))
        one = avg(self.team2.playerAttributes[self.bowler]['bowl'][self.phase]['1'], self.team1.playerAttributes[self.onStrike]['bat'][self.phase]['1']*(1/self.agg))
        two = avg(self.team2.playerAttributes[self.bowler]['bowl'][self.phase]['2'], self.team1.playerAttributes[self.onStrike]['bat'][self.phase]['2']*self.agg*self.set_factor)
        three = avg(self.team2.playerAttributes[self.bowler]['bowl'][self.phase]['3'], self.team1.playerAttributes[self.onStrike]['bat'][self.phase]['3'])
        four = avg(self.team2.playerAttributes[self.bowler]['bowl'][self.phase]['4'], self.team1.playerAttributes[self.onStrike]['bat'][self.phase]['4']*pitch['flat']*self.agg*self.set_factor)
        six = avg(self.team2.playerAttributes[self.bowler]['bowl'][self.phase]['6']*self.sp_death, self.team1.playerAttributes[self.onStrike]['bat'][self.phase]['6']*pitch['flat']*self.agg*self.set_factor)

        weight = [wide, noball, wkt, zero, one, two, three, four, six]
        
        oc = random.choices(outcomes, weight)[0]

        if oc == 'wide':
            self.score += 1
            self.team2.matchStats[self.bowler]['runs_given'] += 1
            self.extras += 1
            print(oc)
            return oc
        elif oc == 'noball':
            self.score += 1
            self.team2.matchStats[self.bowler]['runs_given'] += 1
            self.team1.matchStats[self.onStrike]['balls'] += 1
            self.extras += 1
            self.freeHit = True
            vc = random.choices(outcomes[2:], weight[2:])[0]
            if vc == 'wkt':
                vc = '0'
            print(vc+'nb')
            self.update(int(vc), validBall=False)
            if vc == '1' or vc == '3':
                self.changeStrike()
            return (vc+'nb')
        else:
            if oc != 'wkt':
                print(oc)
                self.update(int(oc))
                if oc == '1' or oc == '3':
                    self.changeStrike()
            return oc


    def update(self, runs, validBall=True, wkt=False):
        global phs_str
        self.score += runs
        self.team2.matchStats[self.bowler]['runs_given'] += runs
        self.team1.matchStats[self.onStrike]['runs'] += runs
        if validBall:
            self.freeHit = False
            self.ball += 0.1
            self.team2.matchStats[self.bowler]['ball'] += 0.1
            if wkt == False:
                self.team1.matchStats[self.onStrike]['balls'] += 1
            if runs == 0:
                if self.phase == 'pp':
                    self.team2.matchStats[self.bowler]['MVP'] += 0.5
                else:
                    self.team2.matchStats[self.bowler]['MVP'] += 1
            if runs == 4:
                self.team1.matchStats[self.onStrike]['4s'] += 1
                self.team1.matchStats[self.onStrike]['MVP'] += 2.5
            if runs == 6:
                self.team1.matchStats[self.onStrike]['6s'] += 1
                self.team1.matchStats[self.onStrike]['MVP'] += 3.5
            if self.ball == 0.7:
                self.team2.matchStats[self.bowler]['ball'] = 0.0
                self.team2.matchStats[self.bowler]['overs'] += 1
                self.overs += 1
                self.ball = 0.1
                print()
                if self.phaseCheck():
                    phs_str += '\n'
                    phs_str += self.__repr__()
                    phs_str += '\n'
                    print(self,'\n')
                self.changeStrike()

    def phaseCheck(self):
        ph = self.phase
        if self.overs < 6:
            self.phase = 'pp'
        elif self.overs < 16:
            self.phase = 'mid'
        else:
            self.phase = 'death'
        if ph != self.phase:
            return True
        return False

    def winnerCheck(self):
        if self.score >= self.target:
            self.team1.wins += 1
            res = "\n{} beat {} by {} wickets with {} balls remaining.\n".format(self.team1.name, self.team2.name, (10 - self.wickets), int((121 - (6 * self.overs + 10 * self.ball))))
        elif self.score < (self.target-1):
            self.team2.wins += 1
            res = "\n{} beat {} by {} runs.\n".format(self.team2.name, self.team1.name, (self.target - (self.score + 1)))
        else:
            res ='\nGame DRAW.\n'
            self.draws = self.draws + 1
        return res

    def changeStrike(self):
        self.onStrike, self.offStrike = self.offStrike, self.onStrike

class seriesStats:
    def __init__(self, t1, t2) -> None:
        self.sStats = {t1.name:{}, t2.name:{}}
        for pl in t1.players[t1.name]:
            self.sStats[t1.name][pl] = {'runs' : 0, 'balls' : 0, 'outs' : 0, 'balls_bowled': 0.0, 'runs_given' : 0, 'wkts' : 0, '4s' : 0, '6s' : 0, '50+':0, '100+':0, 'best_score':0, '3wkt+':0,'5wkt+':0, 'BBI_wkt':0, 'BBI_runs':0, 'MVP':0.0}
        for pl in t2.players[t2.name]:
            self.sStats[t2.name][pl] = {'runs' : 0, 'balls' : 0, 'outs' : 0, 'balls_bowled': 0.0, 'runs_given' : 0, 'wkts' : 0, '4s' : 0, '6s' : 0, '50+':0, '100+':0, 'best_score':0, '3wkt+':0,'5wkt+':0, 'BBI_wkt':0, 'BBI_runs':0, 'MVP':0.0}
    
    def update_Stats(self, ta, tb):
        for t1 in [ta, tb]:
            for pl in t1.matchStats.keys():
                runs = t1.matchStats[pl]['runs']
                wkts = t1.matchStats[pl]['wkts']
                self.sStats[t1.name][pl]['runs'] += runs
                self.sStats[t1.name][pl]['balls'] += t1.matchStats[pl]['balls']
                self.sStats[t1.name][pl]['balls_bowled'] = self.sStats[t1.name][pl]['balls_bowled'] + t1.matchStats[pl]['ball']*10 + t1.matchStats[pl]['overs']*6
                self.sStats[t1.name][pl]['runs_given'] += t1.matchStats[pl]['runs_given']
                self.sStats[t1.name][pl]['wkts'] += wkts
                self.sStats[t1.name][pl]['4s'] += t1.matchStats[pl]['4s']
                self.sStats[t1.name][pl]['6s'] += t1.matchStats[pl]['6s']
                self.sStats[t1.name][pl]['MVP'] += t1.matchStats[pl]['MVP']
                self.sStats[t1.name][pl]['MVP'] += runs*0.1
                if t1.matchStats[pl]['out'] == 'OUT':
                    self.sStats[t1.name][pl]['outs'] += 1
                if runs >= 50:
                    self.sStats[t1.name][pl]['50+'] += 1
                    if runs >= 100:
                        self.sStats[t1.name][pl]['100+'] += 1
                if runs > self.sStats[t1.name][pl]['best_score']:
                    self.sStats[t1.name][pl]['best_score'] = runs
                if wkts >= 3:
                    self.sStats[t1.name][pl]['3wkt+'] += 1
                    if wkts >= 5:
                        self.sStats[t1.name][pl]['5wkt+'] += 1
                if wkts > self.sStats[t1.name][pl]['BBI_wkt']:
                    self.sStats[t1.name][pl]['BBI_wkt'] = wkts
                    self.sStats[t1.name][pl]['BBI_runs'] = t1.matchStats[pl]['runs_given']
                elif wkts == self.sStats[t1.name][pl]['BBI_wkt']:
                    self.sStats[t1.name][pl]['BBI_runs'] = min(t1.matchStats[pl]['runs_given'], self.sStats[t1.name][pl]['BBI_runs'])
                    
    def covert(self, tA, tB):
        statsDF = pd.DataFrame({'Team':pd.Series([], dtype='str'), 'Name':pd.Series([], dtype='str'),
                                'Runs':pd.Series([], dtype='int'), 'Balls_faced':pd.Series([], dtype='int'),
                                'outs':pd.Series([], dtype='int'), 'Best':pd.Series([], dtype='int'),
                                '50+':pd.Series([], dtype='int'), '100+':pd.Series([], dtype='int'),
                                '4s':pd.Series([], dtype='int'), '6s':pd.Series([], dtype='int'),
                                'Balls_Bowled':pd.Series([], dtype='int'), 'Wickets':pd.Series([], dtype='int'),
                                'Runs_given':pd.Series([], dtype='int'), 'BBI':pd.Series([], dtype='str'),
                                '3wkt+':pd.Series([], dtype='int'), '5wkt+':pd.Series([], dtype='int'),
                                'MVP':pd.Series([], dtype='float')
                                })
        for t in self.sStats.keys():
            for name in self.sStats[t].keys():
                pl = self.sStats[t][name]
                bbi = '{} for {}'.format(pl['BBI_wkt'], pl['BBI_runs'])
                statsDF.loc[len(statsDF)] = [t, playersData[name]['name'], pl['runs'], pl['balls'], pl['outs'], pl['best_score'],
                                            pl['50+'], pl['100+'], pl['4s'], pl['6s'], pl['balls_bowled'], 
                                            pl['wkts'], pl['runs_given'], bbi, pl['3wkt+'], pl['5wkt+'], pl['MVP']]
        statsDF['Bat_Avg'] = statsDF['Runs']/statsDF['outs']
        statsDF['Bat_SR'] = statsDF['Runs']/statsDF['Balls_faced']*100
        statsDF['Bowl_Avg'] = statsDF['Runs_given']/statsDF['Wickets']
        statsDF['Bowl_SR'] = statsDF['Balls_Bowled']/statsDF['Wickets']
        statsDF['Eco'] = statsDF['Runs_given']/statsDF['Balls_Bowled']*6 

        statsDF = statsDF.round(2)

        file_name = 'seriesStats/allStats' 
        # file_name = 'seriesStats/allStats_{}-vs-{}'.format(tA.name, tB.name)
        
        statsDF.to_csv(file_name+'.csv')

        statsDF = statsDF.iloc[:,[0, 1, 16, 17, 18, 19, 20, 21, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14 , 15]]
        
        return statsDF

def getNewTeam():
    n1 = input('\nEnter the name of new team:\n')
    print()
    l1 = newTeamInput.main()
    if ((len(l1) == 11) and n1):
        p1 = {n1 : l1}
        t1 = team(n1, p1)
    else:
        print('Team Input closed abruptly.\n')
        r = input('Press "r" to retry OR any other key to close.\n')
        if r.lower() == 'r':
            t1 = getNewTeam()
        else:
            sys.exit()
    return t1

def loadTeam(dictteams):
    teamkeyFound = False
    while(teamkeyFound == False):
        print(list(dictteams.keys()))
        nameA = input('Enter the name of the team, you wish to load\n')
        if nameA in dictteams.keys():
            tA = team(nameA, {nameA : dictteams[nameA]})
            teamkeyFound = True
        else:
            print('Such team name doesnt exist. Check for case sensitive.\n')
    return tA

def pitchChange():
    while(True):
            p = float(input('\nHow much should pitch help pace?\nEnter from 0.5 to 2.0 with 0.5 being least helpful.\n'))
            if((p >= 0.5 and (p <= 2.0))):
                pitch['pace'] = p
                break
            else:
                print("WRONG INPUT. ENTER a value between 0.5 to 2.0.")
        
    while(True):
        s = float(input('\nHow much should pitch help spin?\nEnter from 0.5 to 2.0 with 0.5 being least helpful.\n'))
        if((s >= 0.5 and (s <= 2.0))):
            pitch['spin'] = s
            break
        else:
            print("WRONG INPUT. ENTER a value between 0.5 to 2.0.")
    
    while(True):
        f = float(input('\nHow much should pitch help batters aka Flatness of the pitch?\nEnter from 0.5 to 2.0 with 0.5 being least helpful.\n'))
        if((f >= 0.5 and (f <= 2.0))):
            pitch['flat'] = f
            break
        else:
            print("WRONG INPUT. ENTER a value between 0.5 to 2.0.")


def main():

    global draws
    draws = 0

    global pitch
    pitch = {'pace' : 1.0, 'spin' : 1.0, 'flat' : 1.0}
    if (input("Would you like to change conditions?\nType 'y' for yes and ANY key for no\n") == 'y'):
        pitchChange()

    print(pitch)

    teamtype = input("\nPress 'n' for new team OR 'l' or any key for load team\t")

    with open('customteams.txt', 'r') as fp:
        dictteams = json.load(fp)
    
    if teamtype.lower() == 'n':
        teamA = getNewTeam()
    else:
        teamA = loadTeam(dictteams)

    print(teamA.players)
    print()

    teamtype = input("Press 'n' for new team OR 'l' or any key for load team\t")

    if teamtype.lower() == 'n':
        teamB = getNewTeam()
    else:
        teamB = loadTeam(dictteams)

    print(teamB.players)
    print()

    s1 = seriesStats(teamA, teamB)

    global phs_str
    phs_str = ''

    dictteams[teamA.name] = teamA.players[teamA.name]

    dictteams[teamB.name] = teamB.players[teamB.name]

    teamA.attrUpdate()
    teamB.attrUpdate()

    teamA.bowlingOrder = optimization.main(teamA.playerAttributes)
    print('\n',teamA.name,'Bowling Order:',teamA.bowlingOrder)
    teamB.bowlingOrder = optimization.main(teamB.playerAttributes)
    print('\n',teamB.name,'Bowling Order:',teamB.bowlingOrder)

    with open('extractedData/customTeams.json', 'w') as fp:
        json.dump(dictteams, fp)

    with open('extractedData/customTeams.json', 'r') as fp:
        customTeams = json.load(fp)
    
    with open('customteams.txt', 'w') as f:
        f.writelines(json.dumps(customTeams, indent = 2))

    matches = int(input('\nEnter the number of matches:\n'))

    final_str = ''
    targets = 0
    tossA = 0
    tossB = 0

    for match in range(1, matches+1):

        match_str = ''
        phs_str = ''

        print('\nMatch Number {} of the series.'.format(match))
        final_str += 'Match No #{}\n'.format(match)

        toss = random.choice([teamA.name, teamB.name])
        if toss == teamA.name:
            tossA += 1 
        else:
            tossB = tossB + 1
        choose = random.choices(['bat', 'bowl'], [35, 65])[0]
        print('\n{} won the toss and decide to {} first.\n'.format(toss, choose))
        if ((toss == teamA.name and choose == 'bat') or (toss == teamB.name and choose =='bowl')):
            t1 = teamA
            t2 = teamB
        else:
            t1 = teamB
            t2 = teamA
        
        match_str += '\nMatch Number {} of the series.\n\n{} vs {}\n'.format(match, teamA.name, teamB.name)
        match_str += '\n{}\n'.format(pitch)
        match_str += '\n{} won the toss and decide to {} first.\n'.format(toss, choose)
        match_str += '\n{}\n'.format(teamA.players)
        match_str +=  '\n{}\n'.format(teamB.players)
        
        print(teamA.players)
        print()
        print(teamB.players)
        print()
        print(pitch,'\n')

        for ts in [teamA, teamB]:
            for pl in ts.players[ts.name]:
                ts.matchStats[pl]['runs'] = 0
                ts.matchStats[pl]['balls'] = 0
                ts.matchStats[pl]['out'] = 'DNB'
                ts.matchStats[pl]['overs'] = 0
                ts.matchStats[pl]['ball'] = 0.0
                ts.matchStats[pl]['runs_given'] = 0
                ts.matchStats[pl]['wkts'] = 0
                ts.matchStats[pl]['MVP'] = 0.0
                ts.matchStats[pl]['4s'] = 0
                ts.matchStats[pl]['6s'] = 0
        
        firstInnings = matchStatus(t1, t2, None)
        print('First Innings Begins\n')

        while(not(firstInnings.endInn())):
            print('{:^6.1f}  {:^20} to {:^20}\t'.format(firstInnings.overs+firstInnings.ball, firstInnings.bowler, firstInnings.onStrike),end='')
            outcome = firstInnings.ballOutCome()
            if outcome == 'wkt':
                if firstInnings.freeHit == False:
                    print(outcome)
                    firstInnings.wickets += 1
                    firstInnings.team2.matchStats[firstInnings.bowler]['wkts'] += 1
                    firstInnings.team2.matchStats[firstInnings.bowler]['MVP'] += 2.5
                    firstInnings.team1.matchStats[firstInnings.onStrike]['out'] = 'OUT'
                    firstInnings.team1.matchStats[firstInnings.onStrike]['balls'] += 1

                    if firstInnings.wickets != 10:
                        firstInnings.onStrike = firstInnings.team1.players[firstInnings.team1.name][firstInnings.wickets+1]
                        firstInnings.team1.matchStats[firstInnings.onStrike]['out'] = 'Not Out'
                    firstInnings.update(0, wkt=True)
                else:
                    print('0')
                    firstInnings.update(0)

        fs = firstInnings.scorecard()
        print(fs)
        print(firstInnings)
        print()

        match_str += fs
        match_str += '\n'
        match_str += firstInnings.__repr__()
        match_str += '\n\n' 

        Target = firstInnings.score + 1

        match_str += 'Target - {}\n\n'.format(Target)

        targets += Target

        secondInnings = matchStatus(t2, t1, Target)

        secondInnings.secondInn()
        print('Second Innings Begins\n')

        while(not(secondInnings.endInn())):
            print('{:^6.1f}  {:^20} to {:^20}\t'.format(secondInnings.overs+secondInnings.ball, secondInnings.bowler, secondInnings.onStrike),end='')
            outcome = secondInnings.ballOutCome()
            if outcome == 'wkt':
                if secondInnings.freeHit == False:
                    print('wkt')
                    secondInnings.wickets += 1
                    secondInnings.team2.matchStats[secondInnings.bowler]['wkts'] += 1
                    secondInnings.team2.matchStats[secondInnings.bowler]['MVP'] += 2.5
                    secondInnings.team1.matchStats[secondInnings.onStrike]['out'] = 'OUT'
                    secondInnings.team1.matchStats[secondInnings.onStrike]['balls'] += 1

                    if secondInnings.wickets != 10:
                        secondInnings.onStrike = secondInnings.team1.players[secondInnings.team1.name][secondInnings.wickets+1]
                        secondInnings.team1.matchStats[secondInnings.onStrike]['out'] = 'Not Out'
                    secondInnings.update(0, wkt=True)
                else:
                    print('0')
                    secondInnings.update(0)

        ss = secondInnings.scorecard()
        print(ss)
        print(secondInnings,'\n')

        match_str += ss
        match_str += '\n'
        match_str += secondInnings.__repr__()
        match_str += '\n\n'

        final_str += firstInnings.__repr__()
        final_str += '\n'
        final_str += secondInnings.__repr__()
        result = secondInnings.winnerCheck()
        final_str += result
        final_str += '\n'

        match_str += '\n'
        match_str += result
        match_str += '\n\n'

        match_str += phs_str

        draws = secondInnings.draws

        print(result)

        print(f'\n{teamA.name}  {teamA.wins} \t {teamB.name}  {teamB.wins} \t Draws  {draws}\n')

        s1.update_Stats(teamA, teamB)

        stm = str(match)
        with open('seriesStats/Scorecard'+stm+'.txt', 'w') as f:
            f.writelines(match_str)

    stats = s1.covert(teamA, teamB)

    final_str += (f'\n{teamA.name}  {teamA.wins} \t {teamB.name}  {teamB.wins} \t Draws {draws}\n\n')

    with open('seriesStats/Results.txt', 'w') as f:
        f.writelines(final_str)

    # with open('seriesStats/Results_'+teamA.name+'-vs-'+teamB.name+'.txt', 'w') as f:
    #     f.writelines(final_str)

    print(final_str)

    most_runs = stats.sort_values(by = ['Runs', 'Bat_SR'], ascending = [False, False], ignore_index=True).iloc[0]
    most_wkts = stats.sort_values(by = ['Wickets', 'Bowl_Avg'], ascending = [False, True], ignore_index=True).iloc[0]
    most_sixes = stats.sort_values(by = ['6s', 'Balls_faced'], ascending = [False, True], ignore_index=True).iloc[0]
    mvp = stats.sort_values(by = 'MVP', ascending = False, ignore_index=True).iloc[0]

    print('Most Runs - {} with {} @ {} avg\tTeam - {}\n'.format(most_runs['Name'], most_runs['Runs'], most_runs['Bat_Avg'], most_runs['Team']))
    print('Most Wkts - {} with {} @ {} avg\tTeam - {}\n'.format(most_wkts['Name'], most_wkts['Wickets'], most_wkts['Bowl_Avg'], most_wkts['Team']))
    print('Most 6s - {} {} sixes\tTeam - {}\n'.format(most_sixes['Name'], most_sixes['6s'], most_sixes['Team']))
    print('\nMOST VALUABLE PLAYER is {} \tTeam - {}\n'.format(mvp['Name'].upper(), mvp['Team']))


    print("\n-----THE END OF SERIES AND SIMULATION-----\n")

    print('Average 1st Innings Total {:.2f}'.format(round(targets/matches, 4)-1))

    print(tossA, tossB)

    str_stats= stats.to_string(col_space= 10, index = False, justify='center')

    with open('seriesStats/allStats.txt', 'w') as f:
        f.writelines(str_stats)
    # with open('seriesStats/allStats_'+teamA.name+'-vs-'+teamB.name+'.txt', 'w') as f:
    #     f.writelines(str_stats)
    
    #print(str_stats)

    if(input('\nEnter ANY key to close')):
        return None

if __name__ == '__main__':
    main()

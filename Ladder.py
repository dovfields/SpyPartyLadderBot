import csv
import sys
from prettytable import PrettyTable
from datetime import datetime
from glicko2 import Rating, Glicko2

class member:
    def __init__(self, name, position=0, defences=0, lastplayed="",mu=0,sigma=0,volativity=0):
        self.name = name
        self.position = int(position)
        self.defences = int(defences)
        self.lastplayed = lastplayed
        if not (mu or sigma or volativity):
            self.rating = Rating()
        else:
            self.rating = Rating(float(mu),float(sigma),float(volativity))

    def writeData(self):
        #Username,Position,Defences,Lastplayed,rating_mu,rating_sigma,rating_volativity
        return self.name,str(self.position),str(self.defences),self.lastplayed,self.rating.mu,self.rating.sigma,self.rating.volatility

    def writeOutput(self=None):
        if not self:
            return "Position","Username","Rating"#,"+Defences/Challenges-"
        return str(self.position),self.name,format(self.rating.mu,"1.0f")#,str(self.defences) if int(self.defences)<0 else "+"+str(self.defences)

class challenge:
    def __init__(self, member1, member2, date):
      self.member1 = member1
      self.member2 = member2
      self.date = date

    def isInChallenge(self, member):
        if member == member1 or member == member2:
            return True
        else:
            return False
        
    def writeOutput(self):
        return self.member1.name,self.member2.name,str(self.date.strftime("%Y-%m-%d"))
    
    def writeOutput(self=None):
        if not self:
            return "Member1","Member2","Date"
        return self.member1.name,self.member2.name,str(self.date.strftime("%Y-%m-%d"))
    
class ladder(object):
    def __init__(self,ladderfile, challengesfile):
        self.members = dict()
        self.challenges = []
        self.ladderfile = ladderfile
        self.challengesfile = challengesfile
        self.loadData(self.ladderfile, self.challengesfile)
    
    def loadData(self, ladderfile, challengesfile):
        #Load Ladder data
        try:
            with open(ladderfile, 'r') as f:
                reader = csv.reader(f)
                try:
                    for row in reader:
                        print(row)
                        self.members[row[0].lower()] = member(*row)
                except csv.Error as e:
                    sys.exit('file %s, line %d: %s' % (file, reader.line_num, e))
        except FileNotFoundError:
            print("No Ladder File Found")

        #Load Challenges
        try:
            with open(challengesfile, 'r') as f:
                reader = csv.reader(f)
                try:
                    for row in reader:
                        self.challenges.append(challenge(*row))
                except csv.Error as e:
                    sys.exit('file %s, line %d: %s' % (file, reader.line_num, e))
        except FileNotFoundError:
            print("No Challenges File Found")
                
    def saveData(self):
        with open(self.ladderfile, 'w', newline='') as f:
            writer = csv.writer(f)
            for entry in self.members.items():
                writer.writerow(entry[1].writeData())
                
        with open(self.challengesfile, 'w', newline='') as f:
            writer = csv.writer(f)
            for entry in self.challenges:
                writer.writerow(entry.writeData())

    def addMember(self, name):
        #Check if the member already exists
        if name in self.members:
            print("Can't add - "+name+" already in ladder")
            return False
        
        toadd = member(name)
        if not self.members:
            toadd.position = 1
        else:
            toadd.position = max(self.members.items(), key=lambda mem: mem[1].position)[1].position+1

        self.members[name.lower()]=toadd

    def addChallenge(self, member1, member2, date):
        if not member1 in self.members:
            return print("Can't challenge - "+member1+" not in ladder")
        elif not member2 in self.members:
            return print("Can't challenge - "+member2+" not in ladder")
        #Check if the parties are less than x spaces away.
        #TODO: Remove magic number
        elif abs(self.members.get(member1).position - self.members.get(member2).position) > 3:
            return print("Can't challenge - "+member1+" & "+member2+" are too separated")
        else:
            #Check if either party is already in a challenge.
            for challenge in self.challenges:
                if challenge.isInChallenge(member1):
                    #Member 1 is already in a challenge
                    #Assume they's the challenger and can cancel and re challenge?
                    print(member1+" in challenge")
                if challenge.isInChallenge(member2):
                    #Member 2 is already in a challenge
                    #Apply challenge rules
                    print(member2+" in challenge")

            #If not add new challenge
            self.challenges.append(challenge(self.members.get(member1),self.members.get(member2), date))

    def addWin(self, user, versus, result):
        try:
            mem_user = self.members[user]
        except KeyError:
            return print("Can't post - "+user+" not in ladder")
        try:
            mem_versus = self.members[versus]
        except KeyError:
            return print("Can't post - "+versus+" not in ladder")
        
        if result:
            glick = Glicko2()
            #Swap positions
            mem_user.position,mem_versus.position = mem_versus.position,mem_user.position
            mem_user.rating,mem_versus.rating = glick.rate_1vs1(mem_user.rating,mem_versus.rating)
        else:
            mem_versus.rating,mem_user.rating = glick.rate_1vs1(mem_versus.rating,mem_user.rating)
    
    def __str__(self):
        x = PrettyTable(member.writeOutput())
        for mem in sorted(self.members.items(), key=lambda mem: mem[1].position):
            x.add_row(mem[1].writeOutput())

        return str(x)

import csv
import sys
from prettytable import PrettyTable
from datetime import datetime

class member:
    def __init__(self, name, position=0, defences=0):
      self.name = name
      self.position = int(position)
      self.defences = int(defences)

    def writeLine(self=None):
        if not self:
            return "Position","Username","+Defences/Challenges-"
        return str(self.position),self.name, str(self.defences) if int(self.defences)<0 else "+"+str(self.defences)

class challenge:
    def __init__(self, member1, member2, date):
      self.member1 = member1
      self.member2 = member2
      self.date = date

    def writeLine(self=None):
        if not self:
            return "Member1","Member2","Date"
        return self.member1,self.member2,str(self.date.strftime("%Y-%m-%d"))
    
class ladder(object):
    def __init__(self,ladderfile, challengesfile):
        self.members = []
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
                    next(reader)
                    for row in reader:
                        print(row)
                        self.members.append(member(row[1],row[0],row[2]))
                except csv.Error as e:
                    sys.exit('file %s, line %d: %s' % (file, reader.line_num, e))
                except StopIteration as e:
                    print("Empty Ladder File")
        except FileNotFoundError:
            print("No Ladder File Found")

        #Load Challenges
        try:
            with open(challengesfile, 'r') as f:
                reader = csv.reader(f)
                try:
                    next(reader)
                    for row in reader:
                        print(row)
                        self.challenges.append(challenge(row[0],row[1],row[2]))
                except csv.Error as e:
                    sys.exit('file %s, line %d: %s' % (file, reader.line_num, e))
                except StopIteration as e:
                    print("Empty Challenges File")
        except FileNotFoundError:
            print("No Challenges File Found")
                
    def saveData(self):
        with open(self.ladderfile, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(member.writeLine())
            for entry in self.members:
                writer.writerow(entry.writeLine())
                
        with open(self.challengesfile, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(challenge.writeLine())
            for entry in self.challenges:
                writer.writerow(entry.writeLine())

    def addMember(self, name):
        #Check if the member already exists
        if self.isInLadder(name):
            print("Can't add - "+name+" already in ladder")
            return False
        
        toadd = member(name)
        if not self.members:
            toadd.position = 1
        else:
            toadd.position = max(self.members, key=lambda mem: mem.position).position+1

        self.members.append(toadd)

    def addChallenge(self, member1, member2, date):
        if not self.isInLadder(member1):
            print("Can't challenge - "+member1+" not in ladder")
        elif not self.isInLadder(member2):
            print("Can't challenge - "+member2+" not in ladder")
        else:
            self.challenges.append(challenge(member1,member2, date))

    def addWin(self, user, result):
        if result:
            print(user + " Won!")
        else:
            print(user + " Lost :(")

    def isInLadder(self, username):
        for mem in (matches for matches in self.members if matches.name.lower() == username.lower()):
            return True
        return False
    
    def __str__(self):
        x = PrettyTable(member.writeLine())
        for mem in self.members:
            x.add_row(mem.writeLine())

        return str(x)

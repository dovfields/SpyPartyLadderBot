import csv
import sys
from prettytable import PrettyTable

class member:
    def __init__(self, name, position=0, defences=0):
      self.name = name
      self.position = position
      self.defences = defences

    def writeLine(self=None):
        if not self:
            return "Position","Username","+Defences/Challenges-"
        return self.position,self.name, self.defences if int(self.defences)<0 else "+"+self.defences
        

class Ladder(object):
    def __init__(self,file=None):
        self.members = []
        self.file = file
        if self.file:
            self.openFile(self.file)
    
    def openFile(self, file):
        with open(file, 'r') as f:
            reader = csv.reader(f)
            try:
                next(reader)
                for row in reader:
                    print(row)
                    self.members.append(member(row[1],row[0],row[2]))
            except csv.Error as e:
                sys.exit('file %s, line %d: %s' % (file, reader.line_num, e))
            except StopIteration as e:
                print("Empty file ignored")
                
    def saveFile(self):
        with open(self.file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(member.writeLine())
            for mem in self.members:
                writer.writerow(mem.writeLine())

    def addMember(self, name):
        toadd = member(name)
        if not self.members:
            toadd.position = 1
        else:
            toadd.position = max(self.members, key=lambda mem: mem.position).position+1

        self.members.append(toadd)
        
    def __str__(self):
        x = PrettyTable(member.writeLine())
        for mem in self.members:
            x.add_row(mem.writeLine())

        return str(x)

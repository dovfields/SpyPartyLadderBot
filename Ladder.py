import csv
import sys

class member:
    def __init__(self, name, position):
      self.name = name
      self.position = position
      self.defenses = 0

class Ladder(object):
    def __init__(self,file=None):
        self.members = []
        self.file = file
        if self.file:
            self.openFile(self.file)
    
    def openFile(self, file):
        with open(file, 'rb') as f:
            reader = csv.reader(f)
            try:
                for row in reader:
                    print(row)
            except csv.Error as e:
                sys.exit('file %s, line %d: %s' % (file, reader.line_num, e))

    def saveFile(self):
        with open(self.file, 'w') as f:
            for mem in self.members:
                line = mem.name+","+str(mem.position)+","+str(mem.defenses)+"\n"
                f.write(line)

    def addMember(self, name):
        toadd = member(name, 0)
        if not self.members:
            toadd.position = 1
        else:
            toadd.position = max(self.members, key=lambda mem: mem.position).position+1

        self.members.append(toadd)
    
        

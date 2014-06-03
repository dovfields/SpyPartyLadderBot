import ForumReader
from Ladder import ladder
import configparser
import datetime
from collections import deque
import time


class command():
    def __init__(self, user, arguments):
        self.user = user
        self.arguments = arguments

    def __str__(self):
        return self.user + "," + str(self.arguments)+"\n"

class commandlog():
    def __init__(self, timestamp, text):
        self.timestamp = float(timestamp)
        self.text = text

    def __str__(self):
        return (str(self.timestamp) + "," + self.text)

    def prettywrite(self):
        convert = datetime.datetime.fromtimestamp(self.timestamp)
        return convert.strftime("%Y-%m-%d %H:%M:%S")+ "," + self.text

class errorlog():
    def __init__(self, timestamp, text):
        self.timestamp = float(timestamp)
        self.text = text

    def __str__(self):
        return (str(self.timestamp) + "," + self.text)

    def prettywrite(self):
        convert = datetime.datetime.fromtimestamp(self.timestamp)
        return convert.strftime("%Y-%m-%d %H:%M:%S")+ "," + self.text

class InvalidCommand(Exception):
    def __init__(self):
        self.value = ""

    def __str__(self):
        return repr(self.value)


def main():
    update = False
    errordeque = deque(maxlen=5)
    commanddeque = deque(maxlen=5)
    #Read Config file
    config = configparser.ConfigParser()
    #Debug - To be removed - Allows the code to be run outside the command line
    #config.read(sys.argv[1])        
    config.read("config.ini")

    #Read in recent commands
    with open("commands.txt") as f:
        lines = f.readlines()

    for line in lines:
        args = line.split(",",1)
        print(args)
        commanddeque.append(commandlog(*args))

    #Read in recent errors
    with open("errors.txt") as f:
        lines = f.readlines()

    for line in lines:
        args = line.split(",")
        print(args)
        errordeque.append(errorlog(*args))

    #Login
    red = ForumReader.forumreader(config["Forum"]["host"])
    red.login(config["User"]["username"], config["User"]["password"])

    #Open saved Ladder
    lad = ladder(config["Data"]["ladderfile"], config["Data"]["challengesfile"])

    #Get Commands
    posts = red.getPosts(startPost=int(config["Forum"]["currentpost"]))
    commands = []
    for post in posts:
        for line in post.postbody:
            if line:
                print(line)
                if line.split(" ", 1)[0].lower() == "ladderbot":
                    try:
                        comargs = line.split(" ", 1)[1].split(" ")
                    except IndexError:
                        print("No arguments found")
                        continue

                    comargs[:] = [comarg.lower() for comarg in comargs]
                    commands.append(command(post.user, comargs))

    for com in commands:
        error = ""
        update = True
        print(com.user, com.arguments)
        try:
            if com.arguments[0] == "join":
                error = lad.addMember(com.user)

                if error:
                    raise InvalidCommand
                else:
                    commanddeque.append(commandlog(time.time(),str(com)))
            elif com.arguments[0] == "challenge":
                try:
                    error = lad.addChallenge(com.user, com.arguments[1], datetime.datetime.today())
                except IndexError:
                    error = "Challenge Error - No defender argument"
                    raise InvalidCommand

                if error:
                    raise InvalidCommand
                else:
                    commanddeque.append(commandlog(time.time(),str(com)))
            elif com.arguments[0] == "post":
                try:
                    result = com.arguments[1]
                except IndexError:
                    error = "Post Error - No result argument"
                    raise InvalidCommand
                try:
                    versus = com.arguments[2]
                except IndexError:
                    error = "Post Error - No versus arguments"
                    raise InvalidCommand

                if result == "win":
                    error = lad.addWin(com.user, versus, True)
                elif result == "loss":
                    error = lad.addWin(com.user, versus, False)

                if error:
                    raise InvalidCommand
                else:
                    commanddeque.append(commandlog(time.time(),str(com)))
            elif com.arguments[0] == "hiatus":
                lad.setHiatus(com.user, True) #not sure if this needs a try/except since this can't called improperly?
            elif com.arguments[0] == "unhiatus":
                lad.setHiatus(com.user, False) #not sure if this needs a try/except since this can't called improperly?
            else:
                error = com.arguments[0]+"- Unknown command"
                raise InvalidCommand
        except InvalidCommand:
            errordeque.append(errorlog(time.time(), com.user+": "+error + "\n"))


    #Edit the post
    if update:
        print(datetime.datetime.now())
        #Add table
        posttext = ForumReader.forumreader.strTagSurround("Ladder", ("b",))
        posttext += ForumReader.forumreader.strTagSurround(str(lad), ("code", "center"))

        #Add commands
        commandstring = ""
        for entry in commanddeque:
            commandstring += entry.prettywrite()
        posttext += ForumReader.forumreader.strTagSurround("Commands", ("b",))
        posttext += ForumReader.forumreader.strTagSurround(commandstring, ("code",))

        #Add errors
        errorstring = ""
        for entry in errordeque:
            errorstring += entry.prettywrite()
        posttext += ForumReader.forumreader.strTagSurround("Errors", ("b",))
        posttext += ForumReader.forumreader.strTagSurround(errorstring, ("code",))


        red.editPost(int(config["Forum"]["resultsforum"]), int(config["Forum"]["resultspost"]),posttext)

    #Save the data
    #Get the last post we read
    if posts:
        config["Forum"]["currentpost"] = posts[-1].postID
        with open('config.ini', 'w') as configfile:
            config.write(configfile)

    with open("commands.txt", "w") as f:
        for entry in commanddeque:
            f.write(str(entry))

    with open("errors.txt", "w") as f:
        for entry in errordeque:
            f.write(str(entry))

    lad.saveData()


if __name__ == "__main__":
    main()

from ForumReader import forumreader
from Ladder import ladder
import configparser
import sys
from datetime import datetime

class command():
    def __init__(self, user, arguments):
      self.user = user
      self.arguments = arguments

def main():
    update = False
    #Read Config file
    config = configparser.ConfigParser()
    #Debug - To be removed - Allows the code to be run outside the command line
    #config.read(sys.argv[1])        
    config.read("config.ini")

    #Login
    red = forumreader(config["Forum"]["host"])
    red.login(config["User"]["username"],config["User"]["password"])    
    print(red.isLogged())
    
    #Open saved Ladder
    lad = ladder(config["Data"]["ladderfile"],config["Data"]["challengesfile"])

    #Get Commands
    posts = red.getPosts(startPost=int(config["Forum"]["currentpost"]))
    commands = []
    for post in posts:
        for line in post.postbody:
            if line:
                #print(line)
                if line.split(" ",1)[0].lower() == "ladderbot":
                    try:
                        comargs = line.split(" ",1)[1].split(" ")
                    except IndexError:
                        print("No arguments found")
                        continue

                    comargs[:] = [comarg.lower() for comarg in comargs]
                    commands.append(command(post.user,comargs))

    
    for com in commands:
        print(com.user, com.arguments)
        if com.arguments[0] == "join":
            lad.addMember(com.user)
            update = True
        if com.arguments[0] == "challenge":
            try:
                lad.addChallenge(com.user,com.arguments[1],datetime.today())
            except IndexError:
                print("Challenge Error - No defender argument")
                continue
        if com.arguments[0] == "post":
            try:
                result = com.arguments[1]
            except IndexError:
                print("Post Error - No result argument")
                continue
            try:
                versus = com.arguments[2]
            except IndexError:
                print("Post Error - No versus arguments")                
                continue
            
            if result == "win":
                lad.addWin(com.user, versus, True)
                update = True
            elif result == "loss":
                lad.addWin(com.user, versus, False)

    #Edit the post
    if update:
        red.editPost(int(config["Forum"]["resultsforum"]), int(config["Forum"]["resultspost"]), forumreader.strTagSurround(str(lad),("code","center")))

    #Save the data
    #Get the last post we read
    config["Forum"]["currentpost"] = posts[-1].postID
    with open('config.ini', 'w') as configfile:
        config.write(configfile)

    lad.saveData()

if __name__ == "__main__":
    main()

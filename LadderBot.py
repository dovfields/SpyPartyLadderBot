from ForumReader import forumreader
import Ladder
import configparser
import sys

def main():
    #Read Config file
    config = configparser.ConfigParser()
    #Debug - To be removed - Allows the code to be run outside the command line
    #config.read(sys.argv[1])        
    config.read("config.ini")

    #Login
    red = forumreader(config["Forum"]["host"])
    red.login(config["User"]["username"],config["User"]["password"])    

    #Get Posts
    posts = red.getPosts(startPost=int(config["Forum"]["currentpost"]))

    commands = []
    for post in posts:
        for line in post.postbody:
            if line:
                if line.split(" ",1)[0].lower() == "ladderbot":
                    commands.append([post.user,line.split(" ",1)[1].lower()])

if __name__ == "__main__":
    main()

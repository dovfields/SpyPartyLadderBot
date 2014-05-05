import http.cookiejar
import configparser
import sys
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urlencode, urljoin
from urllib.request import build_opener, install_opener
from urllib.request import Request, HTTPCookieProcessor
from urllib.error import HTTPError

class forumPost:
    def __init__(self, postID, user, postbody):
      self.postID = postID
      self.user = user
      self.postbody = postbody

class forumReader(object):

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64; rv:14.0) Gecko/20100101 Firefox/14.0.1'
    view_topic = "viewtopic.php?f=%i&t=%i"
    
    def __init__(self, host):
        self.host = host
        self.jar = http.cookiejar.CookieJar()
        self.opener = build_opener(HTTPCookieProcessor(self.jar))
        install_opener(self.opener)

    def _send_query(self, url, query, extra_headers=None, encode=True):
        headers = {'User-Agent': self.user_agent}

        if extra_headers:
            headers.update(extra_headers)

        if encode:
            data = bytes(urlencode(query), 'utf-8')
        else:
            if not isinstance(query, bytes):
                data = bytes(query, 'utf-8')
            else:
                data = query

        request = Request(url, data, headers)
        resp = self.opener.open(request)
        html = resp.read()
        self.opener.close()
        return html
    
    def _get_html(self, url):
        headers = {}
        headers['User-Agent'] = self.user_agent
        request = Request(url, headers=headers)
        resp = self.opener.open(request)
        soup = BeautifulSoup(resp)
        self.opener.close()
        return soup
    
    def login(self, username, password):
        if not self.isLogged():
            self.opener.open("https://secure.spyparty.com/beta/forums/")
            form = {}
            form['login'] = username
            form['password'] = password
            form['doLogin'] = "Log in"
            form['ref'] = "https://secure.spyparty.com/beta/forums"
            form['required'] = ""
            form['service'] = "cosign-beta"
            self._send_query("https://secure.spyparty.com/cosign-bin/cosign.cgi", form)
            return self.isLogged()
        else:
            return True
        
    def isLogged(self):
        if self.jar != None:
            for cookie in self.jar:
                if re.search('phpbb3_.*_u', cookie.name) and cookie.value:
                    return True
        return False

    def getPosts(self, forumID, topicID, start=None, ignoredPosts=None):
        posts = []
        url = urljoin(self.host,self.view_topic %(forumID, topicID) )
        if start:
            url = url+("&start=%i" % start)
            
        soup = self._get_html(url)
        page = soup.find_all("table","tablebg")
        output = {}
        for x, row in enumerate(page):

            author = ""
            text = row.find("b", "postauthor")
            if text:
                author = text.get_text()

            postbody = ""
            text = row.find("div", "postbody")
            if text:
                postbody = text.get_text()

            if author and postbody:
                posts.append(forumPost(x,author,postbody))
                             
        return posts
        

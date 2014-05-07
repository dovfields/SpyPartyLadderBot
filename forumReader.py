import http.cookiejar
import configparser
import sys
import re
import codecs
from time import sleep
from io import BytesIO
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
    view_topic = "/viewtopic.php?f=%i&t=%i"
    view_post = "/viewtopic.php?p=%i"
    edit_url = '/posting.php?mode=edit&f=%i&p=%i'

    edit_form_id = 'postform'
    
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

    def _get_form(self, url, form_id):
        form = self._get_html(url).find("form")
        return self._get_form_values(form)

    def _get_form_values(self, soup):

        inputs = soup.find_all("input")
        values = {}
        for input in inputs:
            if input.get('type') == 'submit' or not input.get('name') or not input.get('value'):
                continue
            values[input['name']] = input['value']
        return {'values': values, 'action': soup['action']}

    def _encode_multipart_formdata(self, fields, boundary=None):
        writer = codecs.lookup('utf-8')[3]
        body = BytesIO()

        if boundary is None:
            boundary = '----------b0uNd@ry_$'

        for name, value in getattr(fields, 'items')():
            body.write(bytes('--%s\r\n' % boundary, 'utf-8'))
            if isinstance(value, tuple):
                file, data = value
                writer(body).write('Content-Disposition: form-data; name="%s"; filename="%s"\r\n' % (name, file))
                body.write(bytes('Content-Type: %s\r\n\r\n' % (self._get_content_type(file)), 'utf-8'))
            else:
                data = value
                writer(body).write('Content-Disposition: form-data; name="%s"\r\n' % (name))
                body.write(bytes('Content-Type: text/plain\r\n\r\n', 'utf-8'))

            if isinstance(data, int):
                data = str(data)

            if isinstance(data, str):
                writer(body).write(data)
            else:
                body.write(data)

            body.write(bytes('\r\n', 'utf-8'))

        body.write(bytes('--%s--\r\n' % (boundary), 'utf-8'))

        content_type = 'multipart/form-data; boundary=%s' % boundary
        return body.getvalue(), content_type

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
        url = self.host + (self.view_topic %(forumID, topicID) )
        if start:
            url += ("&start=%i" % start)
        soup = self._get_html(url)
        page = soup.find_all("table","tablebg")
        for post in page:

            postID = ""
            if post.find("td","gensmall"):
                postID = re.search("(?<=p=)\d*",post.find("td","gensmall").find("a").get("href")).group(0)

            author = ""
            if post.find("b", "postauthor"):
                author = post.find("b", "postauthor").get_text()

            postbody = []
            if post.find("div", "postbody"):
                for content in post.find("div", "postbody").contents:
                    if content.name is None:
                        postbody.append(content.string)
                        
            if author and postbody and postID:
                posts.append(forumPost(postID,author,postbody))
                             
        return posts

    def getPost(self, req_postID):
        url = self.host + (self.view_post %(req_postID) )
            
        soup = self._get_html(url)
        page = soup.find_all("table","tablebg")
        for post in page:

            postID = ""
            if post.find("td","gensmall"):
                postID = re.search("(?<=p=)\d*",post.find("td","gensmall").find("a").get("href")).group(0)
                if int(postID)!=req_postID:
                    continue

            author = ""
            if post.find("b", "postauthor"):
                author = post.find("b", "postauthor").get_text()

            postbody = []
            if post.find("div", "postbody"):
                for content in post.find("div", "postbody").contents:
                    if content.name is None:
                        postbody.append(content.string)

            if author and postbody and postID:
                return forumPost(postID,author,postbody)
                             
        return ""

    def editPost(self, forum, post, message):
        url = self.host + (self.edit_url % (forum, post))
        try:
            form = self._get_form(url, self.edit_form_id)
            form['values']['message'] = message
            form['values']['post'] = 'Submit'
            body, content_type = self._encode_multipart_formdata(form['values'])
            headers = {'Content-Type': content_type}

            """ wait at least 2 seconds so phpBB let us post """
            sleep(2)
            html = self._send_query(url, body, headers, encode=False)
            soup = BeautifulSoup(BytesIO(html))
        except HTTPError as e:
            print('\n>>> Error %i: %s' % (e.code, e.msg))

    def strTagSurround(text, tags):
        for tag in tags:
            text = "["+tag+"]"+text+"[/"+tag+"]"
        return text

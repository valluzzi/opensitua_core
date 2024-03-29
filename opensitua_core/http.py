# -----------------------------------------------------------------------------
# Licence:
# Copyright (c) 2012-2018 Luzzi Valerio 
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
#
# Name:        http.py
# Purpose:
#
# Author:      Luzzi Valerio
#
# Created:     28/07/2018
# -----------------------------------------------------------------------------
from .filesystem import *
from .strings import *
from jinja2 import Environment, FileSystemLoader
import os,sys,re,math
import json,base64
from cgi import FieldStorage, parse_qs, escape
from builtins import str as unicode
import sqlite3


class Params:
    """
    Params
    """

    def __init__(self, environ):
        """
        constructor
        """
        self.q = {}

        if isinstance(environ, (dict,)) and not "REQUEST_METHOD" in environ:
            self.q = environ

        elif environ and "REQUEST_METHOD" in environ and environ["REQUEST_METHOD"] == "GET":
            request_body = environ['QUERY_STRING']
            q = parse_qs(request_body)
            for key in q:
                self.q[key] = [escape(item) for item in q[key]]

        elif environ and "REQUEST_METHOD" in environ and environ["REQUEST_METHOD"] == "POST":

            env_copy = environ.copy()
            env_copy['QUERY_STRING']=''
            q = FieldStorage(fp=environ["wsgi.input"], environ=env_copy, keep_blank_values=True)
            for key in q:
                self.q[key] = q.getvalue(key)
                #print(key, "=", len(q.getvalue(key)))

            #load extra query string info:
            request_body = environ['QUERY_STRING']
            q = parse_qs(request_body)
            for key in q:
                self.q[key] = [escape(item) for item in q[key]]

        elif environ:
            self.q = environ

        if environ and "DOCUMENT_ROOT" in environ:
            self.q["DOCUMENT_ROOT"] = environ["DOCUMENT_ROOT"]
            environ["DOCUMENT_WWW"] = os.path.abspath(environ["DOCUMENT_ROOT"] + "/var/www")
            self.q["DOCUMENT_WWW"] = environ["DOCUMENT_WWW"]

        if environ and "HTTP_COOKIE" in environ:
            if isinstance(environ["HTTP_COOKIE"], (str,)):
                self.q["HTTP_COOKIE"] = mapify(environ["HTTP_COOKIE"], ";")
            else:
                self.q["HTTP_COOKIE"] = environ["HTTP_COOKIE"]

            HTTP_COOKIE = self.q["HTTP_COOKIE"]
            if "__username__" in HTTP_COOKIE:
                self.q["__username__"] = HTTP_COOKIE["__username__"]
            if "__token__" in HTTP_COOKIE:
                self.q["__token__"] = HTTP_COOKIE["__token__"]

        if "encoded" in self.q and self.q["encoded"] in ("true","1",1):
            for key in q:
                if not key in ("encoded","encrypted"):
                    try:
                        self.q[key] = base64.b64decode(self.q[key])
                    except:
                        pass



    def keys(self):
        """
        keys
        """
        return self.q.keys()

    def getvalue(self, key, defaultValue=None):
        """
        getvalue
        """
        value = defaultValue
        if key in self.q:
            if isinstance(self.q[key],(tuple,list)) and len(self.q[key])>0:
                value = self.q[key][0]
            else:
                value = self.q[key]

        return value

    def get(self, key, defaultValue=None):
        """
        get
        """
        if key in self.q:
            if isinstance(self.q[key],(tuple,list)) and len(self.q[key])==1:
                return self.q[key][0]
            else:
                return self.q[key]

        return defaultValue

    def toObject(self):
        return self.q

    def toDictionary(self):
        params = {}
        for key in self.q:
            params[key] = self.get(key)
        return params


def webpath(filename, pivot ):
    """
    webpath -  pivot = "/apps/"
    """
    return "/" + rightpart(normpath(filename), pivot)


def loadlibs(dirnames, type, DOCUMENT_ROOT):
    """
    loadlibs
    """
    text = ""
    dirnames = listify(dirnames, sep=",")

    filever = DOCUMENT_ROOT + "/lib/js/core/version.js"
    version = filetostr(filever)
    if version:
        version = version.replace("__VERSION__=", "").strip("'\"\t ;")

    for dirname in dirnames:
        filenames = ls(dirname, r'.*\.%s$'%(type), recursive=True)
        for filename in filenames:
            #DOCUMENT_ROOT = leftpart(normpath(filename), "/lib/")
            webname = "/lib/" + rightpart(normpath(filename), "/lib/")
            if webname and webname != '/lib/':
                if   type=="js":
                    text += sformat("<script type='text/javascript' src='{filename}?v={version}'></script>\n", {"filename": webname,"version":version});
                elif type=="css":
                    text += sformat("<link href='{filename}?v={version}' rel='stylesheet' type='text/css'/>\n",{"filename": webname,"version":version});

    return text

def template(filetpl, fileout=None, env = None):
    """
    template -  generate text from jinja2 template file
    """
    env = env if env else {}
    workdir = justpath(filetpl)
    workdir = workdir if workdir else "."
    environ = Environment(loader=FileSystemLoader(workdir))
    t = environ.get_template(justfname(filetpl))
    text = t.render(env)
    if fileout:
        strtofile(text, fileout)
    return text


def httpDownload(filename, start_response):
    """
    httpDownload
    """
    response_headers = [
        ("Content-Description", "File Transfer"),
        ("Content-type", "application/octet-stream"),
        ("Content-Disposition","attachment; filename=\"%s\""%(justfname(filename))),
        ("Content-Transfer-Encoding", "binary"),
        ('Content-Length', "%s" % len(data))
    ]

    with open(filename,'rb') as stream:
        start_response("200 OK", response_headers)
        block_size = 4096
        return iter(lambda: stream.read(block_size), '')



def httpResponse(text, status, start_response):
    """
    httpResponse
    """
    text = "%s" % str(text)
    response_headers = [('Content-type', 'text/html'), ('Content-Length', str(len(text)))]
    if start_response:
        start_response(status, response_headers)
    return [ text.encode('utf-8')]

def httpResponseOK(text, start_response):
    """
    httpResponseOK
    """
    return httpResponse(text, "200 OK", start_response)

def httpResponseNotFound(start_response):
    """
    httpResponseNotFound
    """
    return httpResponse("404 NOT FOUND", "404 NOT FOUND", start_response)

def JSONResponse(obj, start_response):
    """
    JSONResponse
    """
    if isstring(obj):
        text = obj
    elif isinstance(obj, (dict, list)):
        text = unicode(json.dumps(obj))
    else:
        text = obj

    response_headers = [('Content-type', 'application/json'), ('Content-Length', str(len(text)))]
    if start_response:
        start_response("200 OK", response_headers)
    return [text.encode('utf-8')]

def getCookies(environ):
    """
    getCookies
    """
    HTTP_COOKIE = environ["HTTP_COOKIE"] if "HTTP_COOKIE" in environ else ""
    return mapify(HTTP_COOKIE,";")


def htmlResponse(environ, start_response=None, checkuser=False):
    """
    htmlResponse - return a Html Page
    """

    if checkuser and not check_user_permissions(environ):
        environ["url"] = justpath(environ["SCRIPT_FILENAME"])+"/back.html"
        return htmlResponse(environ, start_response)

    url = environ["url"] if "url" in environ else normpath(environ["SCRIPT_FILENAME"])
    url = forceext(url, "html")

    DOCUMENT_ROOT = environ["DOCUMENT_ROOT"] if "DOCUMENT_ROOT" in environ else ""

    if not isfile(url):
        return httpResponseNotFound(start_response)

    workdir    = justpath(url)
    index_html = justfname(url)

    jss = (DOCUMENT_ROOT + "/lib/js",
           justpath(url),)

    csss = (DOCUMENT_ROOT + "/lib/css",
            DOCUMENT_ROOT + "/lib/js",
            DOCUMENT_ROOT + "/lib/images",
            justpath(url),)

    env = Environment(loader=FileSystemLoader(workdir))
    t = env.get_template(index_html)

    import opensitua_core

    variables = {
        "loadjs":  loadlibs(jss, "js", DOCUMENT_ROOT),
        "loadcss": loadlibs(csss, "css", DOCUMENT_ROOT),
        "APPNAME": juststem(workdir),
        "os": os,
        "sys":sys,
        "re":re,
        "math": math,
        "gecosistema_core": opensitua_core,
        "environ":environ,
        "__file__":url
    }
    html = t.render(variables)  #.encode("utf-8","replace")
    return httpResponseOK(html, start_response)


def check_user_permissions(environ):
    """
    check_user_permissions
    """
    url = normpath(environ["SCRIPT_FILENAME"])
    filedb = justpath(url) + "/htaccess.sqlite"
    if not isfile(filedb):
        DOCUMENT_ROOT = environ["DOCUMENT_ROOT"] if "DOCUMENT_ROOT" in environ else leftpart(normpath(__file__),"/var/www/")
        filedb = DOCUMENT_ROOT + "/etc/opengis3/htaccess.sqlite"

    HTTP_COOKIE = getCookies(environ)

    if os.path.isfile(filedb):
        conn = sqlite3.connect(filedb)
        conn.create_function("md5", 1, md5text)
        c = conn.cursor()
        HTTP_COOKIE["__token__"] = HTTP_COOKIE["__token__"] if "__token__" in HTTP_COOKIE else ""

        sql = """
        SELECT COUNT(*),[mail] FROM [users] 
        WHERE ('{__token__}' LIKE md5([token]||strftime('%Y-%m-%d','now')) AND [enabled])
                OR ([mail] LIKE 'everyone' AND [enabled]);"""
        sql = sformat(sql, HTTP_COOKIE)

        c.execute(sql)
        (user_enabled,mail) = c.fetchone()
        conn.close()
        return mail if user_enabled else False

    return False


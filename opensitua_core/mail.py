# -----------------------------------------------------------------------------
# Licence:
# Copyright (c) 2012-2018 Luzzi Valerio for Gecosistema S.r.l.
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
# Name:        mail
# Purpose:
#
# Author:      Luzzi Valerio
#
# Created:     12/09/2019
# -----------------------------------------------------------------------------
import smtplib, json
from smtplib import SMTP_SSL as SMTP
from email.message import EmailMessage
from email.mime.text import MIMEText
from .strings import *
from .filesystem import *
from .encryption import read_encrypted

# -------------------------------------------------------------------------------
#   mailto
# -------------------------------------------------------------------------------
def system_mail(To, CC="", Body="", Subject=None, fileconf="mail.conf", verbose=False):
    """
    system_mail
    """
    if isstring(To):
        receivers = To.split(",")
    if CC:
        CC = CC.split(",")

    if not Subject:
        Subject = Body[:16] + "[...]"


    if fileconf and isfile(fileconf):
        if justext(fileconf)=="enc":
            text = read_encrypted(fileconf)
        else:
            text = filetostr(fileconf)
        conf = json.loads(text)
        server = conf["server"] if "server" in conf else ""
        username = conf["username"] if "username" in conf else ""
        password = conf["password"] if "password" in conf else ""
        port = int(conf["port"]) if "port" in conf else 465

        #msg = MIMEMultipart()
        #msg = EmailMessage()
        msg = MIMEText(Body, "html")
        msg['From'] = username
        msg['To'] = ",".join(receivers)
        if CC:
            msg['CC'] = ",".join(CC)
        msg['Subject'] = Subject

        try:
            # mailServer = smtplib.SMTP('smtp.gmail.com', 587)
            mailServer = SMTP(server, port)
            mailServer.login(username, password)
            mailServer.sendmail(username, receivers, msg.as_string())
            mailServer.close()
            if verbose:
                print("Sending mail to <%s>"%(msg['To']))
        except smtplib.SMTPException as ex:
            print(ex)
    else:
        print("No file of account configuration found.")

# -------------------------------------------------------------------------------
#   main
# -------------------------------------------------------------------------------
def main():
    system_mail("valerio.luzzi@gecosistema.it", CC="valluzzi@gmail.com", Body= "This is a test smtplib message.", fileconf="mail.conf.enc")


if __name__ == '__main__':
    main()
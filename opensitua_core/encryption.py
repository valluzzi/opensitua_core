# -------------------------------------------------------------------------------
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
# Name:        encryption.py
# Purpose:
#
# Author:      Luzzi Valerio
#
# Created:     20/10/2020
# -------------------------------------------------------------------------------
import os,tempfile, base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def get_key(password=None, filekey=None):
    """
    get_key
    """
    key = None
    filekey = filekey if filekey else tempfile.gettempdir() + "/.private.key"

    if password and isinstance(password, (str,)):
        kdf = PBKDF2HMAC(algorithm = hashes.SHA256(), length = 32, salt = os.urandom(16), iterations = 100000)
        key = base64.urlsafe_b64encode(kdf.derive(password.encode("utf-8")))
    elif password and isinstance(password, (bytes,)):
        key = password
    elif os.path.isfile(filekey):
        with open(filekey, 'rb') as f:
            key = f.read()
    else:
        key = Fernet.generate_key()
        with open(filekey, 'wb') as f:
            f.write(key)

    return key

def encrypt(text, key=None):
    """
    encrypt
    """
    text = text if isinstance(text, (bytes,)) else text.encode("utf-8")
    return Fernet(get_key(key)).encrypt(text)

def encrypt_file(fileclear, fileciphered=None, filekey=None):
    """
    encrypt_file
    """
    key = None
    fileciphered = fileciphered if fileciphered else fileclear+".enc"

    #optionally read key
    if os.path.isfile(filekey):
        with open(filekey, 'rb') as f:
            key = f.read()

    if os.path.isfile(fileclear):
        with open(fileclear, 'rb') as f:
            token = encrypt(f.read(), key)
            with open(fileciphered, 'wb') as s:
                s.write(token)
    return fileciphered

def decrypt(token, key=None ):
    """
    decrypt
    """
    token = token if isinstance(token,(bytes,)) else token.encode("utf-8")
    return Fernet(get_key(key)).decrypt(token)

def read_encrypted(fileciphered, filekey=None):
    """
    read_encrypted
    """
    text = None
    # optionally read key
    key = None
    if os.path.isfile(filekey):
        with open(filekey, 'rb') as f:
            key = f.read()

    if os.path.isfile(fileciphered):
        with open(fileciphered, 'rb') as f:
            text = decrypt(f.read(), key)
    return text

def decrypt_file(fileciphered, fileclear=None, filekey=None):
    """
    decrypt_file
    """
    fileclear = fileclear if fileclear else fileciphered.replace(".enc","")
    text = read_encrypted(fileciphered, filekey)
    if text:
        with open(fileclear, 'wb') as s:
            s.write(text)
    return fileclear

if __name__=="__main__":

    filename = r"D:\Users\vlr20\Projects\GitHub\OpenGIS3\var\www\lib\py\users\mail.conf"
    fileenc = encrypt_file(filename)
    print(fileenc)
    print("---")
    print(read_encrypted(fileenc))
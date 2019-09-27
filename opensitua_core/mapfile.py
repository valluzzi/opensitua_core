# -------------------------------------------------------------------------------
# Licence:
# Copyright (c) 2012-2019 Luzzi Valerio 
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
# Name:        mapfile.py
# Purpose:
#
# Author:      Luzzi Valerio
#
# Created:     26/09/2019
# -------------------------------------------------------------------------------
from .strings import isstring

def PixelOf(value,unit,style="solid"):

    if isstring(value):
        value = value.replace(",",".")
    if float(value)<=0.1 and style=="solid" :
        return 0.5
    elif unit=="Pixel":
        return round(float(value),2)
    elif unit =="MM":
        return round(float(value)*3.779,2)
    return -1
import requests
from lxml import html
import re

url = 'https://account.gianteagle.com'
r = requests.Session()
gelogin = r.get(url, verify=False)
tree = html.fromstring(gelogin.text)
token = list(set(tree.xpath("//input[@name='__RequestVerificationToken']/@value", smart_strings=False)))[0]
data = {
'__RequestVerificationToken': token,
'UserName': self._username,
'Password': self._password,
'IsRememberMeChecked': 'true',
#'deviceId': 'test',
'submit': 'Continue',
'post': 'Submit'
}


auth = r.post(url, data=data, verify=False, allow_redirects=True)
card = r.get("https://www.gianteagle.com/fuelperks-plus", verify=False)
cardtree = html.fromstring(card.text)
#fuelperks = cardtree.xpath("//p[@class='fuel-perks']")
fuelperkspoints = cardtree.xpath("//a[@data-bind='attr: { href: FuelPerkStatementLink() }']/text()", smart_strings=False)
#<a href="#0" data-bind="attr: { href: FuelPerkStatementLink() }">419<span class="icon icon-fuelperks"></span></a>'
accountnum = cardtree.xpath("//p[@class='account-number']/text()", smart_strings=False)[0].replace('''" + ''',"").replace(" + ","")
expfuel = cardtree.xpath("//div[@class='perks-expiring p14 stormcloud']/text()", smart_strings=False)[1]
numexpfuel = re.search("(\d*)", expfuel).group(0)
dateexpfuel = re.search("(\d*/\d*)", expfuel).group(0)
perkoff = cardtree.xpath("//span[@class='off']/text()", smart_strings=False) #Per gallon of gas [0] #1st Grocery Trip[1]
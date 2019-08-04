import logging
from datetime import datetime
from datetime import timedelta
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.util import Throttle
import requests
from lxml import html
import re

__version_ = '0.0.2'

REQUIREMENTS = ['requests','lxml']

CONF_USERNAME="username"
CONF_PASSWORD="password"

ICON = 'tag-text-outline'

url = 'https://account.gianteagle.com'

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(hours=6)

def setup_platform(hass, config, add_entities, discovery_info=None):
    username = str(config.get(CONF_USERNAME))
    password = str(config.get(CONF_PASSWORD))
    add_entities([
	  giant_eagle(username=username, password=password, interval=SCAN_INTERVAL),
	], True) 

class giant_eagle(Entity):
    def __init__(self, username, password, interval):
        self._username = username
        self._password = password
        self.update = Throttle(interval)(self._update)
    def _update(self):
        try:
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
            auth = r.post(url, data=data, verify=False) #, allow_redirects=True
            card = r.get("https://www.gianteagle.com/fuelperks-plus", verify=False)
            cardtree = html.fromstring(card.text)
            #Number of fuel perks points
            fuelperkspoints = cardtree.xpath("//a[@data-bind='attr: { href: FuelPerkStatementLink() }']/text()", smart_strings=False)[0]
            #Your account number
            accountnum = cardtree.xpath("//p[@class='account-number']/text()", smart_strings=False)[0].replace('''" + ''',"").replace(" + ","")
            expfuel = cardtree.xpath("//div[@class='perks-expiring p14 stormcloud']/text()", smart_strings=False)[1]
            #Get number of fuel perks expiring soon
            numexpfuel = re.search("(\d*)", expfuel).group(0)
            #Date that above number of expriing fuel perks expire
            dateexpfuel = re.search("(\d*/\d*)", expfuel).group(0)
            #what the number of fuel perks equate to
            perkoff = cardtree.xpath("//span[@class='off']/text()", smart_strings=False) #Per gallon of gas [0] #1st Grocery Trip[1]

            self._state = fuelperkspoints
            self._attributes = {}
            self._attributes['account_number'] = accountnum
            self._attributes['exp_soon_perks'] = numexpfuel
            self._attributes['exp_soon_date']= dateexpfuel
            self._attributes['fuel_perk']= perkoff[0]
            self._attributes['grocery_perk']= perkoff[1]


        except Exception as err:
            _LOGGER.error(err)

    @property
    def name(self):
        name = "giant_eagle" #+  self._getattribute
        return name

    @property
    def state(self):
        return self._state

    @property
    def icon(self):
        return ICON

    @property
    def device_state_attributes(self):
        """Return the attributes of the sensor."""
        return self._attributes

    @property
    def should_poll(self):
        """Return the polling requirement for this sensor."""
        return True

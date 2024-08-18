# -*- coding: utf-8-*-
importos
import sys
importshutil
import logging
importyaml
importargparse
from client import tts
from client import stt
from client import johnpath
from client import diagnose
fromclient.conversation import Conversation
# Addjohnpath.LIB_PATH to sys.path
sys.path.append(johnpath.LIB_PATH)
parser = argparse.ArgumentParser(description='john Voice Control Center')
parser.add_argument('--local', action='store_true',
help='Use text input instead of a real microphone')
parser.add_argument('--no-network-check', action='store_true',
help='Disable the network connection check')
parser.add_argument('--diagnose', action='store_true',
help='Run diagnose and exit')
4142
parser.add_argument('--debug', action='store_true', help='Show debug     messages') args = parser.parse_args()
ifargs.local:
fromclient.local_mic import Mic
else:
fromclient.mic import Mic
class john(object):
def __init__(self):
self._logger = logging.getLogger(__name__)
# Createconfigdir if it does not exist yet
if not os.path.exists(johnpath.CONFIG_PATH):
try:
os.makedirs(johnpath.CONFIG_PATH)
exceptOSError:
self._logger.error("Could not create configdir: '%s'",
johnpath.CONFIG_PATH, exc_info=True)
Raise
# Check if configdir is writable
if not os.access(johnpath.CONFIG_PATH, os.W_OK):
self._logger.critical("Configdir %s is not writable. john " +
"won't work correctly.",
johnpath.CONFIG_PATH)
# FIXME: For backwards compatibility, move old config file to newly #        created configdir
old_configfile = os.path.join(johnpath.LIB_PATH, 'profile.yml') new_configfile = johnpath.config('profile.yml')
ifos.path.exists(old_configfile):43
ifos.path.exists(new_configfile):
self._logger.warning("Deprecated profile file found: '%s'. " +
"Please remove it.", old_configfile)
else:
self._logger.warning("Deprecated profile file found: '%s'. " + "Trying to copy it to new location '%s'.",
old_configfile, new_configfile)
try:
shutil.copy2(old_configfile, new_configfile)
exceptshutil.Error:
self._logger.error("Unable to copy config file. " +
"Please copy it manually.",
exc_info=True)
Raise
# Read config
self._logger.debug("Trying to read config file: '%s'", new_configfile)
try:
with open(new_configfile, "r") as f:
self.config = yaml.safe_load(f)
exceptOSError:
self._logger.error("Can't open config file: '%s'", new_configfile) Raise
try:
stt_engine_slug = self.config['stt_engine']
exceptKeyError:
stt_engine_slug = 'sphinx'
logger.warning("stt_engine not specified in profile, defaulting " + "to '%s'", stt_engine_slug)
stt_engine_class = stt.get_engine_by_slug(stt_engine_slug)44
try:
slug = self.config['stt_passive_engine']
stt_passive_engine_class = stt.get_engine_by_slug(slug) exceptKeyError:
stt_passive_engine_class = stt_engine_class
try:
tts_engine_slug = self.config['tts_engine']
exceptKeyError:
tts_engine_slug = tts.get_default_engine_slug()
logger.warning("tts_engine not specified in profile, defaulting " + "to '%s'", tts_engine_slug)
tts_engine_class = tts.get_engine_by_slug(tts_engine_slug)
# Initialize Mic
self.mic = Mic(tts_engine_class.get_instance(),
stt_passive_engine_class.get_passive_instance(),
stt_engine_class.get_active_instance())
def run(self):
if 'first_name' in self.config:
salutation = ("How can I be of service, %s?"
% self.config["first_name"])
else:
salutation = "How can I be of service?"
self.mic.say(salutation)
conversation = Conversation("JOHN", self.mic, self.config) conversation.handleForever()
if __name__ == "__main__":45
print("*******************************************************") print("*             john - personal assistant robot   *")
print("*******************************************************")
logging.basicConfig()
logger = logging.getLogger()
logger.getChild("client.stt").setLevel(logging.INFO)
ifargs.debug:
logger.setLevel(logging.DEBUG)
if not args.no_network_check and not diagnose.check_network_connection(): logger.warning("Network not connected. This may prevent john from " +
"running properly.")
ifargs.diagnose:
failed_checks = diagnose.run()
sys.exit(0 if not failed_checks else 1)
try:
app = john()
except Exception:
logger.error("Error occured!", exc_info=True) sys.exit(1)
app.run()
.............................................
..................
# -*- coding: utf-8-*-46
import re
def detectYears(input):
YEAR_REGEX = re.compile(r'(\b)(\d\d)([1-9]\d)(\b)') return YEAR_REGEX.sub('\g<1>\g<2> \g<3>\g<4>', input) def clean(input):
"""
Manually adjust output text before it's translated into actual speech by the TTS system. This is to fix minior idiomatic issues, for example, that 1901 is pronounced
"one thousand, ninehundred and one" rather than "nineteen oh one".
Arguments:
input -- original speech text to-be modified """
return detectYears(input)
........................
.............
# -*- coding: utf-8-*-
importsmtplib
fromemail.MIMEText import MIMEText import urllib2
import re
frompytz import timezonedefsendEmail(SUBJECT,     BODY,     TO,     FROM,     SENDER,     PASSWORD, SMTP_SERVER):
"""Sends an HTML email."""
forbody_charset in 'US-ASCII', 'ISO-8859-1', 'UTF-8':
try:
BODY.encode(body_charset)
exceptUnicodeError:
Pass
else:
Break
msg = MIMEText(BODY.encode(body_charset), 'html', body_charset)
msg['From'] = SENDER
msg['To'] = TO
msg['Subject'] = SUBJECT
SMTP_PORT = 587
session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
session.starttls()
session.login(FROM, PASSWORD)
session.sendmail(SENDER, TO, msg.as_string())
session.quit()
defemailUser(profile, SUBJECT="", BODY=""):
"""
sends an email.
Arguments:
profile -- contains information related to the user (e.g., email
4748
address)
SUBJECT -- subject line of the email
BODY -- body text of the email
"""
defgenerateSMSEmail(profile):
"""
Generates an email from a user's phone number based on their carrier. """
if profile['carrier'] is None or not profile['phone_number']: return None
returnstr(profile['phone_number']) + "@" + profile['carrier']
if profile['prefers_email'] and profile['gmail_address']:
# add footer
if BODY:
BODY = profile['first_name'] + \
",<br><br>Here are your top headlines:" + BODY BODY += "<br>Sent from your john"
recipient = profile['gmail_address']
if profile['first_name'] and profile['last_name']: recipient = profile['first_name'] + " " + \ profile['last_name'] + " <%s>" % recipient else:
recipient = generateSMSEmail(profile)
if not recipient: return False49
try:
if 'mailgun' in profile:
user = profile['mailgun']['username'] password = profile['mailgun']['password'] server = 'smtp.mailgun.org'
else:
user = profile['gmail_address']
password = profile['gmail_password']
server = 'smtp.gmail.com' sendEmail(SUBJECT, BODY, recipient, user,
"john <john>", password, server)
return True except: return False
defgetTimezone(profile):
"""
Returns the pytztimezone for a given profile.
Arguments:
profile -- contains information related to the user (e.g., email address)
"""
try:
returntimezone(profile['timezone']) except:
return None50
defgenerateTinyURL(URL):
"""
Generates a compressed URL.
Arguments:
URL -- the original URL to-be compressed
"""
target = "http://tinyurl.com/api-create.php?url=" + URL
response = urllib2.urlopen(target)
returnresponse.read()
defisNegative(phrase):
"""
Returns True if the input phrase has a negative sentiment.
Arguments:
phrase -- the input phrase to-be evaluated
"""
returnbool(re.search(r'\b(no(t)?|don\'t|stop|end)\b', phrase,
re.IGNORECASE))
defisPositive(phrase):
"""
Returns True if the input phrase has a positive sentiment. Arguments:
phrase -- the input phrase to-be evaluated
"""
returnbool(re.search(r'\b(sure|yes|yeah|go)\b', phrase, re.IGNORECASE))
.............................51
..................
# -*- coding: utf-8-*-
import logging
importpkgutil
importjohnpath
class Brain(object):
def __init__(self, mic, profile):
"""
Instantiates a new Brain object, which cross-references user input with a list of modules. Note that the order of brain.modules matters, as the Brain will cease execution on the first module that accepts a given input.
Arguments:
mic -- used to interact with the user (for both input and output) profile -- contains information related to the user (e.g., phone number)
"""
self.mic = mic
self.profile = profile
self.modules = self.get_modules()
self._logger = logging.getLogger(__name__)
@classmethod defget_modules(cls):52
"""
Dynamically loads all the modules in the modules folder and sorts
them by the PRIORITY key. If no PRIORITY is defined for a given
module, a priority of 0 is assumed.
"""
logger = logging.getLogger(__name__)
locations = [johnpath.PLUGIN_PATH]
logger.debug("Looking for modules in: %s",
', '.join(["'%s'" % location for location in locations]))
modules = []
for finder, name, ispkg in pkgutil.walk_packages(locations):
try:
loader = finder.find_module(name)
mod = loader.load_module(name)
except:
logger.warning("Skipped module '%s' due to an error.", name,
exc_info=True)
else:
ifhasattr(mod, 'WORDS'):
logger.debug("Found module '%s' with words: %r", name,
mod.WORDS)
modules.append(mod)
else:
logger.warning("Skipped module '%s' because it misses " +
"the WORDS constant.", name)
modules.sort(key=lambda mod: mod.PRIORITY if hasattr(mod, 'PRIORITY') else 0, reverse=True)
return modules53
def query(self, texts):
"""
Passes user input to the appropriate module, testing it against each candidate module's isValid function.
Arguments:
text -- user input, typically speech, to be parsed by a module """
for module in self.modules:
for text in texts:
ifmodule.isValid(text):
self._logger.debug("'%s' is a valid phrase for module " + "'%s'", text, module.__name__)
try:
module.handle(text, self.mic, self.profile)
except Exception:
self._logger.error('Failed to execute module',
exc_info=True)
self.mic.say("I'm sorry. I had some trouble with " +
"that operation. Please try again later.")
else:
self._logger.debug("Handling of phrase '%s' by " +
"module '%s' completed", text,
module.__name__)
finally:
return
self._logger.debug("No module was able to handle any of these " + "phrases: %r", texts)
............................54
...............
# -*- coding: utf-8-*-
import logging
fromnotifier import Notifier
from brain import Brain
class Conversation(object):
def __init__(self, persona, mic, profile):
self._logger = logging.getLogger(__name__)
self.persona = persona
self.mic = mic
self.profile = profile
self.brain = Brain(mic, profile)
self.notifier = Notifier(profile)
defhandleForever(self):
"""
Delegates user input to the handling function when activated.
"""
self._logger.info("Starting to handle conversation with keyword '%s'.", self.persona)
while True:
# Print notifications until empty
notifications = self.notifier.getAllNotifications() fornotif in notifications:
self._logger.info("Received notification: '%s'", str(notif))55
self._logger.debug("Started listening for keyword '%s'",
self.persona)
threshold, transcribed = self.mic.passiveListen(self.persona) self._logger.debug("Stopped listening for keyword '%s'",
self.persona)
if not transcribed or not threshold:
self._logger.info("Nothing has been said or transcribed.") continue
self._logger.info("Keyword '%s' has been said!", self.persona)
self._logger.debug("Started to listen actively with threshold: %r", threshold)
input = self.mic.activeListenToAllOptions(threshold)
self._logger.debug("Stopped to listen actively with threshold: %r", threshold)
if input:
self.brain.query(input) else:
self.mic.say("Pardon?")

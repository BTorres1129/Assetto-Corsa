#
# Nitrous
# Created by asapcarlos
#
# Based upon code from RpmBeeper and Klayking and TKu (AC Forum name)
#
# Based on:
#  http://www.assettocorsa.net/forum/index.php?threads/audible-gear-shift-beep.14237/
#  http://www.assettocorsa.net/forum/index.php?threads/app-request.7234/#post-103371
#
#
# Installation:
#  - Extract to your Assetto Corsa/apps/python directory
#  - Activate the app ingame
#

import ac, acsys
import sys
import math
import re
import configparser , platform , os , os.path , traceback


if platform.architecture()[0] == "64bit":
	libdir = 'rpmbeeper_dll_x64'
else:
	libdir = 'rpmbeeper_dll_x86'
sys.path.insert(0, os.path.join(os.path.dirname(__file__), libdir))
os.environ['PATH'] = os.environ['PATH'] + ";."

from sidekick_lib.sim_info import info
from rpmbeeper_third_party.sim_info import SimInfo
from sound_player import SoundPlayer

sim_info = SimInfo()

# sound
AUDIO_1 = os.path.join(os.path.dirname(__file__), "n2o.wav")
AUDIO_2 = os.path.join(os.path.dirname(__file__), "nojuice.wav")
AUDIO_3 = os.path.join(os.path.dirname(__file__), "off.wav")
AUDIO_4 = os.path.join(os.path.dirname(__file__), "charging.wav")

# app window initialization
NAME = "Nitrous"
WIDTH = 135
HEIGHT = 135
app = ac.newApp(NAME)
sound_player = SoundPlayer(AUDIO_1)

# toggle beeper & controls
beeperEnabled = False
LABEL_TOGGLEBEEPER = "{}"
labelToggle = ac.addButton(app, "")

kersChargeValue = 0
ersCurrentKJValue = 0
nosval = 0
chargeval = 0
hasERS = 0
hasKERS = 0
ison = 0

kersChargeText = ""
kersCharge = ""
ersCurrentKJText = ""
ersCurrentKJ = ""
nostext = ""
nos = ""

timer0 = 0
timer1 = 0

font = "Digital-7 Mono"
#font = "Ticking Timebomb BB"


def acMain(ac_version):
	global kersChargeText, kersCharge, ersCurrentKJText, ersCurrentKJ, nostext, nos
	try:	
		
		ac.setSize(app, WIDTH, HEIGHT)

		# toogle control
		ac.setSize(labelToggle, 60, 20)
		ac.setPosition(labelToggle, 35, 30)
		ac.addOnClickedListener(labelToggle, on_click_toggle)
		ac.setBackgroundOpacity(labelToggle, 0.7)
		on_click_toggle(0)

		# remove app icon
		ac.setIconPosition(app, 0, -10000)

		kersChargeText = ac.addLabel(app, "KERS Charge %:")
		ac.setPosition(kersChargeText, 5, 0)
		ac.setFontSize(kersChargeText, 10)

		kersCharge = ac.addLabel(app, str("0"))
		ac.setFontAlignment(kersCharge, 'center')
		ac.setFontSize(kersCharge, 30)
		ac.setCustomFont(kersCharge, font, 1, 1)
		ac.setPosition(kersCharge, WIDTH/2 - 2, 10)
		ac.setFontColor(kersCharge, 0.3, 1, 0, 1)

		ersCurrentKJText = ac.addLabel(app, "Current KJ:")
		ac.setPosition(ersCurrentKJText, 5, 36)
		ac.setFontSize(ersCurrentKJText, 10)

		ersCurrentKJ = ac.addLabel(app, str("0"))
		ac.setFontAlignment(ersCurrentKJ, 'center')
		ac.setFontSize(ersCurrentKJ, 30)
		ac.setCustomFont(ersCurrentKJ, font, 1, 1)
		ac.setPosition(ersCurrentKJ, WIDTH/2 - 2, 46)
		ac.setFontColor(ersCurrentKJ, 0.3, 1, 0, 1)

		nostext = ac.addLabel(app, "NOS Active?")
		ac.setPosition(nostext, 5, 72)
		ac.setFontSize(nostext, 10)

		nos = ac.addLabel(app, str("No"))
		ac.setFontAlignment(nos, 'center')
		ac.setFontSize(nos, 30)
		ac.setCustomFont(nos, font, 1, 1)
		ac.setPosition(nos, WIDTH/2 - 2, 82)
		ac.setFontColor(nos, 0.3, 1, 0, 1)



		return NAME   # say my name
	except Exception as e:
		ac.log("Meep_Meep: Error: %s" % e)

def acUpdate(dt):

	global timer0, timer1, kersChargeValue, ersCurrentKJValue, hasERS, hasKERS, nosval, chargeval, ison
	timer0 += dt

	#Fetches data 60 times per second
	if timer0 > 0.0166:
		timer0 = 0
		kersChargeValue = ac.getCarState(0, acsys.CS.KersCharge)
		hasERS = info.static.hasERS
		hasKERS = info.static.hasKERS

		if hasERS or hasKERS:
			ersCurrentKJValue = ac.getCarState(0, acsys.CS.ERSCurrentKJ)
			
			#Main nitrous activation
			if bool(int(ersCurrentKJValue) > nosval) == True and bool(int(kersChargeValue*100) < 100) == True and bool(int(kersChargeValue*100) > 2) == True and bool(int(ison) < 1) == True and beeperEnabled:
				nosval = int(ersCurrentKJValue)
				chargeval = int(kersChargeValue*100)
				ison = 1
				ac.setText(nos, str("Yes"))
				sound_player.play(AUDIO_1)

			elif bool(int(ersCurrentKJValue) > nosval) == True and bool(int(kersChargeValue*100) < 100) == True and bool(int(ison) > 0) == True and beeperEnabled:
				nosval = int(ersCurrentKJValue)
				chargeval = int(kersChargeValue*100)
				sound_player.stop()

			#Plays "out of juice" noise at <= 2% nitrous remaining
			elif bool(int(ersCurrentKJValue) > nosval) == True and bool(int(kersChargeValue*100) <= 2) == True and bool(int(ison) < 1) == True and beeperEnabled:
				nosval = int(ersCurrentKJValue)
				chargeval = int(kersChargeValue*100)
				ison = 1
				ac.setText(nos, str("Yes"))
				sound_player.play(AUDIO_2)

			#Adds "charging" noise for KERS recharge, currently turned off and commented out
			#elif bool(chargeval < int(kersChargeValue*100)) == True and bool(int(kersChargeValue*100) < 100) == True and bool(int(ison) < 1) == True and beeperEnabled:
			#	chargeval = int(kersChargeValue*100)
			#	sound_player.play(AUDIO_4)

			elif bool(int(kersChargeValue*100) <= 2) == True and bool(int(ison) > 0) == True and beeperEnabled:
				ison = 0
				ac.setText(nos, str("No"))
				sound_player.play(AUDIO_2)

			#Plays "off" noise when nitrous is disengaged
			elif bool(int(ersCurrentKJValue) == nosval) == True and bool(int(kersChargeValue*100) < 100) == True and bool(int(ison) > 0) == True and beeperEnabled:
				ison = 0
				ac.setText(nos, str("No"))
				sound_player.play(AUDIO_3)
				
			#pit reset app fix
			elif bool(int(ersCurrentKJValue) < 1) == True and beeperEnabled:
				nosval = 0

			else:
				ison = 0
				ac.setText(nos, str("No"))
				sound_player.stop()
				

			ac.setText(kersCharge, str(int(kersChargeValue*100)))
			ac.setText(ersCurrentKJ, str(int(ersCurrentKJValue)))
			return
		


def on_click_toggle(*args):
    global beeperEnabled
    beeperEnabled = not beeperEnabled
    ac.setText(labelToggle, LABEL_TOGGLEBEEPER.format("on" if beeperEnabled else "off"))

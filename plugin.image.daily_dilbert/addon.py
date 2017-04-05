####
# This plugin was inspired by the original Dilbert plugin and the Garfield plugin.
# I used those as basis and rewrote a lot of parts. Some code snippets still are re-used though.
# Thanks to the coders of the two above named plugins!
#
# The intention was to get familiar with Python as I had no clue of it prior. The coding is for sure not 
# perfect and most likely not a good style. Helping comments are welcome - check the repo on github
# https://github.com/bigcookie/plugin.image.daily_dilbert/
# Desires: I would like to add images to the directories including thumbnails to allow right/left key browsing, but performance was too low. Any ideas to improve are welcome.
# 

import urllib2,os,re,sys,datetime,xbmc,xbmcgui,xbmcaddon,xbmcplugin
from resources.lib.modules.addon import Addon	# want to get rid of this to save imports
from calendar import monthrange
from urlparse import parse_qs
from random import randint, randrange

# Want to get rid of this - inherited from Garfield Plugin).
# Also want to replace Addon().add_item() (used later on)
addon = Addon('plugin.image.daily_dilbert', sys.argv)

### Global variables ###
# I dont like global variables, but in this case it is easier/faster for me.
# global variables including used Kodi arguments, which are not supposed to be changed or altered
g_AddonHandle = int(sys.argv[1])
g_AddonPath = xbmcaddon.Addon().getAddonInfo('path')
g_Args = parse_qs(sys.argv[2][1:])
g_Args_Mode = g_Args.get('mode', None)
g_Args_Year = g_Args['year'][0] if 'year' in g_Args else "";
g_Args_Month= g_Args['month'][0] if 'month' in g_Args else "";
g_Args_Day = g_Args['day'][0] if 'day' in g_Args else "";	
g_Args_Page = g_Args['page'][0] if 'page' in g_Args else "";	
g_CacheDir = g_AddonPath + "/cache/"									# Where to we store cached scraped Dilbert URLs
g_Now = datetime.date.today()											# Today

### Dilbert Settings ###
g_UseCache = True														# Use the cache function
g_PageItems = 7 														# the page_number items will be pre-fetched and cached, so the higher the number, the longer it takes.
g_PageItemsRandom = 7													# items to be loaded/pre-scraped in random menu
### Dilbert Scraper Configuration
g_BaseUrl = "http://www.dilbert.com/strip/"								# Base URL, date will be added in form .../strip/yyy-mm-dd to get according Dilbert webpage
g_Pattern = re.compile('"(http://assets.amuniversal.com/[a-z0-9]+)"')	# Pattern to search on Dilberts webpage
g_FirstDilbert = datetime.date(1989,4,16) 								# 1. Dilbert online available on 16.4.1989, required for date checks
### Dilbert icons and fanart 
g_Icons={}
g_Icons['today'] = g_AddonPath + "/resources/media/dil_today.png"		
g_Icons['recent'] = g_AddonPath + "/resources/media/dil_recent.png"
g_Icons['random'] = g_AddonPath + "/resources/media/dil_random.png"
g_Icons['date'] = g_AddonPath + "/resources/media/dil_bydate.png"
g_Icons['browse'] = g_AddonPath + "/resources/media/dil_browse.png"
g_Icons['next'] = g_AddonPath + "/resources/media/dil_next.png"
g_Icons['click'] = g_AddonPath + "/resources/media/dil_click2show.png"	# For necessary click action to show strip as no preview is available
g_FanartImage=["","","","","",""]
g_FanartImage[0]= g_AddonPath + "/resources/media/fanart1.jpg"			# Unused for now
g_FanartImage[1]= g_AddonPath + "/resources/media/fanart2.jpg"			# For "Today"
g_FanartImage[2]= g_AddonPath + "/resources/media/fanart3.jpg"			# For "Random"
g_FanartImage[3]= g_AddonPath + "/resources/media/fanart4.jpg"			# For "Recent"
g_FanartImage[4]= g_AddonPath + "/resources/media/fanart5.jpg"			# For "Browse"
g_FanartImage[5]= g_AddonPath + "/resources/media/fanart6.jpg"			# For "By Date"


### SubRoutines ###
def add_image(image):
	# This function comes from Garfield plugin (thanks!) and adds an image item to the directory
    item = xbmcgui.ListItem(image['name'])
    item.setArt({'thumb': image['thumb_url'],
    			'fanart':fanart_image})
    item.setInfo(
        type='pictures',
        infoLabels={
            "title": image['name'],
            "picturepath": image['url'],
            "exif:path": image['url']
        }
    )
    xbmcplugin.addDirectoryItem(g_AddonHandle, image['url'], item)

def read_cache(date):
	# Reads a cached scraped URL if existent
	cache_file=os.path.join(g_CacheDir + date.strftime('%Y-%m-%d') + '.link')
	if os.path.isfile(cache_file):
		try:
			text_file = open(cache_file, "r")
			url=text_file.read()
			text_file.close()
		except:
			return ""
		return url
	else:
		return ""

def write_cache(date,url):
	# Writes a scraped URL to the cache directory
	cache_file=os.path.join(g_CacheDir + date.strftime('%Y-%m-%d') + '.link')
	if not os.path.isfile(cache_file):
		try:
			text_file = open(cache_file, "w")
			text_file.write(url)
			text_file.close()
		except:
			return False
		return True
	else:
		return False
	
def get_image_url(date):
	# Scrapes Dilbert website for URL to get according Dilbert comic strip from given date. 
	# Can be used with or without caching function (controlled by g_UseCache).
	url = read_cache(date) if g_UseCache else "";
	if url:
		return url 
	else:	
		req=urllib2.Request(g_BaseUrl+date.strftime("%Y-%m-%d")+'/')
		req.add_header('User-Agent', ' Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
		try:
			response=urllib2.urlopen(req)
			page=response.read()
			response.close()
			del response
		except:
			msg=['''Couldn't scrape Dilbert webpage for the date '''+str(date.year)+'/'+str(date.month)+'/'+str(date.day)+'''. Please check your internet connection.''','''To be sure try http://www.dilbert.com/strip/1989-04-16 if the webpage is still alive.''']
			xbmcaddon.Addon().log(msg, xbmc.LOGERROR) 
			addon.show_error_dialog(msg)
			sys.exit(1)		
		match=g_Pattern.search(page)
		if match:
			if g_UseCache:
				write_cache(date,match.group(1))
			return match.group(1)
		else:
			return ""

def create_random_date(starting_date, ending_date):
	# Creates a random date between a starting and an end date
    date_delta = ending_date - starting_date
    random_days = randrange(date_delta.days)
    return starting_date + datetime.timedelta(days=random_days)
	
def create_mainmenu():
	# Main menu of the plugin
	addon.add_item({'mode': 'today'}, {'title':'Today\'s Dilbert'}, img=g_Icons['today'], fanart=g_FanartImage[1],is_folder=True)
	addon.add_item({'mode': 'last_week','page':'1'}, {'title':'Recent Dilberts'}, img=g_Icons['recent'], fanart=g_FanartImage[2],is_folder=True)
	addon.add_item({'mode': 'random'}, {'title':'Random Dilbert'}, img=g_Icons['random'], fanart=g_FanartImage[3],is_folder=True)
	addon.add_item({'mode': 'browse','page':'1'}, {'title':'Browse dates'}, img=g_Icons['browse'], fanart=g_FanartImage[4],is_folder=True)
	addon.add_item({'mode': 'enter'}, {'title':'Open a specific date'}, img=g_Icons['date'], fanart=g_FanartImage[5],is_folder=True)
	xbmcplugin.endOfDirectory(g_AddonHandle)

def check_cachedirectory():
	# Checks if cache directory exists. If not, try to create. If creation failed, return False
	if g_UseCache == False:
		return False
	elif not os.path.exists(g_CacheDir):
		try:
			os.makedirs(g_CacheDir)
		except:
			msg=['Cache directory \"' + g_CacheDir + '\" could not be created. No cache will be used even though it is enabled...']
			xbmcaddon.Addon().log(msg, xbmc.LOGERROR) 
			return False
	return True

def select_lastweek(date,fanart_image):
	# This function builds folder structure for recent Dilbert comic strips and allows to go page by page further into the past.
	# g_PageItems configures the strips shown per page
	# Due to performance, we dont pre-scrape and show thumbnails. Strip is shown on click - though no browsing with the arrow keys possible.
	if g_Args_Year and g_Args_Month and g_Args_Day:
		date=date(g_Args_Year,g_Args_Month,g_Args_Day)
		show_image(date)
		return

	days_offset = g_PageItems * (int(g_Args_Page)-1)
	date  = date - datetime.timedelta(days=(days_offset))
	for i in range(g_PageItems):
		date=date-datetime.timedelta(days=1)
		if date > g_FirstDilbert:
			addon.add_item({'mode': 'browse','year':date.year,'month':date.month,'day':date.day},{'title':'%04d-%02d-%02d'%(date.year,date.month,date.day)}, img=g_Icons['click'], fanart=fanart_image,is_folder=True)				
		else:
			break
	title='Next ' + str(g_PageItems) + ' comic strips... >>'
	addon.add_item({'mode': 'last_week','page':'%s'%(int(g_Args_Page)+1)}, {'title':title}, img=g_Icons['next'], fanart=fanart_image,is_folder=True)
	xbmcplugin.endOfDirectory(g_AddonHandle,cacheToDisc=False)

def select_random(date,fanart_image):
	# This function builds the menu for displaying random Dilbert comic strips.
	# g_PageItemsRandom controls the items shown per page.
	# You can reload a new set of random strips easily without going deeper into the folder structure.
	if g_Args_Year and g_Args_Month and g_Args_Day:
		date=date(g_Args_Year,g_Args_Month,g_Args_Day)
		show_image(date)
		return
		
	if g_PageItemsRandom > 1:
		title='Load another ' + str(g_PageItemsRandom) + ' random comic strips:'
	else:
		title='Load another random comic strip:'
	addon.add_item({'mode': 'random'}, {'title':title}, img=g_Icons['random'], fanart=fanart_image,is_folder=True)
	for i in range(g_PageItemsRandom):
		random_date = create_random_date(g_FirstDilbert, g_Now)
		addon.add_item({'mode': 'browse','year':random_date.year,'month':random_date.month,'day':random_date.day},{'title':'%04d-%02d-%02d'%(random_date.year,random_date.month,random_date.day)}, img=g_Icons['click'], fanart=fanart_image,is_folder=True)				

	xbmcplugin.endOfDirectory(g_AddonHandle)

def select_browse(fanart_image):
	# This function builds the folder structure for browsing by date. 
	# Due to time needed for scraping, the comic strip URL is scraped on selection and no thumbnails are shown. This prevents unfortunately browsing with the arrow keys...
	if g_Args_Day:
		date=datetime.date(int(g_Args_Year),int(g_Args_Month),int(g_Args_Day))
		image_url= get_image_url(date)
		xbmc.executebuiltin("ShowPicture(%s)"%image_url)
	elif g_Args_Month:
		day_range_end = g_Now.day+1 if (int(g_Args_Year) == g_Now.year and int(g_Args_Month) == g_Now.month) else monthrange(int(g_Args_Year),int(g_Args_Month))[1]+1
		day_range_start = 16 if (int(g_Args_Year) == 1989 and int(g_Args_Month) == 4) else 1
		for i in range(day_range_start,day_range_end,1):
			if (int(g_Args_Year) == g_Now.year and int(g_Args_Month) == g_Now.month and int(i) == g_Now.day):
				title_addon = ' (Today)'
			elif (int(g_Args_Year) == g_FirstDilbert.year and int(g_Args_Month) == g_FirstDilbert.month and i == g_FirstDilbert.day):
				title_addon = ' (First Dilbert online available)' 
			else:
				title_addon = ""
			addon.add_item({'mode': 'browse','year':g_Args_Year,'month':g_Args_Month,'day':i},{'title':'%s'%i + title_addon}, img=g_Icons['click'], fanart=fanart_image,is_folder=True)
		xbmcplugin.endOfDirectory(g_AddonHandle)
	elif g_Args_Year:
		month_range_end = g_Now.month+1 if (int(g_Args_Year) == g_Now.year) else 12+1
		month_range_start = 4 if (int(g_Args_Year) == 1989) else 1
		for i in range(month_range_start,month_range_end,1):
			title= datetime.date(int(g_Args_Year),int(i),1)
			title=title.strftime("%B") #+ ' %s'%i
			addon.add_item({'mode': 'browse','year':g_Args_Year,'month':i},{'title':title}, img=g_Icons['next'], fanart=fanart_image,is_folder=True)
		xbmcplugin.endOfDirectory(g_AddonHandle)
	else:
		for i in range(g_Now.year,g_FirstDilbert.year-1,-1):
			addon.add_item({'mode': 'browse','year':'%4d'%i},{'title':'%s'%i}, img=g_Icons['next'], fanart=fanart_image,is_folder=True)
		xbmcplugin.endOfDirectory(g_AddonHandle)

def select_date(date):
	# Shows Dilbert comic strip per entered date. 
	# Checks entered date as well for format and if in range from first Dilbert to today
	keyboard = xbmc.Keyboard('', 'Enter date(yyyy/mm/dd)', False)
	keyboard.doModal()
	if keyboard.isConfirmed():
		input = keyboard.getText()
		try:
			year,month,day = input.split('/')
			entered_date = datetime.date(int(year),int(month),int(day))
			if entered_date > date:
				msg=['You hit the future.\nYour entered date '+year+'/'+month+'/'+day+' is out of range!!!']
				addon.show_error_dialog(msg)
			elif entered_date < g_FirstDilbert:
				msg=['Too far back in time. Your entered date '+year+'/'+month+'/'+day+' is out of range!\nThe first electronically avialbale Dilbert is from '+str(g_FirstDilbert.year)+'/'+str(g_FirstDilbert.month)+'/'+str(g_FirstDilbert.day)+' !']
				addon.show_error_dialog(msg)
			else:
				image_url = get_image_url(entered_date)
				xbmc.executebuiltin("ShowPicture(%s)"%image_url)
		except (TypeError,ValueError):
			msg=['Please enter the date in the correct format \"yyyy/mm/dd\" !']
			addon.show_error_dialog(msg)
			sys.exit(1)
	else:
		return
			
def show_image(date):
	# This function displays a comic strip by date.
	image_url=get_image_url(date)
	if image_url:
		xbmc.executebuiltin("ShowPicture(%s)"%image_url)
	else:
		return False

### Main program start ###	
xbmcplugin.setContent(g_AddonHandle, 'pictures')
# Check for Cache
g_UseCache=check_cachedirectory()
# Show menus
if g_Args_Mode is None:
	create_mainmenu()
elif g_Args_Mode[0]=='today':
	show_image(g_Now)
elif g_Args_Mode[0]=='last_week':
	select_lastweek(g_Now,g_FanartImage[2])
elif g_Args_Mode[0]=='random':
	select_random(g_Now,g_FanartImage[3])
elif g_Args_Mode[0]=='browse':
	select_browse(g_FanartImage[4])
elif g_Args_Mode[0]=='enter':
	select_date(g_Now)

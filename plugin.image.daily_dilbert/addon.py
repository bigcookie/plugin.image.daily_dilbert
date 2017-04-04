####
# This plugin was inspired by the original Dilbert plugin and the Garfield plugin.
# I uses those as basis and rewrote some parts. Some code snippets still are re-used
# Thanks to the coders of the two above named plugins!
#
import urllib2,os,re,sys,datetime,xbmc,xbmcgui,xbmcaddon,xbmcplugin
from resources.lib.modules.addon import Addon	# want to get rid of this to save imports
from calendar import monthrange
from urlparse import parse_qs
from random import randint, randrange

# Want to get rid of this - inherited from Garfield Plugin).
# Also want to replace Addon().add_item() (used later on)
addon = Addon('plugin.image.daily_dilbert', sys.argv)

# General Plugin Variables
addon_handle = int(sys.argv[1])
xbmcplugin.setContent(addon_handle, 'pictures')
AddonPath = xbmcaddon.Addon().getAddonInfo('path')
args = parse_qs(sys.argv[2][1:])
mode = args.get('mode', None)

# Where to find icons and fanart
fanart_image = os.path.join(AddonPath + "/resources/media/fanart1.jpg")
fanart_image2 = os.path.join(AddonPath + "/resources/media/fanart2.jpg")
fanart_image3 = os.path.join(AddonPath + "/resources/media/fanart3.jpg")
fanart_image4 = os.path.join(AddonPath + "/resources/media/fanart4.jpg")
fanart_image5 = os.path.join(AddonPath + "/resources/media/fanart5.jpg")
fanart_image6 = os.path.join(AddonPath + "/resources/media/fanart6.jpg")
icon = os.path.join(AddonPath + "/resources/media/icon.png")
today = os.path.join(AddonPath + "/resources/media/dil_today.png")
recent = os.path.join(AddonPath + "/resources/media/dil_recent.png")
random = os.path.join(AddonPath + "/resources/media/dil_random.png")
date = os.path.join(AddonPath + "/resources/media/dil_bydate.png")
browse = os.path.join(AddonPath + "/resources/media/dil_browse.png")
next = os.path.join(AddonPath + "/resources/media/dil_next.png")
click = os.path.join(AddonPath + "/resources/media/dil_click2show.png")

# Dilbert related variables
base_url="http://www.dilbert.com/strip/"							# Base URL, date will be added in form .../strip/yyy-mm-dd to get according Dilbert webpage
pattern=re.compile('"(http://assets.amuniversal.com/[a-z0-9]+)"')	# Pattern to search on Dilberts webpage
cache_dir=os.path.join(AddonPath + '\\cache\\')						# Where to we store cached scraped Dilbert URLs
page_items=7 														# the page_number items will be pre-fetched and cached, so the higher the number, the longer it takes.
page_items_random=5													# items to be loaded/pre-scraped in random menu
first_dilbert=datetime.date(1989,4,16) 								# 1. Dilbert am 16.4.1989, required for date checks
now=datetime.date.today()											# Today
use_cache=True														# Use the cache function

# SubRoutines
def add_image(image):
	# This function comes from Garfield plugin and adds an image item to the directory
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
    xbmcplugin.addDirectoryItem(addon_handle, image['url'], item)

def read_cache(day):
	# Read a cached scraped URL if existent
	cache_file=os.path.join(cache_dir + day.strftime('%Y-%m-%d') + '.link')
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

def write_cache(day,url):
	# Write a scraped URL to the cache
	cache_file=os.path.join(cache_dir + day.strftime('%Y-%m-%d') + '.link')
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
	
def get_image_url(day,use_cache=True):
	# Scrape Dilbert website for URL to get according Dilbert. Can be used with or without caching function. Caching enabled by default.
	if use_cache:
		url=read_cache(day)
	else:
		url=""
	if url:
		return url 
	req=urllib2.Request(base_url+day.strftime("%Y-%m-%d")+'/')
	req.add_header('User-Agent', ' Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
	try:
		response=urllib2.urlopen(req)
		page=response.read()
		response.close()
		del response
	except:
		msg=['''Couldn't open Dilbert webpage for scraping. Check your internet connection or probably the webpage structure has changed... Try http://www.dilbert.com/strip/1989-04-16 if webpage is still alive.''']
		addon.show_error_dialog(msg)
		sys.exit(1)		
	match=pattern.search(page)
	if match:
		if use_cache:
			write_cache(day,match.group(1))
		return match.group(1)
	else:
		return ""

def create_random_date(starting_date, ending_date):
	# Create a random date between a starting and an end date
    date_delta = ending_date - starting_date
    random_days = randrange(date_delta.days)
    return starting_date + datetime.timedelta(days=random_days)
	
def create_mainmenu():
# Main menue of the plugin
	addon.add_item({'mode': 'today'}, {'title':'Today\'s Dilbert'}, img=today, fanart=fanart_image2,is_folder=True)
	addon.add_item({'mode': 'last_week','page':'1'}, {'title':'Recent Dilberts'}, img=recent, fanart=fanart_image3,is_folder=True)
	addon.add_item({'mode': 'random'}, {'title':'Random Dilbert'}, img=random, fanart=fanart_image4,is_folder=True)
	addon.add_item({'mode': 'browse','page':'1'}, {'title':'Browse dates'}, img=browse, fanart=fanart_image5,is_folder=True)
	addon.add_item({'mode': 'enter'}, {'title':'Open a specific date'}, img=date, fanart=fanart_image6,is_folder=True)
	xbmcplugin.endOfDirectory(addon_handle) #,cacheToDisc=False)

def check_cachedirectory(use_cache=True):
# Check if cache directory exists. If not, try to create. If creation failed, dont use caching
	if use_cache == False:
		return False
	elif not os.path.exists(cache_dir):
		try:
			os.makedirs(cache_dir)
		except:
			msg=['Cache directory could not be created. No cache will be used even though it is enabled...']
			xbmcaddon.Addon().log(msg, xbmc.LOGERROR) 
			return False
	return True

def select_today(now,use_cache):
# simple, who todays Dilbert
	image_url=get_image_url(now,use_cache)
	if image_url:
		xbmc.executebuiltin("ShowPicture(%s)"%image_url)
	
def select_lastweek(page,page_items,now,use_cache,first_dilbert,next,fanart_image,addon_handle):
# This function builds recent Dilberts folder structure and allows to go page by page further into the past. 
# Pre-scraping is used, which allows browsing with the arrow keys
	days_offset = page_items * (int(page)-1)
	now  = now - datetime.timedelta(days=(days_offset))
	for i in range(page_items):
		now=now-datetime.timedelta(days=1)
		image_url = get_image_url(now,use_cache)
		if now > first_dilbert:
			if image_url:
				add_image({'url':image_url,'thumb_url':image_url,'name':'%04d-%02d-%02d'%(now.year,now.month,now.day)})
		else:
			break
	if now > first_dilbert:
		title='Next ' + str(page_items) + ' comic strips... >>'
		addon.add_item({'mode': 'last_week','page':'%s'%(int(page)+1)}, {'title':title}, img=next, fanart=fanart_image,is_folder=True)
	xbmcplugin.endOfDirectory(addon_handle,cacheToDisc=False)

def select_random(page_items,next,fanart_image,now,first_dilbert,use_cache,addon_handle):
# This function will pre-scrape page_items# random Dilberts and create the menu. Pre-fetching takes time, probably better to not pre-fetch?
	if page_items_random > 1:
		title='Load another ' + str(page_items_random) + ' random comic strips:'
	else:
		title='Load another random comic strip:'
	addon.add_item({'mode': 'random'}, {'title':title}, img=random, fanart=fanart_image,is_folder=True)
	for i in range(page_items_random):
		random_date = create_random_date(first_dilbert, now)
		image_url = get_image_url(random_date,use_cache)
		if image_url:
			add_image({'url':image_url,'thumb_url':image_url,'name':'%04d-%02d-%02d'%(random_date.year,random_date.month,random_date.day)})
	xbmcplugin.endOfDirectory(addon_handle)

def select_browse(args,next,fanart_image,use_cache,addon_handle):
# This function builds the date browsing filder structure and allows to select. 
# Due to large amount of pre-scraping per month, ShowPicture is used, which doesnt allow arrow browsing, but allows fast building of menus
	year = args['year'][0] if 'year' in args else "";
	month= args['month'][0] if 'month' in args else "";
	day  = args['day'][0] if 'day' in args else "";
	if day:
		date=datetime.date(int(year),int(month),int(day))
		image_url= get_image_url(date,use_cache)
		xbmc.executebuiltin("ShowPicture(%s)"%image_url)
	elif month:
		day_range_end = now.day+1 if (int(year) == now.year and int(month) == now.month) else monthrange(int(year),int(month))[1]+1
		day_range_start = 16 if (int(year) == 1989 and int(month) == 4) else 1
		for i in range(day_range_start,day_range_end,1):
			if (int(year) == now.year and int(month) == now.month and int(i) == now.day):
				title_addon = ' (Today)'
			elif (int(year) == first_dilbert.year and int(month) == first_dilbert.month and i == first_dilbert.day):
				title_addon = ' (First Dilbert online available)' 
			else:
				title_addon = ""
			addon.add_item({'mode': 'browse','year':year,'month':month,'day':i},{'title':'%s'%i + title_addon}, img=click, fanart=fanart_image,is_folder=True)
		xbmcplugin.endOfDirectory(addon_handle)
	elif year:
		month_range_end = now.month+1 if (int(year) == now.year) else 12+1
		month_range_start = 4 if (int(year) == 1989) else 1
		for i in range(month_range_start,month_range_end,1):
			title= datetime.date(int(year),int(i),1)
			title=title.strftime("%B") #+ ' %s'%i
			addon.add_item({'mode': 'browse','year':year,'month':i},{'title':title}, img=next, fanart=fanart_image,is_folder=True)
		xbmcplugin.endOfDirectory(addon_handle)
	else:
		for i in range(now.year,first_dilbert.year-1,-1):
			addon.add_item({'mode': 'browse','year':'%4d'%i},{'title':'%s'%i}, img=next, fanart=fanart_image,is_folder=True)
		xbmcplugin.endOfDirectory(addon_handle)

def select_date(now,first_dilbert,use_cache):
# Show Dilbert per entered date. Will check entered date as well
	keyboard = xbmc.Keyboard('', 'Enter date(yyyy-mm-dd)', False)
	keyboard.doModal()
	if keyboard.isConfirmed():
		input = keyboard.getText()
		try:
			year,month,day = input.split('-')
			entered_date = datetime.date(int(year),int(month),int(day))
			if entered_date > now:
				msg=['You hit the future.\nYour entered date '+year+'-'+month+'-'+day+' is out of range!!!']
				addon.show_error_dialog(msg)
			elif entered_date < first_dilbert:
				msg=['Too far back in time. Your entered date '+year+'-'+month+'-'+day+' is out of range!\nThe first electronically avialbale Dilbert is from '+str(first_dilbert.year)+'-'+str(first_dilbert.month)+'-'+str(first_dilbert.day)+' !']
				addon.show_error_dialog(msg)
			else:
				image_url = get_image_url(entered_date,use_cache)
				xbmc.executebuiltin("ShowPicture(%s)"%image_url)
		except (TypeError,ValueError):
			msg=['Please enter the date in the correct format \"yyyy-mm-dd\" !']
			addon.show_error_dialog(msg)
			sys.exit(1)
	else:
		return
			
### Main program start ###			
use_cache=check_cachedirectory(use_cache)
if mode is None:
	create_mainmenu()
elif mode[0]=='today':
	select_today(now,use_cache)
elif mode[0]=='last_week':
	page = args['page'][0]
	select_lastweek(page,page_items,now,use_cache,first_dilbert,next,fanart_image3,addon_handle)
elif mode[0]=='random':
	select_random(page_items,next,fanart_image4,now,first_dilbert,use_cache,addon_handle)
elif mode[0]=='browse':
	select_browse(args,next,fanart_image5,use_cache,addon_handle)
elif mode[0]=='enter':
	select_date(now,first_dilbert,use_cache)

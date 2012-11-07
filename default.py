import urllib, urllib2, re, sys, cookielib
import xbmc, xbmcgui, xbmcplugin, xbmcaddon
#from BeautifulSoup import BeautifulSoup, SoupStrainer

handle = int(sys.argv[1])

recursion = 0

USERAGENT = "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-GB; rv:1.9.2.8) Gecko/20100722 Firefox/3.6.8"

urls = {}
urls['top40'] = "http://www.vbox7.com/top40"
urls['categories'] = "http://www.vbox7.com/categories"
urls['category'] = "http://www.vbox7.com/category:%s&page=1"
urls['index'] = "http://www.vbox7.com/"
urls['search_videos_list'] = "http://www.vbox7.com/search/?completed=0&vbox_q=%s&ord=date&period=false"

__settings__ = xbmcaddon.Addon(id='plugin.video.vbox7')

def buildItemUrl(item_params = {}, url = ""):
	for k, v in item_params.items():
		if (k != "Title" and k != 'thumbnail'):
			url += k + "=" + urllib.quote_plus(v) + "&"
	return url

def getParameters(parameterString):
	commands = {}
	splitCommands = parameterString[parameterString.find('?')+1:].split('&')

	for command in splitCommands:
		if (len(command) > 0):
			splitCommand = command.split('=')
			name = splitCommand[0]
			value = splitCommand[1]
			commands[name] = value

	return commands

def addFolderListItem(item_params = {}, size = 0):
	item = item_params.get
  
  icon = "DefaultFolder.png"
  
  if (item("thumbnail" , "DefaultFolder.png").find("http://") == -1):
    thumbnail = "DefaultFolder.png"
  else:
    thumbnail = item("thumbnail")

	listitem = xbmcgui.ListItem(item("Title"), iconImage=icon, thumbnailImage=thumbnail)
	listitem.setInfo(type = 'video', infoLabels = {'Title': item("Title")})

	url = buildItemUrl(item_params, '%s?' % sys.argv[0])

	xbmcplugin.addDirectoryItem(handle, url=url, listitem=listitem, isFolder=True, totalItems=size)

def addActionListItem(item_params = {}, size = 0):
	item = item_params.get
	folder = False

  icon = "DefaultFolder.png"
  
  if (item("thumbnail" , "DefaultFolder.png").find("http://") == -1):
    thumbnail = "DefaultFolder.png"
  else:
    thumbnail = item("thumbnail")

	listitem = xbmcgui.ListItem(item("Title"), iconImage=icon, thumbnailImage=thumbnail)
	listitem.setInfo(type = 'video', infoLabels = {'Title': item("Title")})

	url = buildItemUrl(item_params, '%s?' % sys.argv[0])

	xbmcplugin.addDirectoryItem(handle, url=url, listitem=listitem, isFolder=folder, totalItems=size)

def showMessage(heading, message):
	xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s)' % (heading, message, 3000))

def getUserInput(title = "Input", default="", hidden=False):
	result = None

	# Fix for when this functions is called with default=None
	if not default:
		default = ""

	keyboard = xbmc.Keyboard(default, title)
	keyboard.setHiddenInput(hidden)
	keyboard.doModal()

	if keyboard.isConfirmed():
		result = keyboard.getText()

	return result

class RedirectHandler(urllib2.HTTPRedirectHandler):

	def http_error_302(self, req, fp, code, msg, headers):

		cookies = repr(cj)

		if (cookies.find("name='jsSecretToken', value='") == -1):
			pass
		else:
			start = cookies.find("name='jsSecretToken', value='") + len("name='jsSecretToken', value='")
			jsTok = cookies[start:cookies.find("', port=None", start)]

			__settings__.setSetting("jsTok", jsTok)

			print "redirect: found new jsSecretToken " + jsTok

			req.add_header('Cookie', 'PHPSESSID=' + __settings__.getSetting("PHPSESSID") + '; checkCookies=yes; t=1; jsSecretToken=' + __settings__.getSetting("jsTok") + ';')


		result = urllib2.HTTPRedirectHandler.http_error_302(
			self, req, fp, code, msg, headers)

		return result

cj = cookielib.LWPCookieJar()

def getPage(url):
	print 'opening ' + url

	global recursion, cj

	recursion += 1

	req = urllib2.Request(url)
	req.add_header('User-Agent', USERAGENT)

	PHPSESSID = __settings__.getSetting("PHPSESSID")

#	if (len(PHPSESSID) < 1):
#		PHPSESSID = '1234567890'
#		__settings__.setSetting("PHPSESSID", PHPSESSID)

	jsTok = __settings__.getSetting("jsTok")

	bla = 'checkCookies=yes; jsSecretToken=' + jsTok + ';'

	if (len(PHPSESSID) > 1):
		bla += ' PHPSESSID=' + PHPSESSID + ';'

	print "Cookie: " + bla

	req.add_header('Cookie', bla)

	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj), RedirectHandler)
	urllib2.install_opener(opener)

	con = urllib2.urlopen(req)

	cookies = repr(cj)
	if (cookies.find("name='PHPSESSID', value='") == -1):
		pass
	else:
		start = cookies.find("name='PHPSESSID', value='") + len("name='PHPSESSID', value='")
		PHPSESSID = cookies[start:cookies.find("', port=None", start)]

		__settings__.setSetting("PHPSESSID", PHPSESSID)

		print "found new PHPSESSID " + PHPSESSID

	if (cookies.find("name='jsSecretToken', value='") == -1):
		pass
	else:
		start = cookies.find("name='jsSecretToken', value='") + len("name='jsSecretToken', value='")
		jsTok = cookies[start:cookies.find("', port=None", start)]

		__settings__.setSetting("jsTok", jsTok)

		print "found new jsSecretToken " + jsTok

	result = con.read()
	con.close()

	#document.cookie = 'jsSecretToken=71123cdb459c382;

	if (result.find("document.cookie = '") == -1):
		pass
	else:
		start = result.find("document.cookie = 'jsSecretToken=") + len("document.cookie = 'jsSecretToken=")
		jsTok = result[start:result.find(";", start)]
		print 'found document.cookie jsTok ' + jsTok
		__settings__.setSetting("jsTok", jsTok)

	#window.location = '?js=1&token=b87be4265d&back_to=%2Ftop40'

	if (result.find("window.location = '?js=1&token=") == -1):
		pass
	else:
		start = result.find("window.location = '?js=1&token=") + len("window.location = '?js=1&token=")
		jsTok = result[start:result.find("&", start)]
		print 'found window.location jsTok ' + jsTok
		__settings__.setSetting("jsTok", jsTok)

		start = result.find("window.location = '?") + len("window.location = '?")

		if (recursion < 5):
			return getPage('http://www.vbox7.com/show:missjavascript?' + result[start:result.find("'", start)])

	recursion -= 1

	return result

def scrapeVideos(url):
	result = getPage(url)

	objects = []

	videos = re.compile('class="clipThumb".*?href="/play:(.*?)".*?src="(.*?)".*?href=".*?">(.*?)</a>', re.DOTALL).findall(result);

	if (get('act') == 'index'):
		videos = re.compile('class="editorChoice".*?href="/play:(.*?)".*?src="(.*?)".*?<h4>(.*?)</h4>', re.DOTALL).findall(result) + videos;

	for vid, thumbnail, name in videos:
		item = {}
		item['id'] = vid
		item['thumb'] = thumbnail
		item['title'] = name
		objects.append(item)

	return objects


def saveSearch(old_query, new_query, store = "stored_searches"):
	print "stored searches " + store
	old_query = urllib.unquote_plus(old_query)
	new_query = urllib.unquote_plus(new_query)
	try:
		searches = eval(__settings__.getSetting(store))
	except:
		searches = []

	print searches

	for count, search in enumerate(searches):
		if (search.lower() == old_query.lower()):
			del(searches[count])
			break

	searchCount = 20
	searches = [new_query] + searches[:searchCount]

	print searches
	__settings__.setSetting(store, repr(searches))

def MainMenu():
	addFolderListItem({'Title': 'Index', 'act': 'index'})
	addFolderListItem({'Title': 'Top 40', 'act': 'top40'})
	addFolderListItem({'Title': 'Categories', 'act': 'categories'})
	addActionListItem({'Title': 'Play by ID', 'act': 'playbyid', 'name': ''})
	addFolderListItem({'Title': 'Search videos', 'act': 'search_videos', 'name': ''})


def ListVideos(url):
	objects = scrapeVideos(url)
	for video in objects:
		addActionListItem({'Title': video['title'], 'thumbnail': video['thumb'], 'act': 'play', 'vid': video['id'], 'name': video['title']})

def Categories():
	result = getPage(urls[params['act']])
	categories = re.compile('class="catThumb".*?href="/category:(.*?)".*?src="(.*?)".*?href=".*?">(.*?)</a>', re.DOTALL).findall(result);
	for cid, thumbnail, name in categories:
		addFolderListItem({'Title': name, 'act': 'category', 'category_id': cid, 'thumbnail': thumbnail})

def SearchVideos():
	addFolderListItem({'Title': 'Search...', 'act': 'search_videos_list'})

	try:
		searches = eval(__settings__.getSetting("stored_searches"))
	except:
		searches = []

	for search in searches:
		addFolderListItem({'Title': search, 'act': 'search_videos_list', 'search_string': search})

def SearchVideosList():
	if (get("search_string")):
		query = get("search_string")
		query = urllib.unquote_plus(query)
		saveSearch(query, query)
	else:
		query = getUserInput()
		saveSearch(query, query)

	if (query):
		ListVideos(urls['search_videos_list'] % urllib.quote_plus(query))

def PlayById():
	vid = getUserInput()
	PlayVid(vid)

def PlayVid(vid, name = ""):
	print "playing " + vid
	result = getPage('http://vbox7.com/etc/ext.do?key=' + vid)
	match = re.compile('flv_addr=(.+?)&jpg_addr=(.+?)&').findall(result)
	if (len(match) == 1 and len(match[0]) == 2):
		print "flv: " + match[0][0]
		print "thumb: " + match[0][1]
		item = xbmcgui.ListItem(label = name, thumbnailImage = 'http://' + match[0][1])
		item.setInfo(type = 'video', infoLabels = {'Title': name})
		print "playing: " + "http://" + match[0][0]
		#xbmc.executebuiltin("PlayMedia(" + "http://" + match[0][0] + ")")
		xbmc.Player().play("http://" + match[0][0], item)
		return True
	else:
		showMessage('Error', 'Video not found')
		return False

params = getParameters(sys.argv[2])
get = params.get

cache = True

if get('act') == None:
	MainMenu()
elif get('act') == 'index':
	ListVideos(urls['index'])
elif get('act') == 'top40':
	ListVideos(urls['top40'])
elif get('act') == 'categories':
	Categories()
elif get('act') == 'category':
	ListVideos(urls['category'] % get('category_id'))
elif get('act') == 'playbyid':
	PlayById()
elif get('act') == 'search_videos':
	SearchVideos()
	cache = False
elif get('act') == 'search_videos_list':
	SearchVideosList()
elif get('act') == 'play':
	if get('vid') == None:
		params['vid'] = getUserInput()
	PlayVid(urllib.unquote_plus(get('vid')), urllib.unquote_plus(get('name')))

xbmcplugin.endOfDirectory(handle, succeeded=True, cacheToDisc=cache)

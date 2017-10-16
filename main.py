from globals import *
from silenceskip import silenceSkip
from download_nhl import download_nhl
from padding import padding

def createFullGameStream(stream_url, media_auth):
    #SD (800 kbps)|SD (1600 kbps)|HD (3000 kbps)|HD (5000 kbps)        
    bandwidth = ''
    bandwidth = QUALITY

    #Only set bandwidth if it's explicitly set
    if bandwidth != '':
        #Reduce convert bandwidth if composite video selected   
        if ('COMPOSITE' in stream_url or 'ISO' in stream_url) :
            if int(bandwidth) == 5000:
                bandwidth = '3500'
            elif int(bandwidth) == 1200:
                bandwidth = '1500'
                       
    #ARCHIVE
    stream_url = stream_url.replace(MASTER_FILE_TYPE, bandwidth+'K/'+bandwidth+'_complete-trimmed.m3u8') 

    return stream_url
    
                
def getAuthCookie():
    authorization = ''    
    try:
        cj = cookielib.LWPCookieJar('cookies.lwp')
        cj.load('cookies.lwp',ignore_discard=True)    

        #If authorization cookie is missing or stale, perform login    
        for cookie in cj:            
            if cookie.name == "Authorization" and not cookie.is_expired():            
                authorization = cookie.value 
    except:
        pass

    return authorization


def fetchStream(game_id, content_id,event_id):        
    stream_url = ''
    media_auth = ''    
   
    authorization = getAuthCookie()            
    
    if authorization == '':  
        login()
        authorization = getAuthCookie()   
        if authorization == '':
            return stream_url, media_auth

    cj = cookielib.LWPCookieJar('cookies.lwp') 
    cj.load('cookies.lwp',ignore_discard=True)         
    session_key = getSessionKey(game_id,event_id,content_id,authorization)    
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))   
        

    if session_key == '':
        return stream_url, media_auth
    elif session_key == 'blackout':
        msg = "The game you are trying to access is not currently available due to local or national blackout restrictions.\n Full game archives will be available 48 hours after completion of this game."
        tprint(msg)
        return stream_url, media_auth

    #Org
    url = 'https://mf.svc.nhl.com/ws/media/mf/v2.4/stream?contentId='+content_id+'&playbackScenario=HTTP_CLOUD_TABLET_60&platform=IPAD&sessionKey='+urllib.quote_plus(session_key)    
    req = urllib2.Request(url)       
    req.add_header("Accept", "*/*")
    req.add_header("Accept-Encoding", "deflate")
    req.add_header("Accept-Language", "en-US,en;q=0.8")                       
    req.add_header("Connection", "keep-alive")
    req.add_header("Authorization", authorization)
    req.add_header("User-Agent", UA_NHL)
    req.add_header("Proxy-Connection", "keep-alive")        

    response = opener.open(req)
    json_source = json.load(response)       
    response.close()
       

    if json_source['status_code'] == 1:
        if json_source['user_verified_event'][0]['user_verified_content'][0]['user_verified_media_item'][0]['blackout_status']['status'] == 'BlackedOutStatus':
            msg = "You do not have access to view this content. To watch live games and learn more about blackout restrictions, please visit NHL.TV"
            tprint(msg)
        else:
            stream_url = json_source['user_verified_event'][0]['user_verified_content'][0]['user_verified_media_item'][0]['url']    
            media_auth = str(json_source['session_info']['sessionAttributes'][0]['attributeName']) + "=" + str(json_source['session_info']['sessionAttributes'][0]['attributeValue'])
            session_key = json_source['session_key']
            setSetting(id='media_auth', value=media_auth) 
            #Update Session Key
            setSetting(id='session_key', value=session_key)   
    else:
        msg = json_source['status_message']
        tprint(msg)     
    
    # Add media_auth cookie
    ck = cookielib.Cookie(version=0, name='mediaAuth', value="" + media_auth.replace('mediaAuth=','') + "", port=None, port_specified=False, domain='.nhl.com', domain_specified=True, domain_initial_dot=True, path='/', path_specified=True, secure=False, expires=(int(time.time()) + 7500), discard=False, comment=None, comment_url=None, rest={}, rfc2109=False)
    cj = cookielib.LWPCookieJar('cookies.lwp')
    cj.load('cookies.lwp',ignore_discard=True)
    cj.set_cookie(ck)
    cj.save(ignore_discard=False)

    return stream_url, media_auth    
   



def getSessionKey(game_id,event_id,content_id,authorization):    
    #session_key = ''
    session_key = str(getSetting(id="session_key"))

    if session_key == '':        
        epoch_time_now = str(int(round(time.time()*1000)))    

        url = 'https://mf.svc.nhl.com/ws/media/mf/v2.4/stream?eventId='+event_id+'&format=json&platform=WEB_MEDIAPLAYER&subject=NHLTV&_='+epoch_time_now        
        req = urllib2.Request(url)       
        req.add_header("Accept", "application/json")
        req.add_header("Accept-Encoding", "deflate")
        req.add_header("Accept-Language", "en-US,en;q=0.8")                       
        req.add_header("Connection", "keep-alive")
        req.add_header("Authorization", authorization)
        req.add_header("User-Agent", UA_PC)
        req.add_header("Origin", "https://www.nhl.com")
        req.add_header("Referer", "https://www.nhl.com/tv/"+str(game_id)+"/"+event_id+"/"+content_id)
        
        response = urllib2.urlopen(req)
        json_source = json.load(response)   
        response.close()
        
        tprint("REQUESTED SESSION KEY")
        if json_source['status_code'] == 1:      
            if json_source['user_verified_event'][0]['user_verified_content'][0]['user_verified_media_item'][0]['blackout_status']['status'] == 'BlackedOutStatus':
                msg = "You do not have access to view this content. To watch live games and learn more about blackout restrictions, please visit NHL.TV"
                tprint(msg)
                session_key = 'blackout'
            else:    
                session_key = str(json_source['session_key'])
                setSetting(id='session_key', value=session_key)                              
        else:
            msg = json_source['status_message']
            tprint(msg)      
    return session_key  
    

def login():    
    #Check if username and password are provided    
    global USERNAME
    global PASSWORD
   
    if USERNAME != '' and PASSWORD != '':        
        cj = cookielib.LWPCookieJar('cookies.lwp') 
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))   

        try:
            cj.load('cookies.lwp',ignore_discard=True)
        except:
            pass

        #Get Token
        url = 'https://user.svc.nhl.com/oauth/token?grant_type=client_credentials'
        req = urllib2.Request(url)       
        req.add_header("Accept", "application/json")
        req.add_header("Accept-Encoding", "gzip, deflate, sdch")
        req.add_header("Accept-Language", "en-US,en;q=0.8")                                           
        req.add_header("User-Agent", UA_PC)
        req.add_header("Origin", "https://www.nhl.com")
        #from https:/www.nhl.com/tv?affiliated=NHLTVLOGIN
        req.add_header("Authorization", "Basic d2ViX25obC12MS4wLjA6MmQxZDg0NmVhM2IxOTRhMThlZjQwYWM5ZmJjZTk3ZTM=")

        response = opener.open(req, '')
        json_source = json.load(response)   
        authorization = getAuthCookie()
        if authorization == '':
            authorization = json_source['access_token']
        response.close()
 
        url = 'https://gateway.web.nhl.com/ws/subscription/flow/nhlPurchase.login'            
        login_data = '{"nhlCredentials":{"email":"'+USERNAME+'","password":"'+PASSWORD+'"}}'


        req = urllib2.Request(url, data=login_data, headers=
            {"Accept": "*/*",
             "Accept-Encoding": "gzip, deflate",
             "Accept-Language": "en-US,en;q=0.8",
             "Content-Type": "application/json",                            
             "Origin": "https://www.nhl.com",
             "Authorization": authorization,
             "Connection": "keep-alive",
             "User-Agent": UA_PC})     
       
        try:
            response = opener.open(req) 
        except HTTPError as e:
            tprint('The server couldn\'t fulfill the request.')
            tprint('Error code: ', e.code)  
            tprint(url)   
            
            #Error 401 for invalid login
            if e.code == 401:
                msg = "Please check that your username and password are correct"
                tprint(msg)

        response.close()
      

        cj.save(ignore_discard=True); 


def logout(display_msg=None):    
    cj = cookielib.LWPCookieJar('cookies.lwp')   
    try:  
        cj.load('cookies.lwp',ignore_discard=True)
    except:
        pass
        
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))                
    url = 'https://account.nhl.com/ui/rest/logout'
    
    req = urllib2.Request(url, data='',
          headers={"Accept": "*/*",
                    "Accept-Encoding": "gzip, deflate",
                    "Accept-Language": "en-US,en;q=0.8",
                    "Content-Type": "application/x-www-form-urlencoded",                            
                    "Origin": "https://account.nhl.com/ui/SignOut?lang=en",
                    "Connection": "close",
                    "User-Agent": UA_PC})

    try:
        response = opener.open(req) 
    except HTTPError as e:
        tprint('The server couldn\'t fulfill the request.')
        tprint('Error code: ', e.code)
        tprint(url)

    response.close()

    if display_msg == 'true':
        setSetting(id='session_key', value='') 

def getGameId():
    current_time = datetime.now()
    startDate = (current_time.date() - timedelta(days=7)).isoformat()
    endDate = (current_time.date()).isoformat()
    tprint('Checking for new game...')
    url = 'http://statsapi.web.nhl.com/api/v1/schedule?expand=schedule.game.content.media.epg&startDate='+startDate+'&endDate=' + endDate + '&site=en_nhl&platform=playstation'
    tprint('Looking up games @ ' + url)
    #url = 'http://statsapi.web.nhl.com/api/v1/schedule?expand=schedule.teams,schedule.linescore,schedule.scoringplays,schedule.game.content.media.epg&startDate=2016-04-10&endDate=2016-04-10&site=en_nhl&platform=playstation'    
    req = urllib2.Request(url)    
    req.add_header('Connection', 'close')
    req.add_header('User-Agent', UA_PS4)
    response = urllib2.urlopen(req)
    json_source = json.load(response)   
    response.close()
    
    lastGame = getSetting('lastGameID')
    gameToGet = None
    favTeamHomeAway = 'HOME'

    # Go through all games in the file and look for the next game
    for jd in json_source['dates']:
        for jg in jd['games']:
            homeTeamId = jg['teams']['home']['team']['id']
            awayTeamId = jg['teams']['away']['team']['id']
            gameID = jg['gamePk']
            if((str(homeTeamId) == TEAMID or str(awayTeamId) == TEAMID) and gameID > lastGame):
                gameToGet = jg
                if(str(awayTeamId) == TEAMID):
                    favTeamHomeAway = 'AWAY'
                break
        if(gameToGet != None):
            break

    # If there is a game to get then find the best feed
    if(gameToGet != None):
        bestScore = -1
        bestEpg = None
        startDateTime = datetime.strptime(gameToGet['gameDate'],'%Y-%m-%dT%H:%M:%SZ')
        
        if('content' in gameToGet and 'media' in gameToGet['content'] and 'epg' in gameToGet['content']['media'] and 'items' in gameToGet['content']['media']['epg'][0]):
            for epg in gameToGet['content']['media']['epg'][0]['items']:
                score = 0
                if(epg['language'] == 'eng'):
                    score = score + 100
                if(epg['mediaFeedType'] == favTeamHomeAway):
                    score = score + 50
                if(score > bestScore):
                    bestScore = score
                    bestEpg = epg

        # If there isn't a bestEpg then treat it like an archive case
        if(bestEpg == None):
            bestEpg = {}
            bestEpg['mediaState'] = ''

        # If the feed is good to go then return the info
        if((bestEpg['mediaState'] == 'MEDIA_ON' or bestEpg['mediaState'] == 'MEDIA_ARCHIVE') and startDateTime <= datetime.utcnow()):
            gameID = gameToGet['gamePk']
            contentID = bestEpg['mediaPlaybackId']
            eventID = bestEpg['eventId']
            tprint("Found a game: " + str(gameID))
            return gameID, contentID, eventID
        # If it is not then figure out how long to wait and wait
        else:
            # If the game hasn't started then wait until the game has started
            if(startDateTime > datetime.utcnow()):
                waitUntil = startDateTime
                waitTime = (waitUntil - datetime.utcnow()).total_seconds()
                tprint("Game hasn't started yet. Waiting for " + str(waitTime/60) + ' minutes.')
                time.sleep(waitTime)
                return None, None, None
            # If game has started but isn't available yet then wait for 15 minutes
            else:
                waitTime = 2 * 60
                tprint("Game has started but isn't available yet. Waiting for " + str(waitTime/60) + ' minutes.')
                time.sleep(waitTime)
                return None, None, None
    # If there is no game in the file wait a day
    tprint("No game in latest json. Waiting a day.")
    waitTime = 86400
    time.sleep(waitTime)
    return None, None, None  

def reEncode(inputFile, outputFile):
    # Skip the first 5min
    command_first_half = 'ffmpeg -y -ss 300 -t 3600 -nostats -i ' + inputFile + ' -r 30 -vf scale=848x480 -c:v libx264 -profile:v high -preset veryslow -crf 26 -codec:a libopus -b:a 48k ' + outputFile + '_start.mkv'
    command_second_half = 'ffmpeg -y -ss 3900 -nostats -i ' + inputFile + ' -r 30 -vf scale=848x480 -c:v libx264 -profile:v high -preset veryslow -crf 26 -codec:a libopus -b:a 48k ' + outputFile + '_end.mkv'

    # Trigger phone encode first half
    subprocess.Popen(command_first_half, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True).wait()

    # Move to folder to dl from phone
    command = 'mv ' + outputFile + '_start.mkv /Volumes/raid/data/nhl/phone/' + outputFile + '_start.mkv'
    subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    tprint('First Half Phone Encode Done...')

    # Trigger phone encode second half
    subprocess.Popen(command_second_half, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True).wait()
    
    # Move to folder to dl from phone
    command = 'mv ' + outputFile + '_end.mkv /Volumes/raid/data/nhl/phone/' + outputFile + '_end.mkv'
    subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    tprint('Second Half Phone Encode Done...')


def moveToHTPC(sourceFile):
    # Copy to htpc
    command = 'mv ' + sourceFile + ' /Volumes/raid/data/nhl/' + sourceFile
    subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)

#-----------------------------MAIN CODE--------------------#    
# Find the gameID or wait until one is ready


while(True):
    gameID = None
    while(gameID == None):
        gameID, contentID, eventID = getGameId()

    # When one is found then fetch the stream and save the cookies for it
    tprint('Fetching the stream URL')
    stream_url, media_auth = fetchStream(gameID, contentID, eventID)
    saveCookiesAsText()

    # Download stream_url
    outputFile = str(gameID) + '_raw.mkv'
    download_nhl(stream_url, outputFile)

    #Remove silence
    tprint("Removing silence...")
    newFileName = str(gameID) + '.mkv'
    silenceSkip(outputFile, newFileName) 

    setSetting('lastGameID', gameID)

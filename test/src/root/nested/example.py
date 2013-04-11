'''
Created on 05.03.2013

@author: Paul Crease
'''
from bs4 import BeautifulSoup
import re
import psycopg2
import urllib2
global ID

def addToDatabase(dataObject):
    
    conn_string = "host='localhost' dbname='postgres' user='postgres' password='platinum'"
 
    # print the connection string we will use to connect
    #print "Connecting to database\n    ->%s" % (conn_string)
 
    # get a connection, if a connect cannot be made an exception will be raised here
    conn = psycopg2.connect(conn_string)
 
    # conn.cursor will return a cursor object, you can use this cursor to perform queries
    cursor = conn.cursor()
    #print "Connected!\n"
    
    song_link=dataObject[0]
    if song_link.__len__()>250:
        song_link=song_link[:249]
    
    artist_name=dataObject[1]
    if artist_name.__len__()>100:
        artist_name=artist_name[:99]
    
    song_title=dataObject[2]
    if song_title.__len__()>100:
        song_title=song_title[:99]    
    
    genre=dataObject[3]
    if genre.__len__()>100:
        genre=genre[:100]    
    
    lyrics=dataObject[4]
    
    
    
    #print artist_name+" "+song_title+" "+song_link+" "+genre+" "+lyrics
    cursor.execute("INSERT INTO song_lyrics(artist_name ,song_title,song_link,genre,lyrics) VALUES (%s, %s,%s, %s,%s)",(artist_name, song_title,song_link,genre,lyrics))
    conn.commit()
    # execute our Query
    #cursor.execute("SELECT * FROM song_lyrics")
 
    # retrieve the records from the database
    #records = cursor.fetchall()
    cursor.close()
    conn.close()
    # print out the records using pretty print
    # note that the NAMES of the columns are not shown, instead just indexes.
    # for most people this isn't very useful so we'll show you how to return
    # columns as a dictionary (hash) in the next example.

    
def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
        return False
    elif re.match('<!--.*-->', str(element)):
        return False
    return True

def getArtistSongGenre(pageText, dataObject):
    for line in pageText:
        if line.find("cf_page_artist")>-1:
            #print line+str(line.find("cf_page_artist"))
            artist=line[line.find("cf_page_artist")+18:line.find("cf_page_song")-3]
            song=line[line.find("cf_page_song")+16:line.find("cf_page_genre")-3]
            genre=line[line.find("cf_page_genre")+17:line.find("cf_adunit_id")-3]
            
            dataObject.append(artist)
            dataObject.append(song)
            dataObject.append(genre)
            break

def getLyrics(songString, dataObject):
    Lyricurl="http://www.sing365.com/"+songString
    
    try:
        LyricPage=urllib2.urlopen(Lyricurl)
    except urllib2.HTTPError, err:
       if err.code == 404:
           print "error 404"
           return        
       else:
           print "error other than 404"
           return 
       
    lyricPageSoup = BeautifulSoup(LyricPage.read())
    lyricsDiv=lyricPageSoup.findAll(text=True)
    getArtistSongGenre(lyricsDiv, dataObject)
    concatText=""
        
    visible_texts = filter(visible, lyricsDiv)
    for text in visible_texts:
        if text.find("Please")>-1:
            dataObject.append(concatText)
            
            #for dObject in dataObject:
                #print "33"+dObject
            addToDatabase(dataObject)
            #print "end of song\n"
            break        
        else:
            if text.__len__()>1 and text.find("Lyric")==-1 and text.find("Review")==-1:
                concatText=concatText+text.strip('\r\n')
                concatText=concatText+", "
                #print concatText
                continue
        
    #for lyricLine in lyricsDiv:
            #print(str(lyricLine))
            #matches=re.findall(r'\"(.+?)\"',str(lyricLine))
            #if lyricLine.find("page_artist")>0:
            #if lyricLine.string!=None:    
            # print lyricLine
    

def getSongList(hrefString):
    
    Listurl="http://www.sing365.com/"+hrefString
    songListPage=urllib2.urlopen(Listurl)
    soupSongListPage = BeautifulSoup(songListPage.read())
    songs=soupSongListPage.findAll('a')
    
    
    for song in songs:    
        songString= song['href']
        if songString.find("lyrics")>0:
            dataObject = []
            dataObject.append(songString)
            #print "song title = "+ songString
            getLyrics(songString, dataObject)
    
#print soup.prettify(None, "minimal")
for i in range(1,12):
    
    if i==1:
        url="http://www.sing365.com/artist/m.html"
    else:
        url="http://www.sing365.com/artist/m"+str(i)+".html"
        
    page=urllib2.urlopen(url)
    soup = BeautifulSoup(page.read())
    artists=soup.findAll('a')
                
    for artist in artists:
        
            hrefString= artist['href']
            print hrefString
            
            if hrefString.find("lyrics")>0:
                print "artist = "+hrefString
                #dataObject.append(hrefString)
                getSongList(hrefString)
            
                


#V1.1 - fixed bug caused by people leaving playlists open at the forefront when a scheduled show starts.
import requests
import tkinter as tk
import tkinter.font as tkFont
import datetime

endpoint = "http://172.17.251.100:8081/"
formatted_time = ""
next_live = ""
elapsed = 0
currentclipduration = 0
currentclipname = ""

def otavgetplaylist():
    playuniqueid = ''
    clipindex = 1
    clipnumber = []
    cliptype = []
    clipname = []
    clipduration = []
    clipstart = []
    clipid = []
    isdisabled = []
    clipstartcode = []
    next_live = ""
    try:
        currentplayback = requests.get("http://172.17.251.100:8081/playback/playing")
        currentplaybackjson = currentplayback.json()
        uniqueid = currentplaybackjson['playlist_unique_id']
        playuniqueid = currentplaybackjson['item_unique_id']
        playlistitems = "http://172.17.251.100:8081/playlists/" + uniqueid + "/items"
        status = requests.get(playlistitems)
        statusjson = status.json()
    except:
        return [clipnumber, cliptype, clipname, clipduration, clipstart, clipid, playuniqueid, isdisabled, next_live,
                clipstartcode]
    else:
        for x in statusjson:
            if x['clip_type'] != 3:
                clipnumber.append(str(clipindex))
                clipduration.append(x['duration_timecode'])
                clipstart.append(x['displayed_start_timecode'])
                clipid.append(x['unique_id'])
                clipstartcode.append(x['relative_start_time'])
                cliptype.append(x['clip_type'])
            else:
                clipnumber.append(str(clipindex))
                clipduration.append("")
                clipstart.append("")
                clipid.append("")
                clipstartcode.append([""])
                cliptype.append(x['clip_type'])
            if x['name'] != "":
                clipname.append(x['name'])
            else:
                clipname.append(x["filename"])
            clipindex += 1
            if 'is_disabled' in x and x['is_disabled']:
                isdisabled.append('disabled')
            else:
                isdisabled.append('enabled')

        return [clipnumber, cliptype, clipname, clipduration, clipstart, clipid, playuniqueid, isdisabled, next_live,
                clipstartcode]

def playlistitems():
    global formatted_time
    global next_live
    global elapsed
    playlist = otavgetplaylist()
    clipindex = 0
    lives = 0
    currentlive = 0
    totallives = 0
    for x in playlist[0]:
        if "WX" in playlist[2][clipindex] and playlist[1][clipindex] != 3:
            playlist[1][clipindex] = 4
            if int(playlist[9][clipindex]) > int(elapsed) and lives <1:
                next_live = int(playlist[9][clipindex]) - int(elapsed)
                lives+=1
            else:
                currentlive += 1
            totallives+=1
            if currentlive == totallives:
                next_live = -1
        clipindex+=1
def otavplaystatus():
    try:
        status = requests.get("http://172.17.251.100:8081/playback/playing")
        statusjson = status.json()
    except:
        return ['STOPPED', '','']
    else:
        if statusjson['playback_status'] != 'Stopped' and statusjson['playback_status'] != 'Closed':
            if 'item_display_name' in statusjson:
                return [statusjson['item_display_name'],statusjson['item_remaining'], statusjson['playlist_elapsed']]
            else:
                try:
                    return[statusjson['item_filename'],statusjson['item_remaining'],statusjson['playlist_elapsed']]
                except:
                    return ['STOPPED', '','']
        else:
            return['STOPPED', '','']


def update_playing():
    current_time = datetime.datetime.now()
    hours = current_time.strftime("%H")
    minutes = current_time.strftime('%M')
    current_formatted_time = hours + ':' + minutes
    global next_live
    global formatted_time
    global elapsed
    global currentclipduration
    global currentclipname
    updatetime = otavplaystatus()
    try:
        currentclipduration = int(updatetime[1])
        currentclipname = str(updatetime[0])
    except:
        currentclipduration = 0
    otavgetplaylist()
    playlistitems()
    try:
        elapsed = int(updatetime[2])
    except:
        elapsed = 0
    if "WX" in currentclipname and updatetime[0] != "STOPPED":
        timer1["fg"] = 'red'
        timer1["text"] = ("LIVE: " + str(datetime.timedelta(seconds=int(currentclipduration))))
    else:
        if updatetime[0] != 'STOPPED':
            if next_live == -1:
                timer1["fg"] = 'yellow'
                timer1["text"] = "NO LIVE LEFT IN SHOW"
            elif next_live != -1:
                timer1["fg"] = 'orange'
                timer1["text"] = ("NEXT LIVE IN: " + str(datetime.timedelta(seconds=int(next_live))))
        else:
            timer1["fg"] = 'white'
            timer1["text"] = current_formatted_time
    root.after(300, update_playing)



root = tk.Tk()
# setting title
# setting window size
width = 1280
height = 720
screenwidth = root.winfo_screenwidth()
screenheight = root.winfo_screenheight()
alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
root.geometry(alignstr)
root.resizable(width=True, height=True)
root.configure(bg='black')
root.overrideredirect(1)

timer1 = tk.Label(root)
ft = tkFont.Font(family='Proxima', size=70)
timer1["font"] = ft
timer1["fg"] = "red"
timer1["bg"] = "black"
timer1["text"] = "00:00:00"
timer1["justify"] = "center"
timer1.place(x=10, y=10, width=1280, height=80)

update_playing()
root.mainloop()

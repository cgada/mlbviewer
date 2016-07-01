#!/usr/bin/env python
import sys
import datetime
import time
sys.path.insert(0, '/home/cgada/Projects/mlbviewer')

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from MLBviewer import *


def get_date(mycfg):
    now = datetime.datetime.now()
    shift = mycfg.get('time_offset')
    gametime = MLBGameTime(now, shift=shift)

    if shift is not None and shift != '':
        offset = gametime.customoffset(time_shift=shift)
        now = now - offset
    else:
        tt = time.localtime()
        localzone = (time.timezone, time.altzone)[tt.tm_isdst]
        localoffset = datetime.timedelta(0, localzone)
        easternoffset = gametime.utcoffset()
        offset = localoffset - easternoffset
        now = now + offset
        # morning people may want yesterday's highlights, boxes, lines, etc
        # before day games begin.
        if now.hour < 9:
            dif = datetime.timedelta(days=1)
            now = now - dif
    return now

def get_listing(mycfg):
    now = get_date(mycfg)
    startdate = (now.year, now.month, now.day)
    mysched = MLBSchedule(
        ymd_tuple=startdate, time_shift=mycfg.get('time_offset'))

    try:
        available = mysched.getListings(
            mycfg.get('speed'), mycfg.get('blackout'))
    except (KeyError, MLBXmlError):
        if cfg['debug']:
            raise
        available = []
        print "There was a parser problem with the listings page"
        sys.exit()

    print "MLB.TV Listings for " +\
        str(mysched.month) + '/' +\
        str(mysched.day) + '/' +\
        str(mysched.year)

    schedulelist = []
    for n in range(len(available)):
        home = available[n][0]['home']
        away = available[n][0]['away']
        s = available[n][1].strftime('%l:%M %p') + ': ' +\
            ' '.join(TEAMCODES[away][1:]).strip() + ' at ' +\
            ' '.join(TEAMCODES[home][1:]).strip()
        schedulelist.append(s)
    return schedulelist


if __name__ == "__main__":
    myconfdir = os.path.join(os.environ['HOME'], AUTHDIR)
    myconf = os.path.join(myconfdir, AUTHFILE)
    mydefaults = {'speed': DEFAULT_SPEED,
                  'video_player': DEFAULT_V_PLAYER,
                  'audio_player': DEFAULT_A_PLAYER,
                  'audio_follow': [],
                  'alt_audio_follow': [],
                  'video_follow': [],
                  'blackout': [],
                  'favorite': [],
                  'use_color': 1,
                  'favorite_color': 'cyan',
                  'free_color': 'green',
                  'division_color': 'red',
                  'highlight_division': 0,
                  'bg_color': 'xterm',
                  'show_player_command': 0,
                  'debug': 0,
                  'curses_debug': 0,
                  'wiggle_timer': 0.5,
                  'x_display': '',
                  'top_plays_player': '',
                  'max_bps': 2400,
                  'min_bps': 1200,
                  'live_from_start': 0,
                  'use_nexdef': 0,
                  'use_wired_web': 1,
                  'adaptive_stream': 0,
                  'coverage': 'home',
                  'show_inning_frames': 1,
                  'use_librtmp': 0,
                  'no_lirc': 0,
                  'postseason': 0,
                  'milbtv': 0,
                  'rss_browser': 'firefox -new-tab %s',
                  'flash_browser': DEFAULT_FLASH_BROWSER}

    mycfg = MLBConfig(mydefaults)
    try:
        os.lstat(myconf)
    except:
        try:
            os.lstat(myconfdir)
        except:
            dir = myconfdir
        else:
            dir = None
        mycfg.new(myconf, mydefaults, dir)

    mycfg.loads(myconf)
    listing = get_listing(mycfg)

    # Create a Qt application
    app = QApplication(sys.argv)

    # Our main window will be a QListView
    list = QListView()
    list.setWindowTitle('MLB Listings')
    list.setMinimumSize(600, 400)

    # Create an empty model for the list's data
    model = QStandardItemModel(list)

    for game in listing:
        # create an item with a caption
        item = QStandardItem(game)

        # Add the item to the model
        model.appendRow(item)

    # Apply the model to the list view
    list.setModel(model)

    # Show the window and run the app
    list.show()
    app.exec_()

import datetime
import time
import subprocess
import RPi.GPIO as GPIO
import urllib.request
import vlc
import re
from pygame import mixer
from bs4 import BeautifulSoup


def get_score(team):
    """
    Return the score of the selected team.

    Requires the Beautifulsoup4 library and Rpi.GPIO module.

    team = "team three letter abbreviation"
    The script is configured to work with www.nhl.com/ice/m_scores.htm
    and will need to be modified if other URLs are used.
    If the given team is not on the schedule to play 998 will be returned.
    """

    url = "http://www.nhl.com/ice/m_scores.htm"
    page = urllib.request.urlopen(url)
    soup = BeautifulSoup(page, "html.parser")
    team_list = soup.find('a', href=re.compile(team))
    try:
        for td in team_list.parent.find_next_siblings('td'):
            current_score = td.text 
            return int(current_score)
    except:
        current_score = 998
        return int(current_score)

def main():
    """
    Alert when a goal is scored by a specified team.

    Requires vlc on Raspberry Pi.

    If get_score() returns 0 there has not been a goal in the game so it is
    safe to reset old_score to 0.
    If get_score() returns 998 then the desired team is not on the schedule
    and the loop will wait one hour before restarting.
    If get_score() returns a reasonable score greater than old_score it will
    indicate a goal has been scored, triggering the sound and light and
    setting old_score equal to new_score.
    """

    # Set first old_score variable
    old_score = 0
    # Set first current hour and month variable
    now = datetime.datetime.now()
    hour = int(now.strftime("%H"))
    #month = now.month
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)  
    GPIO.setup(2, GPIO.OUT)  # Setup GPIO Pin to 2

    continuous = True  # Loop to run 24/7/365
    while continuous:
        """while month in (6, 7, 8, 9):
            time.sleep(86400)
            now = datetime.datetime.now()
            month = now.month"""
        while hour < 13:
            time.sleep(120)
            now = datetime.datetime.now()
            hour = int(now.strftime("%H"))
        while hour >= 13:
            try: 
                new_score = get_score("SJS")
            except:
                new_score = 999;
            #new_score = 1
            print(new_score)
            if new_score == 0:
                old_score = new_score
            elif new_score >= 998:  # Team not on schedule wait 24 hours 
                time.sleep(86400)
            elif new_score > old_score:  # Goal has been scored
                print('GOAL!:' + str(new_score))
                GPIO.output(2, True)  # Light ON
                p= vlc.MediaPlayer("SJGoalHorn.mp3")
                p.play() # Play sound
                time.sleep(36)
                GPIO.output(2, False)     # Light OFF
                old_score = new_score 
            now = datetime.datetime.now()  # Update hour
            hour = int(now.strftime("%H"))
            time.sleep(2)  

if __name__ == "__main__":
    main()

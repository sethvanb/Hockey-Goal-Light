import datetime
import time
import RPi.GPIO as GPIO
import vlc
import requests

# Run with cronjob at 8am Eastern

def get_todays_game(team):
    try:
        API_URL = "https://statsapi.web.nhl.com/api/v1"
        response = requests.get(API_URL + "/schedule?startDate=2023-01-16", params={"Content-Type": "application/json"})
        data = response.json()
        games = data['dates'][0]['games']
        for game in games:
            if game['teams']['away']['team']['name'] == team or game['teams']['home']['team']['name'] == team: 
                return game['gameDate']
        return None
    except:
        return None

def get_score(team):
    try:
        API_URL = "https://statsapi.web.nhl.com/api/v1"
        response = requests.get(API_URL + "/schedule?startDate=2023-01-16", params={"Content-Type": "application/json"})
        data = response.json()
        games = data['dates'][0]['games']
        for game in games:
            if game['status']['detailedState'] == 'Final':
                return 998
            if game['status']['detailedState'] == 'Pre-Game':
                return 997
            if game['status']['detailedState'] == 'In Progress':
                if game['teams']['away']['team']['name'] == team: 
                    return game['teams']['away']['score']
                elif game['teams']['home']['team']['name'] == team: 
                    return game['teams']['home']['score']
    except:
        return 999

def main():
    # team = 'Boston Bruins' 
    team = 'San Jose Sharks'
    game_time = get_todays_game(team)
    now = datetime.datetime.utcnow()
    tomorrow = now.replace(hour=0, minute=0, second=0) + datetime.timedelta(days=1)
    month = now.month
    if game_time and (month < 6 or month > 9):
        game_time = datetime.datetime.fromisoformat(game_time[:-1])
        sleepTime = (game_time-now).total_seconds()
        if sleepTime > 0:
            time.sleep(sleepTime)

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)  
        GPIO.setup(2, GPIO.OUT)  # Setup GPIO Pin to 2

        old_score = 0
        errors = 0
        pregame = 0
        gameStart = 0
        # on_power_play = False
        now = datetime.datetime.now()
        while now < tomorrow:
            new_score = get_score(team)
            # {new_score, power_play} = get_score(team)
            if new_score >= 999:  # Error occurred
                errors += 1
                if errors >= 5:
                    return 1
            elif new_score == 997:
                if pregame == 0:
                    pregame = 1
                    print('PRE-GAME')
                return 0
            elif new_score == 998:
                print('FINAL')
                print('errors ' + str(errors))
                return 0
            elif new_score == 0:
                if gameStart == 0:
                    gameStart = 1
                    print('GAME START')
                    GPIO.output(2, True)  # Light ON
                    p = vlc.MediaPlayer("GameStart.mp3")
                    p.play()
                    time.sleep(5)
                    GPIO.output(2, False)     # Light OFF
            elif new_score > old_score:  # Goal has been scored
                print(new_score)
                print('GOAL!')
                GPIO.output(2, True)  # Light ON
                p = vlc.MediaPlayer("SJGoalHorn.mp3")
                p.play() # Play Goal Song
                time.sleep(36)
                GPIO.output(2, False)     # Light OFF
                old_score = new_score

            # if power_play and not on_power_play:
            #     print("POWER PLAY!")
            #     #p = vlc.MediaPlayer("SJPowerPlay.mp3")
            #     # p.play() # Play power play Song
            #     on_power_play = True
            # elif not power_play and on_power_play:
            #     on_power_play = False
            time.sleep(3)
            now = datetime.datetime.now()

if __name__ == "__main__":
    main()

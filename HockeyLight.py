import datetime
import time
import RPi.GPIO as GPIO
import vlc
# import re
# from bs4 import BeautifulSoup
# from selenium import webdriver
# from selenium.webdriver.common.by import By

# Run with cronjob at 8am Eastern

def get_todays_game(team):
    return "Now"
    try:
        driver.get("https://www.nhl.com/scores")
        date_button = driver.find_element(By.CLASS_NAME, "datepicker__button")
        driver.execute_script("arguments[0].click();", date_button)
        today_button = driver.find_element(By.CLASS_NAME, "today")
        driver.execute_script("arguments[0].click();", today_button)
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        game_times = soup.find_all('p', {"class": "g5-component--nhl-scores__status-game-time"})
        team_names = soup.find_all('span', {"class": "g5-component--nhl-scores__team-name"})
        for i in range(len(team_names)):
            if team_names[i].get_text() == team:
                return game_times[i//2].get_text()
        return None
    except:
        return None

def get_score(team):
    try:
        driver.get("https://www.nhl.com/scores")
        date_button = driver.find_element(By.CLASS_NAME, "datepicker__button")
        driver.execute_script("arguments[0].click();", date_button)
        today_button = driver.find_element(By.CLASS_NAME, "today")
        driver.execute_script("arguments[0].click();", today_button)
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        if soup.find('span', text=re.compile(team)).parent.parent.parent.parent.parent.find('span', text=re.compile('Final')):
            return 998
        return int(soup.find('span', text=re.compile(team)).parent.parent.find_next_sibling().get_text())
    except:
        return 999

def main():
    team = 'Kraken' # 'Sharks'
    game_time = get_todays_game(team)
    now = datetime.datetime.now()
    tomorrow = now.replace(hour=0, minute=0, second=0) + datetime.timedelta(days=1)
    month = now.month
    if game_time and (month < 6 or month > 9):
        h = int(game_time[0 : game_time.index(":")]) - 3
        m = int(game_time[game_time.index(":")+1 : game_time.index(":")+3])
        if game_time.find("PM"):
            h = h + 12
        game_time = now.replace(hour=h, minute=m)
        time.sleep((game_time-now).total_seconds())

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)  
        GPIO.setup(2, GPIO.OUT)  # Setup GPIO Pin to 2

        old_score = 0
        errors = 0
        # on_power_play = False
        now = datetime.datetime.now()
        while now < tomorrow:
            new_score = get_score(team)
            # {new_score, power_play} = get_score(team)
            print(new_score)
            if new_score >= 999:  # Error occurred
                errors += 1
                if errors >= 5:
                    return 1
            elif new_score == 998:
                print('FINAL')
                return 0
            elif new_score > old_score:  # Goal has been scored
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

            now = datetime.datetime.now()

if __name__ == "__main__":
    main()

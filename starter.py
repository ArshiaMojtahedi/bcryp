from cv2 import cv2
import numpy as np
import mss
import pyautogui
import time
import sys
from random import randint
import yaml
#import requests
import solveCapModule

intro = """
>>---> Pressione ctrl + c ou feche a janela para finalizar o Robozinho 
>>---> Some configs can be fount in the config.yaml file.
"""

print(intro)

if __name__ == '__main__':
    stream = open("config.yaml", 'r')
    c = yaml.safe_load(stream)
    
ct = c['threshold']
pyautogui.PAUSE = c['time_intervals']['interval_between_moviments']
pyautogui.FAILSAFE = True
hero_clicks = 0
login_attempts = 0
last_log_is_progress = False

#imagens necessarias do jogo
go_work_img = cv2.imread('targets/go-work.png')
commom_img = cv2.imread('targets/commom-text.png')
arrow_img = cv2.imread('targets/go-back-arrow.png')
hero_img = cv2.imread('targets/hero-icon.png')
x_button_img = cv2.imread('targets/x.png')
teasureHunt_icon_img = cv2.imread('targets/treasure-hunt-icon.png')
ok_btn_img = cv2.imread('targets/ok.png')
connect_wallet_btn_img = cv2.imread('targets/connect-wallet.png')
select_wallet_hover_img = cv2.imread('targets/select-wallet-1-hover.png')
select_metamask_no_hover_img = cv2.imread('targets/select-wallet-1-no-hover.png')
sign_btn_img = cv2.imread('targets/select-wallet-2.png')
new_map_btn_img = cv2.imread('targets/new-map.png')
green_bar = cv2.imread('targets/green-bar.png')
full_stamina = cv2.imread('targets/full-stamina.png')
puzzle_img = cv2.imread('targets/puzzle.png')
piece = cv2.imread('targets/piece.png')
robot = cv2.imread('targets/robot.png')
slider = cv2.imread('targets/slider.png')

def logger(message, progress_indicator = False):
    global last_log_is_progress

    if progress_indicator:
        if not last_log_is_progress:
            last_log_is_progress = True
            sys.stdout.write('\n => .')
            sys.stdout.flush()
        else:
            sys.stdout.write('.')
            sys.stdout.flush()
        return

    if last_log_is_progress:
        sys.stdout.write('\n\n')
        sys.stdout.flush()
        last_log_is_progress = False

    datetime = time.localtime()
    formatted_datetime = time.strftime("%d/%m/%Y %H:%M:%S", datetime)
    formatted_message = "[{}] \n => {} \n\n".format(formatted_datetime, message)
    print(formatted_message)

    if (c['save_log_to_file'] == True):
        logger_file = open("logger.log", "a")
        logger_file.write(formatted_message)
        logger_file.close()

    return True

def clickBtn(img,name=None, timeout=3, threshold = ct['default']):
    logger(None, progress_indicator=True)
    if not name is None:
        pass
    start = time.time()
    clicked = False
    while(not clicked):
        matches = positions(img, threshold=threshold)
        if(len(matches)==0):
            hast_timed_out = time.time()-start > timeout
            if(hast_timed_out):
                if not name is None:
                    pass
                return False
            continue

        x,y,w,h = matches[0]
        pyautogui.moveTo(x+w/2,y+h/2,1)
        pyautogui.click()
        solveCapModule.solveCaptcha()                         
        return True

def printSreen():
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        sct_img = np.array(sct.grab(monitor))
        return sct_img[:,:,:3]

def positions(target, threshold=ct['default']):
    img = printSreen()
    result = cv2.matchTemplate(img.astype(np.uint8),target,cv2.TM_CCOEFF_NORMED)    
    w = target.shape[1]
    h = target.shape[0]

    yloc, xloc = np.where(result >= threshold)

    rectangles = []
    for (x, y) in zip(xloc, yloc):
        rectangles.append([int(x), int(y), int(w), int(h)])
        rectangles.append([int(x), int(y), int(w), int(h)])

    rectangles, weights = cv2.groupRectangles(rectangles, 1, 0.2)
    return rectangles

def scroll():

    commoms = positions(commom_img, threshold = ct['commom'])
    if (len(commoms) == 0):
        return
    x,y,w,h = commoms[len(commoms)-1]

    pyautogui.moveTo(x,y,1)

    if not c['use_click_and_drag_instead_of_scroll']:
        pyautogui.scroll(-c['scroll_size'])
    else:
        pyautogui.dragRel(0,-c['click_and_drag_amount'],duration=1, button='left')


def clickButtons():
    buttons = positions(go_work_img, threshold=ct['go_to_work_btn'])
    for (x, y, w, h) in buttons:
        pyautogui.moveTo(x+(w/2),y+(h/2),1)
        pyautogui.click()
        global hero_clicks
        hero_clicks = hero_clicks + 1
        if hero_clicks > 20:
            logger('too many hero clicks, try to increase the go_to_work_btn threshold')
            return
    return len(buttons)

def isWorking(bar, buttons):
    y = bar[1]

    for (_,button_y,_,button_h) in buttons:
        isBelow = y < (button_y + button_h)
        isAbove = y > (button_y - button_h)
        if isBelow and isAbove:
            return False
    return True

def clickGreenBarButtons():
    offset = 130
    green_bars = positions(green_bar, threshold=ct['green_bar'])
    logger('%d green bars detected' % len(green_bars))
    buttons = positions(go_work_img, threshold=ct['go_to_work_btn'])
    logger('%d buttons detected' % len(buttons))

    not_working_green_bars = []
    for bar in green_bars:
        if not isWorking(bar, buttons):
            not_working_green_bars.append(bar)
    if len(not_working_green_bars) > 0:
        logger('%d buttons with green bar detected' % len(not_working_green_bars))
        logger('Clicking in %d heroes.' % len(not_working_green_bars))

    for (x, y, w, h) in not_working_green_bars:
        pyautogui.moveTo(x+offset+(w/2),y+(h/2),1)
        pyautogui.click()
        global hero_clicks
        hero_clicks = hero_clicks + 1
        if hero_clicks > 20:
            logger('too many hero clicks, try to increase the go_to_work_btn threshold')
            return
    return len(not_working_green_bars)

def clickFullBarButtons():
    offset = 100
    full_bars = positions(full_stamina, threshold=ct['default'])
    buttons = positions(go_work_img, threshold=ct['go_to_work_btn'])

    not_working_full_bars = []
    for bar in full_bars:
        if not isWorking(bar, buttons):
            not_working_full_bars.append(bar)

    if len(not_working_full_bars) > 0:
        logger('Clicking in %d heroes.' % len(not_working_full_bars))

    for (x, y, w, h) in not_working_full_bars:
        pyautogui.moveTo(x+offset+(w/2),y+(h/2),1)
        pyautogui.click()
        global hero_clicks
        hero_clicks = hero_clicks + 1

    return len(not_working_full_bars)

def goToHeroes():
    if clickBtn(arrow_img):
        global login_attempts
        login_attempts = 0

    clickBtn(hero_img)

def goToGame():
    clickBtn(x_button_img)
    clickBtn(x_button_img)
    clickBtn(teasureHunt_icon_img)

def refreshHeroesPositions():
    clickBtn(arrow_img)
    clickBtn(teasureHunt_icon_img)
    clickBtn(teasureHunt_icon_img)

def login():
    global login_attempts
          
    if login_attempts > 3:
        logger('Too many login attempts, refreshing.')
        login_attempts = 0
        pyautogui.hotkey('ctrl','f5')
        return
        
    if clickBtn(connect_wallet_btn_img, name='connectWalletBtn', timeout = 10):
        solveCapModule.solveCaptcha()
        login_attempts = login_attempts + 1
        logger('Connect wallet button detected, logging in!')
        time.sleep(2)
    
    if clickBtn(sign_btn_img, name='sign button', timeout=8):
        login_attempts = login_attempts + 1
        time.sleep(randint(3,5))
        if clickBtn(teasureHunt_icon_img, name='teasureHunt', timeout = 15):
            login_attempts = 0
        return
    
    if not clickBtn(select_metamask_no_hover_img, name='selectMetamaskBtn'):
        if clickBtn(select_wallet_hover_img, name='selectMetamaskHoverBtn', threshold = ct['select_wallet_buttons'] ):
            pass
    
    else:
        pass
    
    if clickBtn(sign_btn_img, name='signBtn', timeout = 20):
        login_attempts = login_attempts + 1
            
        if clickBtn(teasureHunt_icon_img, name='teasureHunt', timeout=25):
            login_attempts = 0
    
    if clickBtn(ok_btn_img, name='okBtn', timeout=5):
        pass

def refreshHeroes():
    solveCapModule.solveCaptcha()
    goToHeroes()
    solveCapModule.solveCaptcha()

    if c['select_heroes_mode'] == "full":
        logger("Sending heroes with full stamina bar to work!")
    elif c['select_heroes_mode'] == "green":
        logger("Sending heroes with green stamina bar to work!")
    else:
        logger("Sending all heroes to work!")

    buttonsClicked = 1
    empty_scrolls_attempts = c['scroll_attemps']

    while(empty_scrolls_attempts >0):
        if c['select_heroes_mode'] == 'full':
            buttonsClicked = clickFullBarButtons()
        elif c['select_heroes_mode'] == 'green':
            buttonsClicked = clickGreenBarButtons()
        else:
            buttonsClicked = clickButtons()

        if buttonsClicked == 0:
            empty_scrolls_attempts = empty_scrolls_attempts - 1
        scroll()
        time.sleep(2)
    logger('{} heroes sent to work so far'.format(hero_clicks))
    goToGame()

def main():
    time.sleep(5)
    t = c['time_intervals']
    last = {
    "login" : 0,
    "heroes" : 0,
    "new_map" : 0,
    "refresh_heroes" : 0
    }

    while True:
        now = time.time()
        
        if now - last["heroes"] > randint(8,12) * 60:
            last["heroes"] = now
            logger('Sending heroes to work.')
            refreshHeroes()        
        
        if now - last["login"] > randint(2,5) * 60:
            logger("Checking if game has disconnected.")
            sys.stdout.flush()
            last["login"] = now
            login()
            time.sleep(2)
                    
        if now - last["login"] > randint(2,5) * 60:
            logger("Checking if game has disconnected.")
            sys.stdout.flush()
            last["login"] = now
            login()
                    
        if now - last["refresh_heroes"] > randint(5,25) * 60 :
            last["refresh_heroes"] = now
            logger('Refreshing Heroes Positions.')
            refreshHeroesPositions()     
                
        if now - last["new_map"] > randint(3,6):
            last["new_map"] = now
            if clickBtn(new_map_btn_img):
                with open('new-map.log','a') as new_map_log:
                    new_map_log.write(str(time.time())+'\n')
                logger('New Map button clicked!')

        logger(None, progress_indicator=True)
        sys.stdout.flush()
        time.sleep(1)

main()
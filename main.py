import time
import speech_recognition as sr
import pytils
import config_friday
import tts
from fuzzywuzzy import fuzz
import datetime as dt
import os
import num2words
import webbrowser
import random
import pyautogui as pg
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume  # отслеживания звука
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pyowm import OWM
from playsound import playsound
import vosk
import sys
import sounddevice as sd
import queue
import json

r = sr.Recognizer()  # распознавания и вывод речи
m = sr.Microphone(device_index=1)


def start_fun():
    print(f"{config_friday.VA_NAME}, готов к работе!")
    playsound(os.getcwd() + "/sound3/run.wav")


start_fun()

model = vosk.Model("model_small")
sample_rate = 16000
device = 1
rec = vosk.KaldiRecognizer(model, sample_rate)
q = queue.Queue()


def q_callback(indata, status):
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))


duration = 10


def va_listen(callback):  # функция для реагирования
    global stream
    # sound_device библиотека для прослушивания
    stream = sd.InputStream(samplerate=sample_rate, blocksize=8000, device=device, dtype='int16',
                            channels=1, callback=q_callback)
    with stream:
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                callback(json.loads(rec.Result())["text"])


def fun_str_start():
    stream.start()




def va_respond(voice: str):
    print(voice)
    if voice.startswith(config_friday.VA_ALIAS):
        # обращаются к ассистенту
        cmd = recognize_cmd(filter_cmd(voice))
        if cmd['cmd'] not in config_friday.VA_CMD_LIST.keys():
            playsound(os.getcwd() + "/sound1/greet1.wav")
        else:
            # другие функции пятницы
            execute_cmd(cmd['cmd'])
            cmd_work(cmd['cmd'])
            cmd_game(cmd['cmd'])
            pc_config(cmd['cmd'])
            cmd_dialog(cmd['cmd'])


def filter_cmd(raw_voice: str):
    cmd = raw_voice
    for x in config_friday.VA_ALIAS:
        cmd = cmd.replace(x, "").strip()
    return cmd


def recognize_cmd(cmd: str):
    # нечеткое значения команд
    rc = {'cmd': '', 'percent': 0}
    for c, v in config_friday.VA_CMD_LIST.items():  # проходимся по названиям команд и самим команд
        for x in v:  # проходимся по значениям
            vrt = fuzz.ratio(cmd, x)  # сравнение как мы скажем команду и как она на самом деле
            if vrt > rc['percent']:
                rc['cmd'] = c
                rc['percent'] = vrt

    return rc


def time_fix():
    # функция для вывода времени и не большой оптимизации
    # если хочешь вывести время данного момента не забывать слово now
    x = dt.datetime.now().hour
    y = dt.datetime.now().minute

    arr = []
    for i in str(y):
        arr.append(int(i))

    if len(arr) == 1:
        text_time = f"Сейчас {num2words.num2words(x, lang='ru')}  ноль  {num2words.num2words(y, lang='ru')}"
        tts.va_speak(text_time)
    else:
        text_time = f"Сейчас {num2words.num2words(x, lang='ru')}  {num2words.num2words(y, lang='ru')} "
        tts.va_speak(text_time)
    pass


def fun_data_fix():
    z = []
    x = dt.datetime.now().day
    y = num2words.num2words(x, lang='ru')
    gen_month = pytils.dt.ru_strftime(u"%B", inflected=True)  # склонение месяца
    for i in y:
        if i == "ь":
            break
        z.append(i)
    k = "".join(z)
    tts.va_speak(f"{k}ое {gen_month}.")


def weather_fix():
    owm = OWM('a0b68be06e7f5b28a3fb4f9119e56c4b')  # ключ для соединения библиотеки
    mgr = owm.weather_manager()
    observation = mgr.weather_at_place('Saint Petersburg')  # указания места
    w = observation.weather  # записываем в переменную данные о погоде
    x = w.temperature('celsius')
    y = x['temp_max']
    rounted = round(y)
    temp = ''  # переменная для записи склонения градсов
    if rounted % 10 == 1 and rounted % 100 != 11:
        temp += 'граудс'
    elif rounted % 10 in [2, 3, 4] and rounted % 100 not in [12, 13, 14]:
        temp += 'градуса'
    else:
        temp += 'градусов'
    z = w.detailed_status
    if z == 'clouds':
        text_sky = 'пасмурно'
    else:
        text_sky = 'облак+ов, нет'
    text = f"Сейчас {num2words.num2words(rounted, lang='ru')} {temp}, {text_sky}"
    tts.va_speak(text)


def execute_cmd(cmd: str):
    if cmd == 'help':
        # help
        text = "Я умею: рассказывать анекдоты, и открывать сторонние приложенияя. "
        tts.va_speak(text)
        pass
    elif cmd == 'stop':
        stream.stop()
        playsound(os.getcwd() + '/sound7/greet3.wav')
        pass
    elif cmd == 'hot_word':
        playsound('F:/GTA5RP/Friday/sound1/greet1.wav')

    elif cmd == 'joke':
        jokes = ['Как смеются программисты? ... ехе ехе ехе',
                 'ЭсКьюЭль запрос заходит в бар, подходит к двум столам и спрашивает .. «м+ожно присоединиться?»',
                 'Программист это машина для преобразования кофе в код']
        tts.va_speak(random.choice(jokes))
    elif cmd == 'open_browser':
        playsound('F:/GTA5RP/Friday/sound1/greet1.wav')

        webbrowser.open("https://www.google.com")
    elif cmd == 'open_youtube':
        playsound('F:/GTA5RP/Friday/sound6/greet2.wav')
        webbrowser.open("https://www.youtube.com/")
    elif cmd == 'open_music':
        pg.click(x=1751, y=1059)
        time.sleep(1)
        pg.click(x=1744, y=965)
        time.sleep(1)
        pg.click(x=1686, y=849)
        pg.click(x=1717, y=725)
        time.sleep(1)
        playsound(os.getcwd() + '/sound7/greet3.wav')
        webbrowser.open("https://music.yandex.ru/home")
        time.sleep(4)
        pg.click(x=326, y=1001)
    elif cmd == 'conect':
        playsound(os.getcwd() + '/sound6/greet2.wav')
        pg.click(x=1751, y=1059)
        time.sleep(1)
        pg.click(x=1744, y=965)
        time.sleep(1)
        pg.click(x=1686, y=849)
        pg.click(x=1717, y=725)
    elif cmd == 'unconect':
        playsound(os.getcwd() + '/sound6/greet2.wav')
        pg.click(x=1751, y=1059)
        time.sleep(1)
        pg.click(x=1744, y=965)
        time.sleep(1)
        pg.click(x=1687, y=965)
        pg.click(x=1717, y=725)
    elif cmd == 'my_wave':
        pg.click(x=719, y=449)
    elif cmd == 'stop_music':
        pg.click(x=269, y=1008)
    elif cmd == 'next_music':
        pg.click(x=321, y=1004)
    elif cmd == 'time_now':
        return time_fix()
    elif cmd == 'data_now':
        return fun_data_fix()
    elif cmd == 'weather':
        return weather_fix()
    elif cmd == 'open_perp':
        webbrowser.open("https://www.perplexity.ai/")
        playsound('F:/GTA5RP/Friday/sound6/greet2.wav')



def pc_config(cmd: str):
    if cmd == 'close_pc':
        playsound(os.getcwd() + '/sound7/greet3.wav')
        os.system('shutdown -s -t 2')
    elif cmd == 'restart_pc':
        playsound(os.getcwd() + '/sound6/greet2.wav')
        os.system('shutdown /r /t 1')
    elif cmd == 'sleap_pc':
        playsound(os.getcwd() + '/sound1/greet1.wav')
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
    elif cmd == 'scrin_host':
        playsound(os.getcwd() + '/sound2/ok1.wav')
        pg.screenshot('F:/скриншоты/scrin.png')
        os.startfile('F:/скриншоты')
    elif cmd == 'sound_on':
        devices = AudioUtilities.GetSpeakers()  # получаем доступ к динамикам
        interface = devices.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None)  # активизируем интерфейс звука
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMasterVolumeLevel(0.0, None)  # управления громкостью (максимальный громкость)
        playsound(os.getcwd() + '/sound5/ok3.wav')
    elif cmd == 'sound_off':
        playsound(os.getcwd() + '/sound2/ok1.wav')
        devices = AudioUtilities.GetSpeakers()  # получаем доступ к динамикам
        interface = devices.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None)  # активизируем интерфейс звука
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMasterVolumeLevel(-43, None)  # управления громкостью (минимальной громкость)


def cmd_work(cmd: str):
    if cmd == "codewars":
        playsound(os.getcwd() + '/sound2/ok1.wav')
        webbrowser.open('https://www.codewars.com/kata/search/my-languages?q=&r%5B%5D=-8&r%5B%5D=-7&tags=Arrays&xids'
                        '=played&beta=false&order_by=popularity%20desc')
    elif cmd == 'work_mode':
        playsound(os.getcwd() + '/sound4/ok2.wav')
        os.startfile('C:/Users/kirill/AppData/Roaming/Telegram Desktop/Telegram.exe')


def cmd_game(cmd: str):
    if cmd == 'play_mode':
        playsound(os.getcwd() + '/sound2/ok1.wav')
        os.startfile('C:/control/DS4Windows/DS4Windows.exe')
        time.sleep(2)
        os.startfile('F:/Games/Stray/Stray.exe')
    elif cmd == 'open_steam':
        playsound(os.getcwd() + '/sound4/ok2.wav')
        os.startfile('C:/Program Files (x86)/Steam/steam.exe')
    elif cmd == 'game_pad_start':
        playsound(os.getcwd() + '/sound5/ok3.wav')
        os.startfile('C:/control/DS4Windows/DS4Windows.exe')


def cmd_dialog(cmd2: str):
    if cmd2 == "good":
        x = ["с+пасибо.", "спасибо моему разработчику.", "с+пасибо вы тоже."]
        tts.va_speak(random.choice(x))
    elif cmd2 == "un_good":
        x = ["Очень тонкое замечание.", "простите меня сэрр.", "учту"]
        tts.va_speak(random.choice(x))


# начать прослушивание команд
va_listen(va_respond)  # мы помещаем в слушание то что мы сказали

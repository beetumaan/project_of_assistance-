from __future__ import print_function
import datetime
import pickle
import os.path
import shutil
from time import sleep
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import time
import playsound
import pyttsx3
import speech_recognition as sr
import datetime
import os.path
import pytz
import subprocess

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
MONTHS = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november",
          "december"]
DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
DAY_EXTENTIONS = ["rd", "th", "st", "nd"]


def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()


def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        # r.pause_threshold = 1
        audio = r.listen(source)
    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-in')
        print(f"User said: {query}")
    except Exception as e:
        print(f"Exception by machine is {e}")
        print("Unable to Recognizing your voice.")
        return "None"

    return query.lower()


def usrname():
    speak("What should i call you sir")
    sleep(2)
    uname = get_audio()
    speak("Welcome Mister" + uname)
    # speak(uname)
    print("Welcome Mr." + uname)
    sleep(2)
    speak("How can i Help you, Sir")


def wishMe():
    hour = int(datetime.datetime.now().hour)
    if 0 <= hour < 12:
        speak("Good Morning Sir !")

    elif 12 <= hour < 18:
        speak("Good Afternoon Sir !")

    else:
        speak("Good Evening Sir !")

    name = ("skaai")
    speak("I am your Assistant" + name)


def authenticate_google():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)
    return service


def get_event(day, service):
    # Call the Calendar API
    date = datetime.datetime.combine(day, datetime.datetime.min.time())
    end_date = datetime.datetime.combine(day, datetime.datetime.max.time())
    utc = pytz.UTC
    date = date.astimezone(utc)
    end_date = end_date.astimezone(utc)

    speak(f'hold on Getting the events')
    events_result = service.events().list(calendarId='primary', timeMin=date.isoformat(), timeMax=end_date.isoformat(),
                                          singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        speak('No upcoming events found.')
    else:
        speak(f"you have {len(events)} on this day")
        for event in events:

            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])
            start_time = str(start.split("T")[1].split("-")[0])
            if int(start_time.split(":")[0]) < 12:
                start_time += "am"
            else:
                start_time = str(int(start_time.split(":")[0]) - 12)
                start_time += "pm"
            speak(event["summary"] + "at" + start_time)


def get_date(text):
    today = datetime.date.today()

    if text.count("today") > 0:
        return today

    tomorrow = datetime.date.today() + datetime.timedelta(days=1)

    if text.count("tomorrow") > 0:
        return tomorrow

    day = -1
    day_of_week = -1
    month = -1
    year = today.year

    for word in text.split():
        if word in MONTHS:
            month = MONTHS.index(word) + 1
        elif word in DAYS:
            day_of_week = DAYS.index(word)
        elif word.isdigit():
            day = int(word)
        else:
            for ext in DAY_EXTENTIONS:
                found = word.find(ext)
                if found > 0:
                    try:
                        day = int(word[:found])
                    except:
                        pass

    if month < today.month and month != -1:
        year = year + 1

    if month == -1 and day != -1:  # if we didn't find a month, but we have a day
        if day < today.day:
            month = today.month + 1
        else:
            month = today.month

    if month == -1 and day == -1 and day_of_week != -1:
        current_day_of_week = today.weekday()
        diff = day_of_week - current_day_of_week
        if diff < 0:
            diff += 7
            if text.count("next") >= 1:
                diff += 7

        return today + datetime.timedelta(diff)
    if day != -1:
        return datetime.date(month=month, day=day, year=year)


def note(text):
    date = datetime.datetime.now()
    file_name = str(date).replace(':', '-') + "-note.txt"
    f = open(file_name, 'w')
    f.write(text)

    subprocess.Popen(["notepad.exe", file_name])


WAKE = "hello bittu"
service = authenticate_google()
print("lets start")

END = "bye"

while True:
    text = get_audio()
    if text.count(WAKE) > 0:
        speak("I'm ready")
        text = get_audio()

        CLANDER_STRS = ["what do i have", "am i busy", "have plans", "have plan"]
        for phrases in CLANDER_STRS:
            if phrases in text.lower():
                date = get_date(text)
                if date:
                    get_event(date, service)
                else:
                    speak("I don't understand")

        NOTES_STRS = ["make a note", "write down", "notepad", "remember"]
        for phrases in NOTES_STRS:
            if phrases in text.lower():
                speak("what do i have to remember ?")
                note(get_audio())
                speak("i've made a note of that")



    if text.count(END) >0:
      speak("OK BYE BITTU")
      break

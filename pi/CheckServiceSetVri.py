import datetime
import json
import socket
import threading
import time
import urllib.request
import RPi.GPIO as GPIO
import json
import traceback

version = "1.1"

time.sleep(12)

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
uri = "https://healthlight.azurewebsites.net/api/GetLightInfo?code=65NUi6sEoREMPZt2uMaViIZ6KoqrbHWBxAJAgIw3IuVb/qyYjdQZow=="

class RELAY:
    RED = 13
    ORANGE = 19
    GREEN = 26
    ON = 6

GPIO.setup(RELAY.ON,GPIO.OUT)
GPIO.setup(RELAY.RED,GPIO.OUT)
GPIO.setup(RELAY.ORANGE,GPIO.OUT)
GPIO.setup(RELAY.GREEN,GPIO.OUT)

class LightState:
    class Light:
        def __init__(self, pin, on, pattern):
            self.Pin = pin
            self.On = on
            self.Pattern = pattern

    class Switch:
        StartTime = datetime.time(8, 00)
        EndTime = datetime.time(17, 00)
        Pin = RELAY.ON
    
    LightRed = Light(RELAY.RED, False, "solid")
    LightOrange = Light(RELAY.ORANGE, False, "solid")
    LightGreen = Light(RELAY.GREEN, True, "solid")
    Switch = Switch()

class BlinkThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""
    
    def __init__(self, name, lightState):
        super(BlinkThread, self).__init__()
        self.name = name
        self._stop_event = threading.Event()
        self.currentTime = time.time()
        self.state = True
        self.lightState = lightState

    def stop(self):
        self._stop_event.set()

    def join(self, *args, **kwargs):
        self.stop()
        super(BlinkThread,self).join(*args, **kwargs)

    def run(self):
        print ("Starting " + self.name)
        while not self._stop_event.is_set():
            if datetime.datetime.now().time() > self.lightState.Switch.StartTime and datetime.datetime.now().time() < self.lightState.Switch.EndTime :
                if time.time() - self.currentTime > 1:
                    self.currentTime = time.time()
                    threadLock.acquire()
                    try:
                        if self.state:
                            if lightState.LightRed.Pattern == "blink" and lightState.LightRed.On:
                                #print("Blinking red light")
                                GPIO.output(lightState.LightRed.Pin, 0)
                            if lightState.LightOrange.Pattern == "blink" and lightState.LightOrange.On:
                                #print("Blinking orange light")
                                GPIO.output(lightState.LightOrange.Pin, 0)
                            if lightState.LightGreen.Pattern == "blink" and lightState.LightGreen.On:
                                #print("Blinking green light")
                                GPIO.output(lightState.LightGreen.Pin, 0)
                            self.state = False
                        else:
                            if lightState.LightRed.Pattern == "blink" and lightState.LightRed.On:
                                GPIO.output(lightState.LightRed.Pin, 1)
                            if lightState.LightOrange.Pattern == "blink" and lightState.LightOrange.On:
                                GPIO.output(lightState.LightOrange.Pin, 1)
                            if lightState.LightGreen.Pattern == "blink" and lightState.LightGreen.On:
                                GPIO.output(lightState.LightGreen.Pin, 1)
                            self.state = True
                    finally:
                        threadLock.release()
            else:
                print("Outside business hours, wait a minute. Time is: " + str(datetime.datetime.now().time()))
                time.sleep(60)
        print("stopped blinking!")

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('8.8.8.8', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

class readData (threading.Thread):
    def __init__(self, name, lightState, uri):
        threading.Thread.__init__(self)
        self.name = name
        self.lightState = lightState
        self.uri = uri
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def join(self, *args, **kwargs):
        self.stop()
        super(readData,self).join(*args, **kwargs)

    def run(self):
        print ("Starting " + self.name)
        while not self._stop_event.is_set():
            if datetime.datetime.now().time() > self.lightState.Switch.StartTime and datetime.datetime.now().time() < self.lightState.Switch.EndTime :
                # Get lock to synchrSonize threads
                threadLock.acquire()
                try:
                    ip = get_ip()
                    headers = {"IP": ip, "scriptVersion": version}
                    req = urllib.request.Request(self.uri, headers=headers)
                    url = urllib.request.urlopen(req)
                    data = json.loads(url.read().decode())

                    self.lightState.LightRed.On = data['LightRed']['On']
                    self.lightState.LightRed.Pattern = data['LightRed']['Pattern']

                    self.lightState.LightOrange.On = data['LightOrange']['On']
                    self.lightState.LightOrange.Pattern = data['LightOrange']['Pattern']

                    self.lightState.LightGreen.On = data['LightGreen']['On']
                    self.lightState.LightGreen.Pattern = data['LightGreen']['Pattern']

                    # Free lock to release next thread
                finally:
                    threadLock.release()
                    print("States set")
                    time.sleep(5)
            else:
                print("Outside business hours, wait a minute. Time is: " + str(datetime.datetime.now().time()))
                time.sleep(60)

class setLight (threading.Thread):
    def __init__(self, name, lightState):
        threading.Thread.__init__(self)
        self.lightState = lightState
        self.name = name
        self._stop_event = threading.Event()
   
    def stop(self):
        self._stop_event.set()

    def join(self, *args, **kwargs):
        self.stop()
        super(setLight,self).join(*args, **kwargs)

    def run(self):
        print ("Starting " + self.name)
      
        while not self._stop_event.is_set():
            if datetime.datetime.now().time() > self.lightState.Switch.StartTime and datetime.datetime.now().time() < self.lightState.Switch.EndTime :
                GPIO.output(self.lightState.Switch.Pin, 1)
                # Get lock to synchronize threads
                threadLock.acquire()
                try:
                    if self.lightState.LightRed.On and self.lightState.LightRed.Pattern == "solid":
                        #print("Turning on red light solid")
                        GPIO.output(self.lightState.LightRed.Pin, 1)
                    elif not self.lightState.LightRed.On:
                        #print("Turning off red light")
                        GPIO.output(self.lightState.LightRed.Pin, 0)

                    if self.lightState.LightOrange.On and self.lightState.LightOrange.Pattern == "solid":
                        #print("Turning on orange light solid")
                        GPIO.output(self.lightState.LightOrange.Pin, 1)
                    elif not self.lightState.LightOrange.On:
                        #print("Turning off orange light")
                        GPIO.output(self.lightState.LightOrange.Pin, 0)

                    if self.lightState.LightGreen.On and self.lightState.LightGreen.Pattern == "solid":
                        #print("Turning on green light solid")
                        GPIO.output(self.lightState.LightGreen.Pin, 1)
                    elif not self.lightState.LightGreen.On:
                        #print("Turning off green light")
                        GPIO.output(self.lightState.LightGreen.Pin, 0)
                finally:
                    # Free lock to release next thread
                    threadLock.release()
            else:
                GPIO.output(self.lightState.Switch.Pin, 0)
                #print("Outside business hours, wait a minute")
                time.sleep(60)

threadLock = threading.Lock()
threads = []
lightState = LightState()

while True:
    try:
        # Create new threads
        threadData = readData("Data Thread", lightState, uri)
        threadLight = setLight("Light Thread", lightState)
        blinkThread = BlinkThread("blinkThread", lightState)

        # Start new Threads
        threadData.start()
        threadLight.start()
        blinkThread.start()

        # Add threads to thread list
        threads.append(threadData)
        threads.append(threadLight)
        threads.append(blinkThread)

        # Wait for all threads to complete
        for t in threads:
            t.join()
    except Exception as ex:
        try:
            print("Exception found!")
            error = str(ex) + " | with stacktrace: " + traceback.format_exc()
            data = {"message": error, "level": "error"}

            json_data = json.dumps(data)
            headers = {'Content-type': 'application/json'}
            jsondataasbytes = json_data.encode('utf-8')
            req = urllib.request.Request("https://healthlight.azurewebsites.net/api/SaveLogging?code=vmLIhZBCghiCYjqEzh9OfZsUS0m1JELeR06aa/c65CaXoyszknM1gg==", headers=headers)
            url = urllib.request.urlopen(req,data=jsondataasbytes)
        except:
        		print("Cannot write exception!")
    finally:
        threadData.stop()
        threadLight.stop()
        blinkThread.stop()


print ("Exiting Main Thread")

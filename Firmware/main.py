from machine import Pin, I2C, UART, PWM
import sh1106
import time

# RGB LED
green = Pin(7, Pin.OUT)
red = Pin(44, Pin.OUT)
blue = Pin(8, Pin.OUT)

# Screen
i2c = I2C(0, scl=Pin(6), sda=Pin(5))

oled = sh1106.SH1106_I2C(128, 64, i2c)

# Scanner
uart = UART(1, timeout=100, baudrate=9600, tx=2, rx=4)

# Buzzer
buzzer = PWM(Pin(9), freq=2000, duty_u16=0)

lastScannedTime = 0

oledOn = False

lightOn = False

def show(msg):
    global oledOn

    oled.fill(0)
    msg1 = msg[:16]
    msg2 = msg[16:]

    oled.text(msg1, 0, 0)
    oled.text(msg2, 0, 10)
    oled.show()
    oledOn = True


def set_light(color):
    global lightOn

    green.off()
    red.off()
    blue.off()
    lightOn = False

    if color == "green":
        green.on()
        lightOn = True
    elif color == "red":
        red.on()
        lightOn = True
    elif color == "blue":
        blue.on()
        lightOn = True

def beepBuzzer(good):
    buzzer.freq(2000 if good else 1000)
    numRepeat = 1 if good else 2
    for _ in range(numRepeat):
        buzzer.duty_u16(32768)
        time.sleep_ms(100)
        buzzer.duty_u16(0)
        time.sleep_ms(100)

def readScannerInput():
    if uart.any():
        try:
            raw = uart.readline()
            code = raw.decode().strip()
            return code
        except:
            return None
    else:
        return None
    
def selfTest():
    set_light("green")
    time.sleep_ms(500)
    set_light("red")
    time.sleep_ms(500)
    set_light("blue")
    time.sleep_ms(500)
    beepBuzzer(True)
    time.sleep_ms(500)




def main():
    global lastScannedTime
    global oledOn
    
    selfTest()
    
    show("Ready")
    set_light("green")

    lastScannedTime = time.ticks_ms()

    while True:
        timeElapsed = time.ticks_diff(time.ticks_ms(), lastScannedTime)
        if oledOn and  timeElapsed >= 5000:
            oled.fill(0)
            oled.show()
            oledOn = False
        if timeElapsed <= 500:
            readScannerInput()
        if lightOn and timeElapsed >= 2000:
            set_light("off")

        code = readScannerInput()
        if code is not None:
            show(code)
            lastScannedTime = time.ticks_ms()
            if code.isdigit():
                set_light("green")
                beepBuzzer(True)
            else:
                set_light("red")
                beepBuzzer(False)                 

main()
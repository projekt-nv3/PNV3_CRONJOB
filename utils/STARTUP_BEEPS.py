import Jetson.GPIO as GPIO
import time
import timeit

OUTPUT_PIN = 21
GPIO.setmode(GPIO.BCM)
GPIO.setup(OUTPUT_PIN, GPIO.OUT)

def sleep_ms(milliseconds):
    seconds = milliseconds / 1000.0
    start_time = timeit.default_timer()
    while timeit.default_timer() - start_time < seconds:
        time.sleep(seconds - (timeit.default_timer() - start_time))


for i in range(5):
    GPIO.output(OUTPUT_PIN, GPIO.HIGH)
    sleep_ms(400)
    GPIO.output(OUTPUT_PIN, GPIO.LOW)
    sleep_ms(200)

import cv2
import numpy as np

import platform
import logging
import time

from detect import LogoDetector
import os
import datetime
RELAY_PIN = 23

# Check Platform
if platform.system() == 'Linux':
    import RPi.GPIO as GPIO
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(RELAY_PIN, GPIO.OUT)

    def unlock():
        logging.info("Unlocking Door")
        GPIO.output(RELAY_PIN, GPIO.HIGH)
        time.sleep(0.5)
        GPIO.output(RELAY_PIN, GPIO.LOW)
else:
    def unlock():
        logging.info("Unlocking Door")
        time.sleep(0.5)

def setup_logging(root):
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(root, 'logs')
    os.makedirs(logs_dir, exist_ok=True)

    # Setup Logging
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Setup Console Handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    logging.getLogger('').addHandler(ch)

    # Setup File Handler with daily log file
    log_file = os.path.join(logs_dir, f"door_unlock_{datetime.date.today().strftime('%Y-%m-%d')}.log")
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)
    logging.getLogger('').addHandler(fh)

    # Setup Logging Level
    logging.getLogger('').setLevel(logging.DEBUG)

    # Setup detected image save directory with daily folder
    save_path = os.path.join(root, "logs", "detected", datetime.date.today().strftime('%Y-%m-%d'))
    os.makedirs(save_path, exist_ok=True)
    return save_path

if __name__ == "__main__":

    # Setup Logging
    img_save_path = setup_logging(os.path.dirname(os.path.abspath(__file__)))

    # Setup Logo Detector
    detector = LogoDetector(cv2.imread("origin.png"))

    # Setup Video Capture
    vc = cv2.VideoCapture(0)
    vc.read() # Warmup
    vc.read()
    vc.read()

    # Initial Unlock Test
    logging.info("Testing Unlock")
    unlock()

    security_flag = False

    # Start Video Capture
    try:
        while True:
            ret, frame = vc.read()
            if not ret:
                logging.error("Failed to read video capture")
                break
             
            # Check if security flag is set
            if security_flag:
                # Save security frame
                save_file = os.path.join(img_save_path, f"{datetime.datetime.now().strftime('%H-%M-%S')}_security.jpg")
                cv2.imwrite(save_file, frame)
                logging.info("Security frame saved to %s", save_file)
                security_flag = False

                # Wait for 5 seconds before continuing
                time.sleep(5)
                continue

            if detector.detect(frame):
                for _ in range(10):
                    if not detector.detect(frame):
                        logging.debug("False positive, ignoring")
                        break
                else:
                    # Save detected frame
                    save_file = os.path.join(img_save_path, f"{datetime.datetime.now().strftime('%H-%M-%S')}.jpg")
                    cv2.imwrite(save_file, frame)
                    logging.info("Logo detected, unlocking door. Frame saved to %s", save_file)
                    unlock()

                    # Capture a new frame for security purposes
                    security_flag = True

            # cv2.imshow("frame", frame)
            # cv2.waitKey(1)
    except KeyboardInterrupt:
        logging.info("Keyboard Interrupt")
    finally:
        vc.release()
        cv2.destroyAllWindows()
        logging.info("Video Capture Released")
        logging.info("Program Exited")

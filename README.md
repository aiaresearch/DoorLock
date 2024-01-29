# DoorLock: Logo-Based Door Lock System for Raspberry Pi

## Description:

This project implements a logo-based door lock system using a Raspberry Pi equipped with OpenCV and RPi.GPIO libraries. The system is designed to detect a specific 2D pattern, in this case, our association's logo, using computer vision techniques. Upon successful detection of the logo, the system activates an electric magnet to control the lock of the back door of our office, effectively granting access to authorized personnel.

## Features:

- **Logo Detection:** Utilizes OpenCV for image processing and pattern recognition to detect a predefined 2D logo pattern.
- **Door Lock Control:** Integrates RPi.GPIO library to interface with an electric magnet controlling the lock mechanism.
- **Verification Process:** Verifies the presence of the logo pattern to grant access, ensuring security through visual recognition.

## Dependencies:

- **OpenCV:** Used for image processing and logo detection.
- **RPi.GPIO:** Enables interfacing with GPIO pins on the Raspberry Pi for controlling the electric magnet.

## License:

This project is licensed under the [MIT License](LICENSE).

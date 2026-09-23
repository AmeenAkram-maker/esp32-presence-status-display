ESP32 PRESENCE STATUS DISPLAY 

I created a dual microcontroller system consisting of two ESP32s. I utilized C++ and Python to bridge local network data to hardware displays. The user enters data into a custom-made terminal Python app (calendar data) which is then displayed remotely.

The highlights of the project are as follows:
- ESP32 Sender and Receiver: Uses ESP-NOW protocol for low-latency hardware-to-hardware communication 
- Python Backend: Creates and parses calendar JSON data and acts as an HTTP server gateway
- ST7735 TFT Display: Uses Adafruit GFX libraries for custom UI rendering and a Conway's Game of Life idle screensaver 

**PLEASE READ THE PDF ATTACHED FOR A DETAILED README**
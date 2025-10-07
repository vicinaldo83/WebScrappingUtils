# Web scrapping and automation utils

Utility things that I used while doing webscraping and desktop automation. Basic functions to start and control selenium webdriver instances, manipulate desktop applications and conrtol sheets. 
Since much of the code was made for an partucular application, there is some really especific things, but great part of the code can be reused for other things.

## Config.py ⚙

Configuration file to load envoriment variables, the only really important thing is the driver and log paths.
Also defines the type for different OS.

## Gerenciador.py 📂

Basically two main classe
  * **AppManager**: Application manager, control desktop excutables.
  * **PlanManager**: Sheets Manager, open, read, convert to JSON, modify from JSON and save sheets.

## Log.py 📝

Create and control logs files, also define the decorator to register some functions funcionality.

## Robo.py 🤖

The base for the Interactive robot I use, it sets the basic interaction like locate and click objects from the screen using pyautogui image locator, control downloaded files, take screenshots, etc.

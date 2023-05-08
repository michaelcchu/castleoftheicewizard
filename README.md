The purpose of this repository is to provide a distribution version of the game
Castle of the Ice Wizard. The original code can be found in the repository
called "Castle-of-the-Ice-Wizard".

Instructions:
- download the repository

A) to run the program:
- navigate to dist folder
- run main.exe

B) to compile the .exe file:
- in Command Prompt, navigate to the repository
- on Windows, type

venv\Scripts\activate

- then type

pyinstaller --onefile --add-data resources;resources main.pyw

C) to edit the python/pygame code:
- open main.py, sprites.py, settings.py, and pathFinder.py
  (these are the main python programs for this game)

D) to run the python code:
- in Command Prompt, navigate to the repository
- on Windows, if you have not already activated the virtual environment, type

venv\Scripts\activate

- then type

python main.py
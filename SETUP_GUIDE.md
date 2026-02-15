# Tetris Game - Beginner's Setup Guide

Welcome! This guide will walk you through everything you need to play your Tetris game, even if you've never programmed before.

## Step 1: Install Python

Python is the programming language we used to build this game.

### For Windows:
1. Go to https://www.python.org/downloads/
2. Click the big yellow "Download Python" button (get version 3.8 or newer)
3. Run the installer
4. **IMPORTANT**: Check the box that says "Add Python to PATH" at the bottom
5. Click "Install Now"
6. Wait for installation to complete

### For Mac:
1. Go to https://www.python.org/downloads/
2. Click the "Download Python" button
3. Open the downloaded .pkg file
4. Follow the installation steps
5. Python will be installed

### For Linux:
Python is usually already installed! Open a terminal and type:
```bash
python3 --version
```
If you see a version number, you're good to go!

## Step 2: Install Pygame

Pygame is a library that helps us create games with graphics and sound.

### On Windows:
1. Press the Windows key and type "cmd"
2. Click on "Command Prompt"
3. Type this command and press Enter:
   ```
   pip install pygame
   ```
4. Wait for it to finish (you'll see "Successfully installed pygame")

### On Mac:
1. Press Command + Space and type "terminal"
2. Open Terminal
3. Type this command and press Enter:
   ```
   pip3 install pygame
   ```
4. Wait for installation to complete

### On Linux:
1. Open your terminal
2. Type:
   ```
   pip3 install pygame
   ```

## Step 3: Get Your Game File

You should have a file called `tetris.py` - this is your game!

Save it somewhere you can find it easily, like:
- Windows: `C:\Users\YourName\Documents\tetris.py`
- Mac/Linux: `/home/yourname/tetris.py` or in your Documents folder

## Step 4: Run the Game!

### On Windows:
1. Open Command Prompt (Windows key + type "cmd")
2. Navigate to where you saved the file:
   ```
   cd C:\Users\YourName\Documents
   ```
3. Run the game:
   ```
   python tetris.py
   ```

### On Mac/Linux:
1. Open Terminal
2. Navigate to where you saved the file:
   ```
   cd ~/Documents
   ```
3. Run the game:
   ```
   python3 tetris.py
   ```

## How to Play

### Controls:
- **Left/Right Arrow Keys**: Move the piece left or right
- **Up Arrow Key**: Rotate the piece
- **Down Arrow Key**: Make the piece fall faster (soft drop)
- **Spacebar**: Instantly drop the piece to the bottom (hard drop)
- **R Key**: Restart the game

### Goal:
- Complete horizontal lines to clear them and score points
- The game gets faster as you level up
- Don't let the blocks reach the top!

### Scoring:
- 1 line cleared: 100 points × level
- 2 lines cleared: 300 points × level
- 3 lines cleared: 500 points × level
- 4 lines cleared (Tetris!): 800 points × level
- Soft drop (down arrow): 1 point per row
- Hard drop (spacebar): 1 point per row

### Levels:
- You gain a level every 10 lines cleared
- Each level makes the pieces fall faster
- Higher levels = more points per line!

## Troubleshooting

### "Python is not recognized" error:
- You need to add Python to your PATH
- Reinstall Python and make sure to check "Add Python to PATH"

### "No module named pygame" error:
- Pygame didn't install correctly
- Try running `pip install pygame` again
- Make sure you're using `pip` on Windows or `pip3` on Mac/Linux

### Game window is too small/large:
- Open the `tetris.py` file in a text editor
- Near the top, find these lines:
  ```python
  SCREEN_WIDTH = 400
  SCREEN_HEIGHT = 600
  ```
- Change these numbers to make the window bigger or smaller
- Save and run again

### Game runs but pieces are hard to see:
- You can adjust the `BLOCK_SIZE` variable (default is 30)
- Larger numbers = bigger blocks

## Making Changes (Optional)

Want to customize your game? Here are some easy changes:

### Change Colors:
Find this section in the code:
```python
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
# etc...
```
Change the numbers to get different colors (they're in Red, Green, Blue format, 0-255)

### Change Starting Speed:
Find this line:
```python
self.fall_speed = 500
```
Lower number = faster game, higher number = slower game

### Change Level-Up Rate:
Find this line:
```python
self.level = self.lines_cleared // 10 + 1
```
Change the `10` to level up faster (lower number) or slower (higher number)

## Having Fun!

That's it! You now have a fully working classic Tetris game. Enjoy playing, and feel free to experiment with the code to make it your own!

Some challenges to try:
- Beat your high score
- Clear 4 lines at once (Tetris!)
- Reach level 10
- Score 10,000 points

Happy gaming! 🎮

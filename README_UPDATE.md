# Simple Update Pipeline - Usage Instructions

## Overview
A clean, simple update system that's completely separate from the core game logic.

## Components Created
1. **version.json** - Contains current game version
2. **update_system.py** - Handles all update logic (separate from game)
3. **update_server.py** - Simple server for testing updates
4. **Modified snake_game.py** - Added main menu with "Check for Updates" option

## How It Works
1. Game shows main menu with "Play Game" and "Check for Updates"
2. When user clicks "Check for Updates":
   - Compares local version.json with server version
   - If newer version exists, shows update dialog
   - User can choose to update or continue with current version
3. If user chooses to update:
   - Downloads new version
   - Creates update installer script
   - Closes current game and installs update
   - Restarts game with new version

## Testing the Update Pipeline

### Step 1: Test Current Game
```bash
python snake_game.py
```
- Should show main menu
- Click "Play Game" to ensure game works normally
- Click "Check for Updates" (will show error since server is not running)

### Step 2: Start Update Server
```bash
# In a separate terminal
python update_server.py
```
- Server runs on http://localhost:8080
- Serves version 1.1.0 (newer than client's 1.0.0)

### Step 3: Test Update Flow
```bash
python snake_game.py
```
- Click "Check for Updates"
- Should show "Update Available" dialog
- Shows current version (1.0.0) vs new version (1.1.0)
- Click "Yes" to test download flow

### Step 4: Test "No Updates Available"
To test this scenario:
1. Edit version.json and change version to "1.1.0"
2. Run the game and check for updates
3. Should show "You're already running the latest version!"

## Key Features
- ✅ **Simple & Clean**: No over-engineering, just what's needed
- ✅ **Separate from Game**: Update logic is isolated in update_system.py
- ✅ **User Choice**: Always prompts before updating
- ✅ **Automatic Restart**: Game restarts after update
- ✅ **Error Handling**: Fails gracefully when server is offline
- ✅ **Version Comparison**: Proper semantic version checking

## File Structure
```
SimpleGame/
├── snake_game.py          # Main game (now with menu)
├── update_system.py       # Update logic (separate!)
├── update_server.py       # Test server
├── version.json          # Current version info
├── [existing game files] # Unchanged core game files
└── README_UPDATE.md      # This file
```

## Publishing a New Version
1. Update the version number in update_server.py
2. Add changelog items
3. Replace the executable the server serves
4. Users will be notified next time they check for updates

## Notes
- Update server uses simple HTTP (fine for local testing)
- For production, use HTTPS and proper authentication
- Update installer creates a temporary Python script for file replacement
- System is designed to be simple and understandable
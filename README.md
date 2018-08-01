# WoT External Minimap
WoT mod which allows the minimap to be displayed on a second monitor or device

## Development
1. Copy the content of the `res/` folder into your `WoT/res_mods/<current version>` folder.
2. Open a command prompt in your `WoT/res_mods/<current version>` folder and run `python -m compileall .`.
   Make sure you're using Python 2.
3. Install Node.js and run `npm install -g @vue/cli` in a command prompt.
4. Copy the `minimap-ui` folder into your `WoT/mods` folder.
5. Open a command prompt in your `WoT/mods/minimap-ui` folder and run `vue-cli-service build`.
   
## Usage
1. Start WoT
2. Open `localhost:13370` in your web browser.

Your browser will open a WebSocket connection with the mod and will print some position data to the screen.

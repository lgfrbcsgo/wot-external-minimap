# WoT External Minimap
WoT mod which allows the minimap to be displayed on a second monitor or device

## Installation
1. Copy the content of the `res/` folder into your `WoT/res_mods/<current version>` folder.
2. Open a command prompt in your `WoT/res_mods/<current version>` folder and run `python -m compileall .`.
   Make sure you're using Python 2.
   
## Usage
1. Start WoT and open a new blank window in web browser.
2. Open the developer tools (press F12 in Chrome).
3. Paste the following script into the console.

```javascript
var socket = new WebSocket("ws://localhost:8000");
socket.onmessage = function (event) {
  var reader = new FileReader();
  reader.onload = function() {
    console.log(JSON.parse(reader.result));
  }
  reader.readAsText(event.data);
}
```

The script will open a WebSocket connection with the mod and will print some position data to the console.

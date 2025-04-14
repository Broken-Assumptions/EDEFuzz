A Chrome extension to record interactions with the web page and produce a config file for EDEFuzz.

## Installation

To install the Chrome plugin, please follow the below steps:

- Open Chrome. 
- At the top-right corner, click the three-dots icon.
- From the drop-down menu, select `Extensions` - `Manage extensions`.
- Make sure you are in developer mode so that you can load unpacked plugins. At the top-right corner, toggle `developer mode`.
- At the top-left area of the same page (extensions), there should be a button `load uncompressed extension`. Click it and select the `./ChromePlugin/` folder.
- You should now have the plugin loaded. 

## Usage

- Open the web page for test in Chrome
- Click the icon for this extension in Chrome, then click the "start" button to start recording
- Manually trigger the API call on the web page (e.g. by clicking button / enter texts into textbox / etc.)
- Once the target API is triggered, click the icon for this extension in Chrome, and click the "stop" button to stop recording --- there should be a popup dialog prompting you to save the generated config file
- Inspect the generated file and make necessary adjustments (you will need to at least specify the `TARGET`

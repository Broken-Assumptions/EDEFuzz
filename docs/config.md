# EDEFuzz - Hunting excessive data exposure in web APIs

A tool to flag excessive data exposure vulnerabilities in web APIs. Tested on Ubuntu 18.04, Ubuntu 20.04 and Windows 10.


## Preparing a configuration file

A configuration file contains mainly the following three components:

- the target API to be tested 
- a sequence of instructions for EDEFuzz to interact with the web page under test
- (optional) the area-of-interest (discussed in section 4.4)

A line begins with a hashtag (`#`) indicates a comment line, which is ignored by EDEFuzz.


### Specify a target API

To specify the target API under test, write `TARGET /url/to/target?parameter=value`. In most cases, an absolute path would work well. This should typically be the first line in the configuration file. 

EDEFuzz checks if the provided `TARGET` appears in the _request_ _url_ of an HTTP request. Thus, any parameter containing timestamp or random values should not be included. For example, if an API call has the URL `/api/update?id=1&value=999&request_time=1686612345` could be recorded as `TARGET /api/update?id=1&value=999&request_time=`. 


### Provide a sequence of instructions

Add a sequence of interactions into the configuration file, so that EDEFuzz knows what to do to trigger the API call, and guide the web page to a fuzz-able state. 

EDEFuzz currently supports the following instructions.

- `LOAD [URL]`

Example: `LOAD https://pa55er6y.github.io/edesample1/`

This instructs EDEFuzz to load a specific web page by URL. It's typically the first instruction in the configuration file. 

- `WAIT_LOCATE [xpath]` 

Example: `WAIT_LOCATE //input[@id="password"]`

This instructs EDEFuzz to wait until the specified object (by XPath) is visually present on the web page. For example, after loading a web page, we want to wait until a specific object on the page is present (to indicate the page is fully loaded), before further interacting with the web page. 

- `INPUT [xpath] [value]`

Example: `INPUT //input[@id="username"] edefuzz`

This instructs EDEFuzz to fill in texts into an object (typically, a textbox) on the web page specified by XPath. 

- `CLICK [xpath]`

Example: `CLICK //form[@id="login"]/input[@type="submit"]`

This instructs EDEFuzz to click an object (for example, a button) on the web page specified by XPath.

- `HOVER [xpath]`

This instructs EDEFuzz to hover the mouse on top of an object (for example, an image) on the web page specified by XPath.

- `SCROLL END` / `SCROLL PAGE`

Scroll down the page. `SCROLL END` will scroll down to the bottom of the page (by simulating pressing _End_ on the keyboard), while `SCROLL PAGE` will scroll down for one screen (by simulating pressing _PgDn_ on the keyboard).

- `COOKIE [COOKIES]`

Example: `COOKIE key1=value1;key2=value2;key3=123`

This allows EDEFuzz to set the cookies for the current web page. Make sure the current loaded web page is from the same domain in order to have the cookies set correctly. This instruction is useless in the test execution phase, though could be handy to bypass authentication for some web pages. 

- `SLEEP [SECOND]`

Example: `SLEEP 2`

This instructs EDEFuzz to wait for a specified period of time (in seconds), before continuing the next instruction. 


### Specify an area-of-interest

Typically, the last line in the configuration file should be `FUZZ`, to instruct EDEFuzz to extract the DOM tree of the current web page for comparison. However, using the DOM tree for the entire web page could slightly reduce performance, and may produce false negatives. 

Optionally, human knowledge can be utilised to specify an area-of-interest. An area-of-interest allows EDEFuzz to only extract and compare a subtree of the entire DOM tree. The area-of-interest should be specified using XPath, for example, `FUZZ //div[@id="container"]/table`.


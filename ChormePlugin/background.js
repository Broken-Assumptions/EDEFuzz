// background.js
/*
chrome.action.onClicked.addListener((tab) => {
  chrome.scripting.executeScript({
    target: { tabId: tab.id },
    files: ['main.js']
  });
});*/

let commands = [];
let status = false;

/*chrome.runtime.onInstalled.addListener(() => {
  chrome.storage.sync.set({ commands });
  chrome.storage.sync.set({ status });
  console.log("Empty command sequence added to local storage.");
});*/


chrome.runtime.onMessage.addListener(
  function(request, sender, sendResponse) {
    //chrome.storage.sync.get("status", ({ status }));
    if (sender.tab) { // sent from content script
      if (status) {
        //chrome.storage.sync.get("commands", ({ commands }));
        
        if (request.e.substring(0, 5) == "INPUT" && commands.length > 0 && commands[commands.length-1].startsWith(request.e.substring(0, request.e.length-1))) {
            commands[commands.length-1] = commands[commands.length-1] + request.e.substring(request.e.length-1);
        }
        else {
            commands.push(request.e); 
        }
        
        //chrome.storage.sync.set({ commands });
        console.log("From webpage: " + request.e);
      }
    }
    else { // sent from extension
      //console.log(request.action);
      if (status) { // recording ON
        if (request.action == "stop") {
          console.log("From extension: stop");
          status = false;
          commands.push("FUZZ");
          //chrome.storage.sync.set({ status });
          //chrome.storage.sync.get("commands", ({ commands }));
          console.log(commands);
          
          //var blob = new Blob(commands, {type: "text/plain"});
          //var url = URL.createObjectURL(blob);
          chrome.downloads.download({
            url: "data:text/plain;base64," + btoa(commands.join("\r\n")),
            filename: "new.config"
          });
        }
      }
      else { // recording OFF
        if (request.action == "start") {
          console.log("From extension: start");
          commands = ["# EDEFuzz configuration", "", "TARGET REPLACE_ME", ""];
          
          //tab = await getCurrentTab();
          
          //chrome.storage.sync.set({ commands });
          status = true;
          //chrome.storage.sync.set({ status });
        }
      }
    }
  }
);




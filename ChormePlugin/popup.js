

document.getElementById("start").addEventListener("click", function() {
    chrome.runtime.sendMessage({action: "start"});
    
    var query = { active: true, lastFocusedWindow: true };
    chrome.tabs.query(query, callback);
});

function callback(tabs) {
    chrome.scripting.executeScript({
        target: { tabId: tabs[0].id },
        files: ["inject.js"]
    });
}

document.getElementById("stop").addEventListener("click", function() {
    chrome.runtime.sendMessage({action: "stop"});
});

//function updateStatus() {
//    chrome.runtime.sendMessage()
//}
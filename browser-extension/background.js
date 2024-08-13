chrome.commands.onCommand.addListener(function(command) {
  if (command === "submit-link") {
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
      if (tabs[0]) {
        submitLink(tabs[0].url);
      }
    });
  }
});

function submitLink(url) {
  chrome.storage.sync.get({port: 9000}, function(items) {
    const rssItem = `
      <item>
        <link>${url}</link>
      </item>
    `;
    
    fetch(`http://localhost:${items.port}/submit`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/xml'
      },
      body: rssItem
    })
    .then(response => response.text())
    .then(result => {
      console.log('Success:', result);
      changeIcon(true);
    })
    .catch(error => {
      console.error('Error:', error);
      changeIcon(false);
    });
  });
}

function changeIcon(success) {
  const iconPath = success ? 'icon_success.png' : 'icon_error.png';
  chrome.browserAction.setIcon({path: iconPath});
  
  // Reset icon after 1 second
  setTimeout(() => {
    chrome.browserAction.setIcon({path: 'icon.png'});
  }, 1000);
}

chrome.browserAction.onClicked.addListener(function(tab) {
  chrome.tabs.create({url: 'interface.html'});
});

chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
  if (request.action === "changeIcon") {
    changeIcon(request.success);
  }
});

let menuVisible = false;
let menu = null;

function createMenu() {
  menu = document.createElement('div');
  menu.id = 'syndex-menu';
  menu.innerHTML = `
    <div class="syndex-header">Syndex</div>
    <div>Port: <input type="number" id="portInput" min="1" max="65535" value="9000"></div>
    <button id="submitButton">Submit Current URL</button>
  `;
  document.body.appendChild(menu);

  const portInput = document.getElementById('portInput');
  const submitButton = document.getElementById('submitButton');
  
  chrome.storage.sync.get({port: 9000}, function(items) {
    portInput.value = items.port;
  });

  portInput.addEventListener('change', function() {
    chrome.storage.sync.set({port: this.value}, function() {
      console.log('Port saved:', portInput.value);
    });
  });

  submitButton.addEventListener('click', function() {
    chrome.runtime.sendMessage({action: "submitLink", url: window.location.href});
  });
}

function toggleMenu() {
  if (!menu) {
    createMenu();
  }
  menuVisible = !menuVisible;
  menu.style.display = menuVisible ? 'block' : 'none';
}

chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
  if (request.action === "toggleMenu") {
    toggleMenu();
  }
});

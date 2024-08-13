// interface.js
document.addEventListener('DOMContentLoaded', function() {
    const portInput = document.getElementById('portInput');
    const submitButton = document.getElementById('submitButton');
    const refreshButton = document.getElementById('refreshButton');
    const statusDiv = document.getElementById('status');
    const rssContentDiv = document.getElementById('rssContent');

    // Load saved port and fetch RSS
    chrome.storage.sync.get({port: 9000}, function(items) {
        portInput.value = items.port;
        fetchRSS();
    });

    // Save port when changed
    portInput.addEventListener('change', function() {
        chrome.storage.sync.set({port: this.value}, function() {
            statusDiv.textContent = 'Port saved: ' + portInput.value;
        });
    });

    // Submit current URL
    submitButton.addEventListener('click', function() {
        chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
            if (tabs[0]) {
                submitLink(tabs[0].url);
            } else {
                statusDiv.textContent = 'No active tab found';
            }
        });
    });

    // Refresh RSS
    refreshButton.addEventListener('click', fetchRSS);

function fetchRSS() {
    const port = portInput.value;
    statusDiv.textContent = 'Fetching RSS...';
    
    fetch(`http://localhost:${port}/rss`)
    .then(response => response.text())
    .then(xml => {
        const parser = new DOMParser();
        const xmlDoc = parser.parseFromString(xml, "text/xml");
        
        // Fetch and display channel title
        const channelTitle = xmlDoc.querySelector("channel > title");
        const titleText = channelTitle.hasAttribute("unspecified") ? "Untitled Channel" : channelTitle.textContent;
        
        let output = `<h2 class="editable channel-title" contenteditable="true" data-placeholder="Channel Title">${titleText}</h2>`;
        
        const items = Array.from(xmlDoc.getElementsByTagName("item"));
        
        items.forEach((item, index) => {
            const title = item.getElementsByTagName("title")[0];
            const link = item.getElementsByTagName("link")[0];
            const description = item.getElementsByTagName("description")[0];
            const pubDate = item.getElementsByTagName("pubDate")[0];

            const titleText = title.hasAttribute("unspecified") ? "" : title.textContent;
            const fullUrl = link.textContent;
            const trimmedUrl = fullUrl//.replace(/^https?:\/\//, '').substring(0, 50);
            const displayUrl = trimmedUrl + (trimmedUrl.length < fullUrl.length ? '' : '');
            const descriptionText = description.hasAttribute("unspecified") ? "" : description.textContent;

            output += `<div class="rss-item-box">`;
            output += `<div class="rss-item" data-index="${items.length - 1 - index}" data-pubdate="${pubDate.textContent}">`;
            output += `${items.length - 1 - index}: <a href="${fullUrl}" target="_blank">${displayUrl}</a><br>`;
            output += `    <span class="editable title ${titleText ? '' : 'placeholder'}" contenteditable="true" data-placeholder="title...">${titleText || 'title...'}</span><br>`;
            output += `    <span class="editable description ${descriptionText ? '' : 'placeholder'}" contenteditable="true" data-placeholder="...">${descriptionText || '...'}</span>`;
            output += `</div></div><br>`;
        });

        rssContentDiv.innerHTML = output;
        statusDiv.textContent = 'RSS fetched successfully';

        // Add event listeners for editable content
        document.querySelectorAll('.editable').forEach(el => {
            el.addEventListener('blur', handleEdit);
            el.addEventListener('keydown', function(e) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    e.target.blur();
                }
            });
            el.addEventListener('focus', function(e) {
                if (e.target.textContent === e.target.dataset.placeholder) {
                    e.target.textContent = '';
                    e.target.classList.remove('placeholder');
                }
            });
            el.addEventListener('blur', function(e) {
                if (e.target.textContent === '') {
                    e.target.textContent = e.target.dataset.placeholder;
                    e.target.classList.add('placeholder');
                }
            });
        });
    })
    .catch(error => {
        statusDiv.textContent = 'Error fetching RSS: ' + error;
        rssContentDiv.textContent = '';
    });
}

    function handleEdit(event) {
        const element = event.target;
        if (element.classList.contains('channel-title')) {
            sendChannelTitleEdit(element.textContent);
        } else {
            const item = element.closest('.rss-item');
            const index = item.dataset.index;
            const pubDate = item.dataset.pubdate;
            const field = element.classList.contains('title') ? 'title' : 'description';
            const newValue = element.textContent;

            if (newValue !== element.dataset.placeholder) {
                sendEdit(index, pubDate, field, newValue);
            }
        }
    }

    function sendChannelTitleEdit(newTitle) {
        const port = portInput.value;
        fetch(`http://localhost:${port}/edit-channel`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                field: 'title',
                value: newTitle
            })
        })
        .then(response => response.text())
        .then(result => {
            statusDiv.textContent = 'Channel title updated: ' + result;
        })
        .catch(error => {
            statusDiv.textContent = 'Error updating channel title: ' + error;
        });
    }

    function sendEdit(index, pubDate, field, newValue) {
        const port = portInput.value;
        fetch(`http://localhost:${port}/edit`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                pubDate: pubDate,
                field: field,
                value: newValue
            })
        })
        .then(response => response.text())
        .then(result => {
            statusDiv.textContent = 'Edit successful: ' + result;
        })
        .catch(error => {
            statusDiv.textContent = 'Error editing item: ' + error;
        });
    }
});

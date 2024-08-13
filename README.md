# Syndex
> A syndex is a (syn)dicated-in(dex), aka a distributed bookmark.
>
> This repository contains the spec and simple implemenentations of **Syndex the cli** and **Syndex the browser extension**.

---

## Usage

### 1. Syndex the cli

Install Syndex the cli
```
pip install syndex
```

```
pipx install syndex
```

Or manually through the repo
```
git clone git@github.com:spikedoanz/syndex.git
cd syndex
pip install .
```

Bookmarks can be added in the following format
```
syndex [file_path.xml] [url to bookmark] [title] [description]
```

> title and description will contain the tag undefined=True if blank


Example:
```
syndex hello-world.xml https://en.wikipedia.org/wiki/RSS \
"this is an example title" \
"this is an example description"
```

Will create the following xml file:
```
<?xml version="1.0" ?>
<rss version="2.0">
  <channel>
    <item>
      <title>this is an example title</title>
      <link>https://en.wikipedia.org/wiki/RSS</link>
      <pubDate>Tue, 13 Aug 2024 17:36:21 +0000</pubDate>
      <description>this is an example description</description>
    </item>
    <title unspecified="true"/>
  </channel>
</rss>
```

Appennding a record can be done the same way
```
syndex hello-world.xml https://en.wikipedia.org/wiki/Git \
"god i love git"
```

Will append the new bookmark to the TOP of the xml file:
```
<?xml version="1.0" ?>
<rss version="2.0">
  <channel>
    <item>                                                  | 
      <title>god i love git</title>                         |     
      <link>https://en.wikipedia.org/wiki/Git</link>        |  <- inserted here
      <pubDate>Tue, 13 Aug 2024 17:37:37 +0000</pubDate>    |
      <description unspecified="true"/>                     |
    </item>                                                 |
    <item>
      <title>this is an example title</title>
      <link>https://en.wikipedia.org/wiki/RSS</link>
      <pubDate>Tue, 13 Aug 2024 17:36:21 +0000</pubDate>
      <description>this is an example description</description>
    </item>
    <title unspecified="true"/>
  </channel>
</rss>
```
---

### 2. Syndex the browser extension

The extension is a lot more WIP so you can only install from source for now

Clone the repo:
```
git clone git@github.com:spikedoanz/syndex.git
```

<br>

#### Installing the extension
For chrome, type [chrome://extensions](chrome://extensions) into your search bar.

Click the developer mode button on the top right

Then click load unpacked.

Then select the browser-extension folder in the syndex repository.

<br>

[Detailed guide from Google Chrome docs here](https://support.google.com/chrome_webstore/answer/2664769?hl=en).

<br>

[Detailed guide from Firefox docs here](https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/Your_first_WebExtension).


<br>

#### Load the extension
You'll then see the new Syndex extension (with the § logo).

Click on it, and you'll be brought to the bookmark management page.


<br>

#### Hosting a server
Then, use syndex-cli to host an http server watching your bookmarks file. (defaults to 9000)

```
syndex hello-world.xml -s [PORT](optional)
```

The extension listens on port 9000 by default (customizable with the Port input box at the bottom)

<br>

#### Saving bookmarks
Then, to (S)ave a bookmark:

```
Default: Ctrl+Shift+S
Mac: Cmd+Shift+S
```

Which will append whatever url you're currently on to your xml file.


<br>

#### Editing bookmarks
You can click on pretty much anything on the bookmarks page to change it and it'll be reflected in the xml file.

```
Bookmark title default: Untitled

Title default: title...

Description default: ...
```

---

## Extras 

### 1. RSS spec

Everything in the [RSS spec](https://www.rssboard.org/rss-specification) is accepted. Though this is the standard:

- title: whatever you want
    - default: ```<title unspecified="true" />```

- Every bookmark is just an item in an RSS feed. Minimal requirements are:
    - link: ```<link>url to bookmark that can be curled</link>```
    - THATS IT
    - Optional tags (syndex includes these by default):
        - title: human / llm readable text
            - default: ```<title unspecified="true" />```
        - description: human / llm readable text
            - default: ```<description unspecified="true" />```
        - pubDate: bookmarked time

## 2. Hosting
Because this entire spec is just some rss files managed by git, it can be hosted directly on github/gitlab and inherits all of the nice features that provides.
- Very high uptime
- Integration into existing dev pipelines
- No need for a separate authentication system, just use the one you're using for git

## 3. Forking

Syndexes can be extended by forking them through github.

They can be combined by creating multi repos.

## 4. User Space
- All downloading, filtering, and search tools should be implemented in the user space, independent of the spec in this document.
    - TODO: Search
    - TODO: RAG
    - TODO: Recommendation

## 5. Dual private / public use
For private use, syndex is a lightweight protocol for platform agnostic bookmarking -- think Obsidian Markdown vs whatever Notion has

For public use, syndex is a dream for sharers. They can expose their RSS feeds and enable others to fork, merge, and manipulate the bookmark collections. This opens up possibilities like building search engines across community syndexes.

## 6. Community managed syndex
Software that lets people merge two syndexes automatically would be interesting:
- Deduplication.
- PRs as the system to insert new bookmarks.
- Train a model to learn how to do PRs -> Autofiltering preference model?

import argparse
import json
import os
import xml.etree.ElementTree as ET
import urllib.request
from typing import Optional
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import xml.dom.minidom

def is_url_valid(url: str) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            return response.status < 400
    except urllib.error.URLError:
        return False

def load_rss(file_path: str) -> ET.Element:
    if not os.path.isfile(file_path):
        root = ET.Element('rss', {'version': '2.0'})
        channel = ET.SubElement(root, 'channel')
        ET.SubElement(channel, 'title', {'unspecified': 'true'})
    else:
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            channel = root.find('channel')
            if channel is None:
                raise ValueError(f"Error: {file_path} is not a valid RSS file.")
            if channel.find('title') is None:
                ET.SubElement(channel, 'title', {'unspecified': 'true'})
        except ET.ParseError:
            raise ValueError(f"Error: {file_path} is not a valid XML file.")
    
    return root

def add_bookmark(file_path: str, url: str, title: Optional[str] = None, message: Optional[str] = None, validate: bool=True):
    if validate:
        if not is_url_valid(url):
            print(f"Error: {url} is not a valid or accessible URL.")
            return

    try:
        root = load_rss(file_path)
    except ValueError as e:
        print(str(e))
        return

    channel = root.find('channel')

    # Create new item
    new_item = ET.Element('item')
    
    # Add title
    if title:
        ET.SubElement(new_item, 'title').text = title
    else:
        ET.SubElement(new_item, 'title', {'unspecified': 'true'})

    ET.SubElement(new_item, 'link').text = url
    ET.SubElement(new_item, 'pubDate').text = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")
    
    if message:
        ET.SubElement(new_item, 'description').text = message
    else:
        ET.SubElement(new_item, 'description', {'unspecified': 'true'})

    # Prepend the new item to the channel
    channel.insert(0, new_item)

    # Convert to string
    xml_str = ET.tostring(root, encoding='unicode')
    
    # Use minidom to prettify the XML
    dom = xml.dom.minidom.parseString(xml_str)
    pretty_xml = dom.toprettyxml(indent='  ')
    
    # Remove extra newlines that minidom adds
    pretty_xml = '\n'.join([line for line in pretty_xml.split('\n') if line.strip()])

    # Write the prettified XML to file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(pretty_xml)

    print(f"Added bookmark to {file_path}: {url}")

class SyndexHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, file_path=None, **kwargs):
        self.file_path = file_path
        super().__init__(*args, **kwargs)

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        if self.path == '/submit':
            try:
                rss_item = ET.fromstring(post_data)
                url = rss_item.find('link').text
                add_bookmark(file_path=self.file_path, url=url, validate=False)
                
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b"Bookmark added successfully")
            except ET.ParseError:
                self.send_response(400)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b"Invalid XML data")
        elif self.path == '/edit':
            try:
                edit_data = json.loads(post_data)
                self.edit_item(edit_data)
                
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b"Item edited successfully")
            except json.JSONDecodeError:
                self.send_response(400)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b"Invalid JSON data")
        elif self.path == '/edit-channel':
            try:
                edit_data = json.loads(post_data)
                self.edit_item({'field': 'channel_title', 'value': edit_data['value']})
                
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b"Channel title updated successfully")
            except json.JSONDecodeError:
                self.send_response(400)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b"Invalid JSON data")
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"Not found")

    def do_GET(self):
        if self.path == '/rss':
            try:
                root = load_rss(self.file_path)
                xml_str = ET.tostring(root, encoding='unicode')
                
                self.send_response(200)
                self.send_header('Content-type', 'application/rss+xml')
                self.end_headers()
                self.wfile.write(xml_str.encode())
            except ValueError as e:
                self.send_response(500)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(str(e).encode())
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"Not found")

    def edit_item(self, edit_data):
        try:
            root = load_rss(self.file_path)
        except ValueError as e:
            print(str(e))
            return

        channel = root.find('channel')
        
        if edit_data['field'] == 'channel_title':
            channel_title = channel.find('title')
            if channel_title is None:
                channel_title = ET.SubElement(channel, 'title')
            if edit_data['value']:
                channel_title.text = edit_data['value']
                if 'unspecified' in channel_title.attrib:
                    del channel_title.attrib['unspecified']
            else:
                channel_title.text = None
                channel_title.set('unspecified', 'true')
        else:
            for item in channel.findall('item'):
                if item.find('pubDate').text == edit_data.get('pubDate'):
                    element = item.find(edit_data['field'])
                    if element is not None:
                        if edit_data['value']:
                            element.text = edit_data['value']
                            if 'unspecified' in element.attrib:
                                del element.attrib['unspecified']
                        else:
                            element.text = None
                            element.set('unspecified', 'true')
                    break
        
        # Write the updated XML to file
        xml_str = ET.tostring(root, encoding='unicode')
        dom = xml.dom.minidom.parseString(xml_str)
        pretty_xml = dom.toprettyxml(indent='  ')
        pretty_xml = '\n'.join([line for line in pretty_xml.split('\n') if line.strip()])
        
        with open(self.file_path, 'w', encoding='utf-8') as f:
            f.write(pretty_xml)

def start_server(file_path: str, port: int):
    try:
        root = load_rss(file_path)
        # Save the file to ensure it exists and is properly formatted
        xml_str = ET.tostring(root, encoding='unicode')
        dom = xml.dom.minidom.parseString(xml_str)
        pretty_xml = dom.toprettyxml(indent='  ')
        pretty_xml = '\n'.join([line for line in pretty_xml.split('\n') if line.strip()])
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(pretty_xml)
        print(f"RSS file loaded or created: {file_path}")
    except ValueError as e:
        print(f"Error: {str(e)}")
        return

    handler = lambda *args, **kwargs: SyndexHandler(*args, file_path=file_path, **kwargs)
    server = HTTPServer(('localhost', port), handler)
    print(f"Server started on port {port}")
    print(f"Serving RSS file: {file_path}")
    print("Press Ctrl+C to stop the server")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped")

def main():
    parser = argparse.ArgumentParser(description='Syndex - Add Bookmarks or Start Server')
    parser.add_argument('filepath', type=str, help='Path to the XML file')
    parser.add_argument('-s', '--server', nargs='?', const=9000, type=int, help='Start server on specified port (default: 9000)')
    parser.add_argument('url', type=str, nargs='?', help='URL of the bookmark')
    parser.add_argument('title', type=str, nargs='?', help='Title of the bookmark')
    parser.add_argument('message', type=str, nargs='?', help='Description of the bookmark')
    args = parser.parse_args()

    if args.server is not None:
        start_server(args.filepath, args.server)
    elif args.url:
        add_bookmark(args.filepath, args.url, args.title, args.message)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()

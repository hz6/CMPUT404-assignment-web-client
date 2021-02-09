#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse


def help():
    print("httpclient.py [GET/POST] [URL]\n")


class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body


class HTTPClient(object):

    def get_host_port(self, url):
        [port, hostname, path] = [0, "localhost", "/"]
        if urllib.parse.urlparse(url).port:
            port = urllib.parse.urlparse(url).port
        else:
            port = 80
        if urllib.parse.urlparse(url).hostname:
            hostname = urllib.parse.urlparse(url).hostname
        else:
            hostname = "localhost"
        if urllib.parse.urlparse(url).path:
            path = urllib.parse.urlparse(url).path
        else:
            path = "/"
        return [hostname, port, path]

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        code = data.split(" ")[1]
        return int(code)

    def get_headers(self, data):
        header = data.split("\r\n\r\n")[0]
        return header

    def get_body(self, data):
        body = data.split("\r\n\r\n")[1]
        return body

    def sendall(self, data):
        self.socket.sendall(data.encode("utf-8"))

    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        [host, port, path] = self.get_host_port(url)
        agent = "User-Agent: curl/7.64.1\r\n"
        accept = "Accept: */*\r\n"
        connection = "Conntection: close\r\n"
        payload = "GET" + path + "HTTP/1.1" + agent + \
            "Host:" + host + accept + connection
        self.connect(host, port)
        self.sendall(payload)
        content = self.recvall(self.socket)
        self.close()
        code = self.get_code(content)
        body = self.get_body(content)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        [host, port, path] = self.get_host_port(url)
        agent = "User-Agent: curl/7.64.1\r\n"
        accept = "Accept: */*\r\n"
        content_type = "Content-Type: application/json/x-www-form-urlencoded\r\n"
        connection = "Conntection: close\r\n"
        if args:
            message = urllib.parse.urlparse(args)
            content_length = "Content-length: " + str(len(message)) + "\r\n"
            payload = "POST" + path + "HTTP/1.1\r\n" + agent + "Host:" + host + "\r\n" + \
                content_length + content_type + connection + \
                "\r\n" + urllib.parse.urlencode(args)
        else:
            content_length = "Content-length: " + str(0) + "\r\n"
            payload = "POST" + path + "HTTP/1.1\r\n" + agent + "Host:" + \
                host + "\r\n" + content_length+content_type+connection+"\r\n"
        try:
            self.connect(host, port)
            self.sendall(payload)
            content = self.recvall(self.socket)
            self.close()
            code = self.get_code(content)
            body = self.get_body(content)
        except:
            code = 404
            body = None

        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST(url, args)
        else:
            return self.GET(url, args)


if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command(sys.argv[2], sys.argv[1]))
    else:
        print(client.command(sys.argv[1]))

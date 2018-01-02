"""python template for running in afterburn mode"""

import sys
import os
from function import handler

SEPARATOR = "\r\n"
HTTP_METHODS = ['POST']

class MalformedRequestError(Exception):
    """Custom Exception to handle Malformed Http requests"""
    def __init__(self, message):
        super(MalformedRequestError, self).__init__(message)
        self.message = message

def parse_header():
    """Reads the http headers from watchdog over stdin
    Returns:
        string: http method of the request
        dict: http headers in string to string dictionary
    """
    raw_header = ""
    while True:
        line = read_line()
        if line == "\n":
            break
        raw_header += line

    headers = {}
    method = ''
    for index, header in enumerate(raw_header.split("\n")):
        # Parse the first line to get http method
        if index == 0:
            method = header.split(' ')[0]
            continue
        # Parse rest of the lines for key, value
        parts = header.split(':')
        
        # Ignoring the dirty headers(for now). If we decide to throw the exception,
        # we have to do it after reading the body to keep the next request clean
        if len(parts) < 2:
            continue
        
        headers[parts[0]] = ''.join(parts[1:])

    return method, headers

def read_line():
    """Reads the individual line representing header from stdin"""
    line = ""
    while True:
        char = sys.stdin.read(1)
        if char == "\r":
            continue
        line += char
        if char == "\n":
            break
    return line

def get_request():
    """Reads the http request from watchdog over stdin

    Returns:
        string: http method of the request
        dict: http headers in string to string dictionary
        string: http body of the request
    """
    method, headers = parse_header()

    if 'Content-Length' not in headers:
        raise KeyError('Content-Length must be present in the request')

    content_length = int(headers['Content-Length'])
    body = sys.stdin.read(content_length)

    if method not in HTTP_METHODS:
        raise MalformedRequestError('Unrecognised Http method')

    return method, headers, body

def make_response(status, result, content_type=None):
    """Makes the http response

    Returns:
        string: raw response
    """
    response = ""
    # Add headers
    response += "HTTP/1.1 {}{}".format(status, SEPARATOR)
    response += "Content-Length: {}{}".format(len(result), SEPARATOR)
    if content_type:
        response += "Content-Type: {}{}".format(content_type, SEPARATOR)
    response += "Connection: Close{}".format(SEPARATOR)
    # Add separator
    response += SEPARATOR
    # Add body
    response += result

    return response

def parse():
    """
    Reads the incoming request from stdin
    Calls the function with the request body
    Writes the function's response to stdout
    """
    while True:
        try:
            # Get the incoming request
            method, headers, body = get_request()
            # Call the function
            result = handler.handle(body)
            # Make response
            response = make_response("200 OK", result, "text/plain")
        except MalformedRequestError as error:
            result = "Malformed Request: {}".format(" ".join(error.args))
            response = make_response("400 Bad Request", result, "text/plain")
        except KeyboardInterrupt:
            os.remove("/tmp/.lock")
            sys.exit(1)
        except BaseException as error:
            result = "Internal Error: {}".format(" ".join(error.args))
            response = make_response("500", result, "text/plain")
        # Write response to stdout
        sys.stdout.write(response)
        sys.stdout.flush()

if __name__ == "__main__":
    parse()

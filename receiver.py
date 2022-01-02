#!/usr/bin/python3.9
# -*- coding: utf-8 -*-

import socket, os, shutil, sys
from colorama import Fore, Style
import argparse

### FOR PARSING ARGUMENTS
argparser = argparse.ArgumentParser(description="Transfer files and directories between sockets")
argparser.add_argument("HOST", action="store", type=str, nargs="?", help="host to connect to")
argparser.add_argument("PORT", type=int, default=9999, help="port to connect to", action="store")
argparser.add_argument("--ouput-dir", "-o", action="store", nargs="?", type=str, default="./", help="output the content to this directory (default: current)", dest="output_path")
argparser.add_argument("--no-color", "-nc", action="store_false", dest="color_support", help="disables color support (default: enabled)")
argparser.add_argument("--quiet", "-q", action="store_true", dest="quiet_mode", help="does not print anything except errors")

parser = argparser.parse_args()

host = parser.HOST
port = parser.PORT
output_path = parser.output_path
color_support = parser.color_support
quiet_mode = parser.quiet_mode

if color_support == True:
    lyellow = Fore.LIGHTYELLOW_EX
    lblue = Fore.LIGHTBLUE_EX
    lred = Fore.LIGHTRED_EX
    reset = Fore.RESET
    lgreen = Fore.LIGHTGREEN_EX
else:
    lyellow = ""
    lblue = ""
    lred = ""
    lgreen = ""
    reset = ""

def print_status(string, quiet_mode):
    if quiet_mode == False:
        print(f"{lblue}[*]{reset} {string}")
    else:
        pass
def print_error(string, quiet_mode):
    if quiet_mode == False:
        print(f"{lred}[-]{reset} {string}")
    else:
        pass
def print_debug(string, quiet_mode):
    if quiet_mode == False:
        print(f"{lgreen}[+]{reset} {string}")
    else:
        pass
def print_line(string, quiet_mode):
    if quiet_mode == False:
        print(f"{reset}{string}")
    else:
        pass

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    server.connect((host, port))
except socket.error:
    print_error("Could not connect to the server", False)
    sys.exit(1)

buffer_size = server.recv(100).decode('UTF-8').strip()
print_status("Connected to the server", quiet_mode)

def recv_file(file_name, output_path, quiet_mode, BUFFER_SIZE):
    size = server.recv(100).decode('UTF-8').strip()
    terminator = server.recv(21).decode('UTF-8')
    with open(os.path.join(output_path, file_name), mode="wb") as f:
        data = b''
        while not bytes(terminator, "utf-8") in data:
            data = server.recv(int(BUFFER_SIZE))
            if bytes(terminator, "utf-8") in data:
                data = data[:-len(terminator)]
                f.write(data)
                break
            f.write(data)
    if os.path.getsize(os.path.join(output_path, file_name)) == int(size):
        server.send(bytes("1", "utf-8"))
        print_status(f"File '{lyellow}{os.path.join(output_path, file_name)}{reset}' received successfully", quiet_mode)
    else:
        server.send(bytes("0", "utf-8"))
        print_error(f"File '{lred}{os.path.join(output_path, file_name)}{reset}' is not received successfully", False)
        

def main(server, output_path, quiet_mode):
    path = server.recv(1030).decode('UTF-8').strip()
    if path == "": # SERVER SIDE HAS BEEN CLOSED
        sys.exit(1)
    
    if path.startswith("[DIR]") == True:
        try:
            if os.path.isdir(os.path.join(output_path, path[5:])) == True:
                shutil.rmtree(os.path.join(output_path, path[5:]))
            os.makedirs(os.path.join(output_path, path[5:]))
            print_status(f"Created directory '{lyellow}{os.path.join(output_path, path[5:])}{reset}'", quiet_mode)
            status = "1"
        except Exception:
            print_error(f"Could not create directory '{lred}{os.path.join(output_path, path[5:])}{reset}'", False)
            status = "0"

        server.send(bytes(status, "utf-8"))
    elif path.startswith("[FILE]") == True:
        print_status(f"Receiving '{lyellow}{path[6:]}{reset}' ...", quiet_mode)
        recv_file(path[6:], output_path, quiet_mode, buffer_size)
    else:
        pass

if __name__ == "__main__":
    if output_path != "./":
        print_status(f"Saving to '{lyellow}{output_path}{reset}'", quiet_mode)
        try:
            os.makedirs(output_path)
        except FileExistsError:
            pass
        except Exception:
            print_error(f"Could not access the directory '{lred}{output_path}{reset}'", False)
            server.send(bytes("0", "utf-8"))
            server.close()
            sys.exit(1)
    server.send(bytes("1", "utf-8"))
    while True:
        main(server, output_path, quiet_mode)

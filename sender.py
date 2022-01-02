#!/usr/bin/python3.9
# -*- coding: utf-8 -*-

import socket, os, sys, random, time, string, glob
import argparse
from colorama import Fore, Style

### ARGUMENT PARSING
argparser = argparse.ArgumentParser(description="Transfers file and directories between two devices using sockets")
argparser.add_argument("path", nargs="+", type=str, action="store", help="path to the files or directories to send")
argparser.add_argument("--buffer", "-b", type=str, action="store", default=8192, help="sets to this buffer size (default: 8192)", dest="buffer_size")
argparser.add_argument("--host", "-H", type=str, action="store", nargs="?", help="host address to bind on (default: 0.0.0.0)", default="0.0.0.0", dest="host")
argparser.add_argument("--port", "-p", type=int, action="store", nargs="?", dest="port", help="sets to this port (default: 9999)", default=9999)
argparser.add_argument("--no-color", "-n", action="store_false", dest="color_support", help="disables color support (default: True)")
argparser.add_argument("--quiet", "-q", action="store_true", dest="quiet", help="does not print any output except errors")
parser = argparser.parse_args()

host = parser.host
port = parser.port
buffer_size = parser.buffer_size
color_support = parser.color_support
path = parser.path
quiet_mode = parser.quiet

if buffer_size < 21:
    print_error("Buffer size should be greater than or equal to 21 bytes", False)
    sys.exit(1)
# ---

### FOR COLOR SUPPORT
if color_support == True:
    lyellow = Fore.LIGHTYELLOW_EX
    lred = Fore.LIGHTRED_EX
    lblue = Fore.LIGHTBLUE_EX
    lgreen = Fore.LIGHTGREEN_EX
    reset = Fore.RESET
else:
    lyellow = ""
    lblue = ""
    lred = ""
    lgreen = ""
    reset = ""
# ---

### FOR PRINTING TO STDOUT
def print_status(string, quiet_mode):
    if quiet_mode == True:
        pass
    else:
        print(f"{lblue}[*]{reset} {string}")
def print_error(string, quiet_mode):
    if quiet_mode == True:
        pass
    else:
        print(f"{lred}[-]{reset} {string}")
def print_debug(string, quiet_mode):
    if quiet_mode == True:
        pass
    else:
        print(f"{lgreen}[+]{reset} {string}")
def print_line(string, quiet_mode):
    if quiet_mode == True:
        pass
    else:
        print(f"{reset}{string}")
# ---

### FOR SOCKET
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # FOR IPV4 OVER TCP
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

try:
    server_socket.bind((host, port))
except socket.error:
    print_error("Could not bind host to the port", False)
    sys.exit(1)

server_socket.listen(1)
print_status(f"Server started successfully on {lyellow}{host}{reset}:{lyellow}{port}{reset}", quiet_mode)
# ---

client, address = server_socket.accept()
print_status(f"Connected with {lyellow}{address[0]}{reset}:{lyellow}{address[1]}", quiet_mode)
client.send(bytes(f"{buffer_size}", "utf-8"))


def send_file(FILE, BUFFER_SIZE, quiet_mode):
    size = os.path.getsize(FILE)
    client.send(bytes(f"{size:<100}", "utf-8"))
    terminator = ''.join(random.choices(string.ascii_lowercase + string.digits, k=21))
    client.send(bytes(terminator, "utf-8"))
    with open(FILE, mode="rb") as f:
        while (data := f.read(int(BUFFER_SIZE))):
            client.send(data)
    client.send(bytes(terminator, "utf-8"))
    ack = client.recv(1).decode('UTF-8')
    if bool(int(ack)) == True:
        print_status(f"File sent '{lyellow}{FILE}{reset}'", quiet_mode)
    else:
        print_error(f"Could not send file '{lred}{FILE}{reset}'", False)

def main(client, path, quiet_mode, buffer_size):
    for FILE in path:
        if os.path.isdir(FILE) == True:
            if FILE[-1] == "/":
                FILE = FILE[:-1]
            dir_name = os.path.basename(FILE)

            files_and_subdirs = sorted(glob.glob(os.path.join(FILE, "**/*"), recursive=True), key=os.path.isdir, reverse=True)
            for elem in files_and_subdirs:
                if os.path.isdir(elem) == True:
                    elem = elem[len(FILE):]
                    elem = dir_name + elem
                    client.send(bytes(f"[DIR]{elem:<1025}", "utf-8"))
                    status = client.recv(1).decode('UTF-8')
                    if bool(int(status)) == True:
                        print_status(f"Created directory '{lyellow}{elem}{reset}'", quiet_mode)
                    else:
                        print_error(f"Could not create directory '{lred}{elem}{reset}'", quiet_mode)
                elif os.path.isfile(elem) == True:
                    elem2 = elem[len(FILE):]
                    elem2 = dir_name + elem2
                    client.send(bytes(f"[FILE]{elem2:<1024}", "utf-8"))
                    print_status(f"Sending file '{lyellow}{elem}{reset}' ...", quiet_mode)
                    start_time = time.time()
                    send_file(elem, buffer_size, quiet_mode)
                    end_time = time.time()
                    time_taken_to_send_file = end_time - start_time
                    print_debug(f"Time taken: {lgreen}%f{reset}" % time_taken_to_send_file, quiet_mode)
                time.sleep(1)
        elif os.path.isfile(FILE) == True:
            name = os.path.basename(FILE)
            client.send(bytes(f"[FILE]{name:<1024}", "utf-8"))
            print_status(f"Sending file '{lyellow}{FILE}{reset}' ...", quiet_mode)
            start_time = time.time()
            send_file(FILE, buffer_size, quiet_mode)
            end_time = time.time()
            time_taken_to_send_file = end_time - start_time
            print_debug(f"Time taken: {lgreen}%f{reset} seconds" % time_taken_to_send_file, quiet_mode)
            time.sleep(1)
        else:
            try:
                with open(FILE, mode="rb") as f:
                    pass
            except FileNotFoundError:
                print_error(f"No such path exists '{lred}{FILE}{reset}'", False)
            except PermissionError:
                print_error(f"Permission not sufficient to read file '{lred}{FILE}{reset}'", False)
            except Exception:
                print_error(f"Could not read file '{lred}{FILE}{reset}'", False)

client_status = client.recv(1).decode('UTF-8')
if bool(int(client_status)) == True:
    pass
else:
    print_error(f"Cannot send files and directories, exitting", False)
    server.close()
    sys.exit(1)
main(client, path, quiet_mode, buffer_size)

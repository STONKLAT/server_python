#!/usr/bin/env python3
import sys, os
cwd = os.getcwd()
import os.path
import configparser
import pexpect
from pathlib import Path
import fabric
import time
home = str(Path.home())
rows, columns = os.popen('stty size', 'r').read().split()
scriptpath = os.path.dirname(os.path.realpath(__file__))

def endprogram(exitcode):
     exit(exitcode)

if not os.path.isfile(f'{scriptpath}/hosts.ini'):
     print("No hosts file found!\nGenerating one for you in script dir...")
     with open(f'{scriptpath}/hosts.ini', "x") as f:
            f.write(
'''[configuration]
defaultHost = examplehost

#=========Define hosts here=========#
[examplehost]
    ip = 192.142.0.102
    username = root
    password = helloWorld22'''
    )
            print("\nPlease configure the file to use the program")
            exit(0)

try:
    config = configparser.ConfigParser()
    config.read(f'{scriptpath}/hosts.ini')

    defaultHost = config.get('configuration', 'defaultHost')

    ssh_host = config.get(defaultHost, 'ip')
    ssh_username = config.get(defaultHost, 'username')
    ssh_password = config.get(defaultHost, 'password')
except:
    print('''
    \033[0;31mThere was an error with the config.\033[0m
    ''')
    endprogram(1)

def noarg(): 
    print('''
    \033[0;31mNo known argument provided!
    \033[0mAvaible args:
                    login, l --> Connects to the server via ssh

                         run --> Runs a command on the server
                                 Syntax: server run (--in-terminal, -t true/false (default = true)) [command]

                 transfer, t --> Transfers a file to the server
                                 Syntax: server transfer (--host, -h hostname) [file] [destination]

                    add_host --> Adds a new host to the configuration file

                    del_host --> Removes a host from the configuration file

                default_host --> Sets a host to be the default
    ''')
    endprogram(1)
arguments = sys.argv[1:]

if arguments == []: noarg()

if arguments[0] == "login" or arguments[0] == "l":

    cmd = f"ssh {ssh_username}@{ssh_host}"
    print("\n\033[1;30m\033[2m ⚙️  Running ==> \033[0m" + cmd)

    ssh_session = pexpect.spawn(cmd)
    ssh_session.setwinsize(int(rows),int(columns))
    ssh_session.expect('password:')
    print("\n\033[1;30m\033[2m ⚙️  Automatically inputing password ==> \033[0m", end="")
    for _ in range(len(ssh_password)):
         print('*', end="")
    print("")
    ssh_session.sendline(ssh_password)
    ssh_session.interact()

    # End of Program
    endprogram(0)
elif arguments[0] == "transfer" or arguments[0] == "t":
    where = arguments[2].replace(home, "~")

    if not os.path.isfile(arguments[1]):
            print('''
    \033[0;31mThat file does not exist!\033[0m
    ''')
            endprogram(1)
            

    print(f'\nFile to transfer: {arguments[1]}\nServer Location: {where}\n')
    print('Press enter to start transfer (ctrl-c to cancel)')
    input()
    print()
        
    cmd = f"scp {arguments[1]} {ssh_username}@{ssh_host}:{where}"
    print(cmd)

    ssh_session = pexpect.spawn(cmd)
    ssh_session.expect('password:')
    ssh_session.sendline(ssh_password)
    ssh_session.interact()

    # End of Program
    endprogram(0)
elif arguments[0] == "run":
    terminal = True
    if arguments[1] == "--in-terminal" or arguments[1] == "-t":
            if arguments[2].lower() == "false":
               terminal = False
            elif arguments[2].lower() == "true":
                 terminal = True
            else:
                 noarg()
            cmdplacement = 3
    else:
          cmdplacement = 1
    
    command = " ".join(arguments[cmdplacement:])
    
    c = fabric.Connection(ssh_host, port=22, user=ssh_username, connect_kwargs={'password': ssh_password})
    with c:
        try:
            if terminal == False:
                 c.run(f'/bin/bash -c "(nohup {command} >& /dev/null < /dev/null &)"')
                 print(f' ⚙️  Running "{command}" in the background')
            else:
                c.run(command)
        except:
            print(f'''
    \033[0;31mException while running "{command}" on server!\033[0m
    ''')
            endprogram(1)
    endprogram(0)

     
    
elif arguments[0] == "add_host":
    pass # to make later
elif arguments[0] == "del_host":
     pass
elif arguments[0] == "default_host":
     pass
else:
    noarg()
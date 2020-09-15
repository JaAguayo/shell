#! /usr/bin/env python3

import os, sys, re

while(1):
    current_dir = os.getcwd()
    command = input('$ ')
    if command == 'exit':
        sys.exit(1)
        
    elif command == 'help':
        os.write(1,("help was selected\n").encode())
        
    elif command == 'ls':
        dirs = os.listdir(current_dir)
        print('File List')
        print('----------------')
        for file in dirs:
            print(file)
        print('----------------')
    
    elif 'cd' in command:
        if '..' in command:
            change = '..'
        else:
            change = command.split('cd')[1].strip()
        try:
            print(current_dir)
            os.chdir(change)
            new_dir = os.getcwd()
            print(new_dir)
            
        except FileNotFoundError:
            os.write(2,("cd: no such file or directory\n").encode())

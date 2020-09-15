#! /usr/bin/env python3

import os, sys, re

    
def execute_command(command):
    for directory in re.split(':',os.environ['PATH']):
        program = "%s/%s" % (directory, command[0])
        print(program)
        try:
            os.execve(program, command,os.environ)
        except FileNotFoundError:
            pass
        except ValueError:
            pass

def execute_path(command):
    try:
        os.execve(command[0],command,os.environ)
    except FileNotFoundError:
        pass

def execute(command):
    rc = os.fork()
    if rc < 0:
        os.write(2,"Fork failed".encode())
        sys.exit(1)
    elif rc == 0:
        command = [i.strip() for i in re.split('',command)]
        if '/' in command [0]:
            execute_path(command)
        else:
            execute_command(command)
            os.write(2, ("Command %s not found\n" % command[0]).encode())
            sys.exit(1)
    else:
        child_pid_code = os.wait()

def output_redir(command):
    command,file_path = [i.strip() for i in re.split('>',command)]
    file_path = os.getcwd() + '/' + file_path
    print(file_path)
    command = [i.strip() for i in re.split(' ',command)]
    print(command)
    rc = os.fork()
    if rc < 0:
        os.write(2,"Fork failed".encode())
        sys.exit(1)
        
    elif rc == 0:
        os.close(1)
        os.open(file_path,os.O_CREAT | os.O_WRONLY);
        os.set_inheritable(1,True)
        
        execute_command(command)
        
        os.write(2, ("Command %s not found\n" % command[0]).encode())
        sys.exit(1)
    else:
        child_pid_code = os.wait()

def input_redir(command):
    command,file_path = [i.strip() for i in re.split('>',command)]
    file_path = os.getcwd() + '/' + file_path
    print(file_path)
    command = [i.strip() for i in re.split(' ',command)]
    print(command)
    rc = os.fork()
    if rc < 0:
        os.write(2,"Fork failed".encode())
        sys.exit(1)
        
    elif rc == 0:
        os.close(0)
        os.open(file_path,os.O_RDONLY);
        os.set_inheritable(0,True)
        
        execute_command(command)
        
        os.write(2, ("Command %s not found\n" % command[0]).encode())
        sys.exit(1)
    else:
        child_pid_code = os.wait()

def pipe(command):
    r,w = os.pipe()
    for f in (r,w):
        os.set_inheritable(f,True)

while(1):
    current_dir = os.getcwd()
    
    command = input('$ ')

    if command == '':
        continue
    
    elif command == 'exit':
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
            current_dir = os.getcwd()
            print(current_dir)
            
        except FileNotFoundError:
            os.write(2,("cd: no such file or directory\n").encode())

    elif command == 'pwd':
        os.write(1,(current_dir + "\n").encode())

    elif '>' in command:
        output_redir(command)

    elif '<' in command:
        input_redir(command)

    elif '|' in command:
        pipe = True
        print(pipe)

    elif '&' in command:
        background = True
        print(background)

    else:
        command = command.split()
        os.write(2,("%s: command not found\n" % command[0]).encode())

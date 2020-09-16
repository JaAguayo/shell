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
    os.write(2, ("Command %s not found\n" % command[0]).encode())


def input_redir(command):
    
    rc = os.fork()
    
    if rc < 0:
        os.write(2,"Fork failed".encode())
        sys.exit(1)
        
    elif rc == 0:
        os.close(0)
        os.open(command[-1],os.O_RDONLY)
        os.set_inheritable(0,True)

        command = command[0:command.index("<")]
        execute_command(command)

        os.write(2, ("Command %s not found\n" % command[0]).encode())
        sys.exit(1)


    
def output_redir(command):
    
    rc = os.fork()

    if rc < 0:
        os.write(2,"Fork failed".encode())
        sys.exit(1)
        
    elif rc == 0:
        os.close(1)
        os.open(command[-1],os.O_CREAT | os.O_WRONLY)
        os.set_inheritable(1,True)

        command = command[0:command.index(">")]
        execute_command(command)

        os.write(2, ("Command %s not found\n" % command[0]).encode())
        sys.exit(1)

       
def pipe(command):
    i = command.index('|')
    pipe1 = command[0:i]
    pipe2 = command[i+1:len(command)]

    r,w = os.pipe()

    for f in (r,w):
        os.set_inheritable(f,True)
    pipeChild = os.fork()

    if pipeChild < 0:
        os.write(2,"Fork failed".encode())
        sys.exit(1)

    if pipeChild == 0:
        os.close(1)
        os.dup(w)
        os.set_inheritable(1,True)
        for f in (r,w):
            os.close(f)
            
        execute_command(pipe1)

    else:
        os.close(0)
        os.dup(r)
        os.set_inheritable(0,True)
        for f in (r,w):
            os.close(f)

        execute_command(pipe2)
        

while(1):
    current_dir = os.getcwd()
    prompt = '$ '
    if 'PS1' in os.environ:
        prompt = os.environ['PS1']

    try:
        command = [str(i) for i in input(prompt).split()]
    except EOFError:
        sys.exit(1)

    if command == '':
        continue
    
    elif command == 'exit':
        sys.exit(1)
        
    elif command == 'help':
        os.write(1,("help was selected\n").encode())

    elif 'echo' in command:
        os.write(1,(command[1] + "\n").encode())
        
    elif command == 'ls':
        dirs = os.listdir(current_dir)
        for file in dirs:
            os.write(1,(file + "\n").encode())
    
    elif 'cd' in command:
        if '..' in command:
            change = '..'
        else:
            change = command.split('cd')[1].strip()
        try:
            os.chdir(change)
                        
        except FileNotFoundError:
            os.write(2,("cd: no such file or directory\n").encode())

    elif command == 'pwd':
        os.write(1,(current_dir + "\n").encode())

    elif '>' in command:
        output_redir(command)

    elif '<' in command:
        input_redir(command)

    elif '|' in command:
        pipe(command)
        
    elif '&' in command:
        background = True
        print(background)

    elif '/'in command[0]:
        program = command[0]
        try:
            os.execve(program,command,os.environ)
        except FileNotFoundError:
            pass
    else:
        execute_command(command)

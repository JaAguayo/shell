#! /usr/bin/env python3

import os, sys, re


def execute_command(command):
    for directory in re.split(':',os.environ['PATH']): #try each dir in path
        program = "%s/%s" % (directory, command[0]) #getting the path
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
        os.close(0) #close 0 since input is in fd 0
        os.open(command[-1],os.O_RDONLY) #open read only file
        os.set_inheritable(0,True)

        command = command[0:command.index("<")] #get the string before the < as the prog to exec
        execute_command(command)

        os.write(2, ("Command %s not found\n" % command[0]).encode())
        sys.exit(1)


    
def output_redir(command):
    
    rc = os.fork()

    if rc < 0:
        os.write(2,"Fork failed".encode())
        sys.exit(1)
        
    elif rc == 0:
        os.close(1) #close 1 since output is fd 1
        os.open(command[-1],os.O_CREAT | os.O_WRONLY) #open a file to write to
        os.set_inheritable(1,True)

        command = command[0:command.index(">")] #exec the command that is before the >
        execute_command(command)

        os.write(2, ("Command %s not found\n" % command[0]).encode())
        sys.exit(1)

       
def pipe(command):
    i = command.index('|') #gets the number of index where | is
    prog1 = command[0:i] #puts each command into different variables
    prog2 = command[i+1:len(command)]

    r,w = os.pipe() #get the read and write file descriptors

    for f in (r,w):
        os.set_inheritable(f,True)
    pipeChild = os.fork()

    if pipeChild < 0:
        os.write(2,"Fork failed".encode())
        sys.exit(1)

    if pipeChild == 0:
        os.close(1) #close 1 for write since fd 1 is output
        os.dup(w) #dup the fd that is for write from pipe
        os.set_inheritable(1,True) #set fd 1 inheritable
        for f in (r,w):
            os.close(f) #close output/input fds
            
        execute_command(prog1) 

    else:
        os.close(0) #close 0 for read since fd 0 is input
        os.dup(r) #dup the fd for read
        os.set_inheritable(0,True)
        for f in (r,w):
            os.close(f) #close fds

        execute_command(prog2)
        
#shell
while(1):
    current_dir = os.getcwd() #gest current dir
    prompt = '$ '
    if 'PS1' in os.environ:
        prompt = os.environ['PS1'] #sets prompt to $ if PS1 isnt in enviornment

    try:
        command = [str(i) for i in input(prompt).split()] #gets input and splits it
    except EOFError:
        sys.exit(1)

    if command == '': #if nothing is entered it redisplays prompt
        continue
    
    elif command == 'exit': #exit command
        sys.exit(1)    
    
    elif 'echo' in command: #echo command
        os.write(1,(command[1:-1] + "\n").encode())
        
    elif command == 'ls': #list the files in the directory
        dirs = os.listdir(current_dir) #gets list of files
        for file in dirs: 
            os.write(1,(file + "\n").encode()) #loop through list and print
    
    elif 'cd' in command: #change directory
        if '..' in command:
            change = '..' 
        else:
            change = command.split('cd')[1].strip() #gets the dir that is specified after cd
        try:
            os.chdir(change) #change dir with either cd .. or cd <dir>
                        
        except FileNotFoundError:
            os.write(2,("cd: no such file or directory\n").encode())

    elif command == 'pwd':
        os.write(1,(current_dir + "\n").encode()) #prints working dir

    elif '>' in command:
        output_redir(command) #output redirection

    elif '<' in command:
        input_redir(command) #input redirection

    elif '|' in command:
        pipe(command) #piping        
    
    elif '/'in command[0]: #handles path names to execute
        program = command[0]
        try:
            os.execve(program,command,os.environ)
        except FileNotFoundError:
            pass
        #execute commands
    else:
        execute_command(command)


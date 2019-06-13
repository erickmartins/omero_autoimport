#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 12 16:40:47 2018

@author: erick
"""

import subprocess
import shlex
    
    
def get_shares(IP):
    command = "smbclient -L "+ IP + " -A /home/erick/smb_credentials.txt"
#    print(command)
    result = subprocess.check_output(shlex.split(command) )
    result = result.split()
    shares=[]
    started = 0
    for i in range(len(result)):
        if (result[i]=="Disk"):
            shares.append(result[i-1])
            started = 1
        if (result[i]=="IPC" and started == 1):
            break
    return shares


def mount_share(IP, share):
    command = "sudo mount -t cifs //"+IP+"/"+share+" /home/erick/mnt -o credentials=/home/erick/smb_credentials.txt,vers=1.0,rw,dir_mode=0777,file_mode=0777,defaults,noperm"
#    print(command)
    proc = subprocess.Popen(shlex.split(command) ,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    output,err=proc.communicate()
    proc.wait()
#    if err:
#        print(err)


def mount_imported(IP):
    command = "sudo mount -t cifs //"+IP+"/imported"+" /home/erick/mnt_imported -o credentials=/home/erick/smb_credentials.txt,vers=1.0,rw,dir_mode=0777,file_mode=0777,defaults,noperm"
#    print(command)
    proc = subprocess.Popen(shlex.split(command) ,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    output,err=proc.communicate()
    proc.wait()        
        
def get_username():
    command = "cat /home/erick/mnt/.username.txt"
#    print(command)
    proc = subprocess.Popen(shlex.split(command),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    out, err = proc.communicate()
    username = out.rstrip()
    
    return username, err


def get_password():
    command = "cat /home/erick/passfile_omero.txt"
#    print(command)
    proc=subprocess.Popen(shlex.split(command),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    out, err = proc.communicate()
    passw = out.rstrip()
    return passw


def get_list_files():
    
    command = "find /home/erick/mnt/ -type f \( -mmin -43200 -a -mmin +1 \)"
#    print(command)
    proc=subprocess.Popen(shlex.split(command),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    out, err = proc.communicate()
    files = out.split()
    
    return files

def unmount():
    command = "sudo umount /home/erick/mnt"
    print(command)
    proc = subprocess.Popen(shlex.split(command),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    out, err = proc.communicate()  
#    if err:
#        print(err)
    proc.wait()
    
def unmount_imported():
    command = "sudo umount /home/erick/mnt_imported"
    print(command)
    proc = subprocess.Popen(shlex.split(command),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    out, err = proc.communicate()  
#    if err:
#        print(err)
    proc.wait()

def import_file(curr_file,username,passw, f):
    proc = subprocess.Popen(
                        'nice -n 15 /home/erick/OMERO.server/bin/omero '+'import '+
                        curr_file+
#                        ' -f '+
                        ' -T '+ "\"regex:^.*mnt/(?<Container1>.*?)\" "+
                        '-u '+ username+
                        ' --sudo '+ 'root '+
                        '-s '+ 'camdu.warwick.ac.uk '+
                        '-w '+ passw , shell=True, stdout=subprocess.PIPE,stderr=f)
#    print("after import")
    out,err=proc.communicate()
    return out,err
    #           
                

def create_user(username, password):
    command = "/home/erick/OMERO.server/bin/omero login -s camdu.warwick.ac.uk -u root -w "+password
#    print(command)
    proc=subprocess.Popen(shlex.split(command),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    out, err = proc.communicate()
    print(out,err)
    command = "/home/erick/OMERO.server/bin/omero ldap create "+username
#    print(command)
    proc=subprocess.Popen(shlex.split(command),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    out, err = proc.communicate()
    print(out,err)


def move_file(currfile, share):
    
    command = "mkdir /home/erick/mnt_imported/"+share
    print(command)
    proc = subprocess.Popen(shlex.split(command))
    out, err = proc.communicate()
    file_wo_dir,final_dir = recreate_folder(currfile,"/home/erick/mnt","/home/erick/mnt_imported/"+share)
    command = "mv " + currfile + " " + final_dir +"/"+ file_wo_dir
    print(command)
    proc = subprocess.Popen(shlex.split(command))
    out, err = proc.communicate()  
    
    
def parse_log():
    log = open("log.log", "r")
    lines = log.readlines()
    lastsuccess = 0
    currline = 0
    allfiles = []
    for line in lines:
        if "IMPORT_DONE" in line:
            
            this_import = lines[lastsuccess:currline]
            lastsuccess = currline
            files = parse_import(this_import)
            allfiles.extend(files)
        currline += 1
        
    print(allfiles)
    return allfiles



def parse_import(this_import):
    files = []
    for line in this_import:
        if "FILE_UPLOAD_COMPLETE" in line:
            thisfile = line.split(" ")[-1].rstrip()
            files.append(thisfile)
    return files



def recreate_folder(filename,base,output):
    
    
    file_split = filename.split("/")
    base_split = base.split("/")
    i = len(base_split)
    
    fold_string = ""    
    while i < len(file_split)-1:
        folder = file_split[i]
        fold_string = fold_string + "/" + folder
        command = "mkdir "+ output + "/"+fold_string
        proc = subprocess.Popen(shlex.split(command),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        out, err = proc.communicate()
        i += 1
    return file_split[-1],output + "/"+fold_string








def from_dvs(IP):
    
    
    shares = get_shares(IP)
#    shares = ['ratamero']
    print(shares)
    
    
    mount_imported(IP)
    
    for share in shares:
        if share == "imported":
            print("IMPORTED SHARE - SKIPPING")
            continue
        print("share="+share)
        
        mount_share(IP, share)
        ####### importing code goes here #########    
        command = "/home/erick/OMERO.server/bin/omero sessions clear"
#        print(command)
        proc = subprocess.Popen(shlex.split(command),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        out, err = proc.communicate()
        username, err = get_username()
        if err:
            print(err)
        else:
            
            print(username)
            passw = get_password()
            create_user(username, passw)
#            
            ###### find all files older than an hour, newer than a month, save list to text file
            files = get_list_files()
            print(files)
            # read text file and loop over files importing and moving
            for curr_file in files:
                f = open('log.log', 'w')
                print("importing "+curr_file)
                out,err=import_file(curr_file,username,passw, f)
                f.close()    
                filestomove = parse_log()
            
                for curr_file in filestomove:
                    move_file(curr_file, share)
                
#            print("test:",passw, username)
#            
            
#            
            unmount()
    
    unmount_imported()

if __name__=="__main__":
    IP="192.168.10.122"
    from_dvs(IP)
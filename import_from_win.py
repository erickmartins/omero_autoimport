#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 12 16:40:47 2018

@author: erick
"""

import subprocess
import shlex


def get_folders(folder):
    command = "ls -p /home/erick/"+folder
#    print(command)
    result = subprocess.check_output(shlex.split(command))
    folders = result.split()
    filtered_folders = [x for x in folders if x.endswith("/")]
    for i in range(len(filtered_folders)):
        filtered_folders[i] = filtered_folders[i][:-1]
    return filtered_folders


def create_folder(folder):
    command = "mkdir \"/home/erick/" + folder + "\""
    print(command)
    proc = subprocess.Popen(shlex.split(command))
    out, err = proc.communicate()
    proc.wait()
    if err:
        print(err)



def mount_share(IP, vers, folder):
    command = "sudo mount -t cifs //" + IP + "/Data" + " /home/erick/" + folder + " -o credentials=/home/erick/smb_credentials.txt,vers=" + \
        str(vers) + ",rw,dir_mode=0777,file_mode=0777,defaults"
#    print(command)
    proc = subprocess.Popen(shlex.split(
        command), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = proc.communicate()
    proc.wait()
    if err:
        print(err)


def mount_petabyte():
    command = "cat /home/erick/ads_credentials.txt"
    proc = subprocess.Popen(shlex.split(
        command), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    credentials = out.rstrip()
    command = "sudo mount -t cifs //ads.warwick.ac.uk/shared/HCSS2/Shared243/" + \
        " /home/erick/mnt_petabyte -o " + \
        str(credentials) + ",vers=3.0" + \
        ",rw,dir_mode=0777,file_mode=0777,defaults"
    print(command)
    proc = subprocess.Popen(shlex.split(
        command), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = proc.communicate()
    proc.wait()
    if err:
        print(err)


def get_username(micro, folder):
    command = "cat /home/erick/"+micro+"/"+ folder + "/.username.txt"
#    print(command)
    proc = subprocess.Popen(shlex.split(
        command), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    username = out.rstrip()

    return username, err


def get_password():
    command = "cat /home/erick/passfile_omero.txt"
#    print(command)
    proc = subprocess.Popen(shlex.split(
        command), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    passw = out.rstrip()
    return passw


def get_list_files(micro, folder):

    command = "find /home/erick/" + micro +"/"+ folder + \
        "/ -type f \( -mmin -43200 -a -mmin +60 \)"
#    command = "find /home/erick/" + micro +"/"+ folder + \
#        "/ -type f "
    print(command)
    proc = subprocess.Popen(shlex.split(
        command), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    files = out.split("\n")
    mvd2s = [s for s in files if "mvd2" in s]
    print(mvd2s)
    files_sorted = mvd2s + sorted(files,key=len)
    return files_sorted


def unmount(micro):
    command = "sudo umount /home/erick/" + micro
    print(command)
    proc = subprocess.Popen(shlex.split(
        command), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    if err:
        print(err)
    proc.wait()


def unmount_petabyte():
    command = "sudo umount /home/erick/mnt_petabyte"
    print(command)
    proc = subprocess.Popen(shlex.split(
        command), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    if err:
        print(err)
    proc.wait()


def import_file(curr_file, username, passw, f, complete, micro):
    proc = subprocess.Popen(
        'nice -n 15 /home/erick/OMERO.server/bin/omero ' + 'import \"' +
        curr_file +
        '\" -T ' + "\"regex:^.*"+micro+"/.*?/(?<Container1>.*?)\" " +
        '-u ' + username +
        ' --sudo ' + 'root ' +
        '-s ' + 'camdu.warwick.ac.uk ' +
        '-w ' + passw + ' --skip upgrade --exclude=clientPath', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#    print("after import")
    out, err = proc.communicate()
    f.write(err)
    complete.write(err)
    return out, err
    #


def create_user(username, password):
    command = "/home/erick/OMERO.server/bin/omero login -s camdu.warwick.ac.uk -u root -w " + password
#    print(command)
    proc = subprocess.Popen(shlex.split(
        command), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    print(out, err)
    command = "/home/erick/OMERO.server/bin/omero ldap create " + username
#    print(command)
    proc = subprocess.Popen(shlex.split(
        command), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    print(out, err)


def move_file(currfile, folder, micro):

    command = "mkdir /home/erick/"+micro+"/imported/" + folder
    print(command)
    proc = subprocess.Popen(shlex.split(command))
    out, err = proc.communicate()
    file_wo_dir, final_dir = recreate_folder(
        currfile, "/home/erick/" + micro + "/"+folder, "/home/erick/"+micro+"/imported/" + folder)
    command = "mv \"" + currfile + "\" \"" + final_dir + "/" + file_wo_dir + "\""
    print(command)
    proc = subprocess.Popen(shlex.split(command))
    out, err = proc.communicate()
    if err:
        print(err)


def copy_file_to_petabyte(currfile, folder, micro):

    command = "mkdir /home/erick/mnt_petabyte/" + folder
    print(command)
    proc = subprocess.Popen(shlex.split(command))
    out, err = proc.communicate()
    file_wo_dir, final_dir = recreate_folder(
        currfile, "/home/erick/" + micro + "/"+folder, "/home/erick/mnt_petabyte/" + folder)
    command = "cp \"" + currfile + "\" \"" + final_dir + "/" + file_wo_dir + "\""
    print(command)
    proc = subprocess.Popen(shlex.split(command))
    out, err = proc.communicate()
    if err:
        print(err)


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
            thisfile = line.split("FILE_UPLOAD_COMPLETE: ")[-1].rstrip()
            files.append(thisfile)
    return files


def recreate_folder(filename, base, output):

    file_split = filename.split("/")
    base_split = base.split("/")
    i = len(base_split)
#    print(file_split,base_split)

    fold_string = ""
    while i < len(file_split) - 1:
        folder = file_split[i]
        fold_string = fold_string + "/" + folder
        command = "mkdir \"" + output + "/" + fold_string + "\""
        proc = subprocess.Popen(shlex.split(
            command), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()
        i += 1
    return file_split[-1], output + "/" + fold_string


def from_win(IP, vers, isLattice, micro):
    create_folder(micro)
    mount_share(IP, vers, micro)
    if isLattice:
        mount_petabyte()
    folders = get_folders(micro)
#    shares = ['ratamero']
    print(folders)
    complete = open('log_complete.log', 'a', 0)

    for folder in folders:
        if folder == "imported":
            print("IMPORTED FOLDER - SKIPPING")
            continue
        print("folder=" + folder)

        ####### importing code goes here #########
        command = "/home/erick/OMERO.server/bin/omero sessions clear"
#        print(command)
        proc = subprocess.Popen(shlex.split(
            command), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()
        username, err = get_username(micro,folder)
        if err:
            print(err)
        else:
            #
            print(username)
            passw = get_password()
            create_user(username, passw)
##
#            ###### find all files older than an hour, newer than a month, save list to text file
            files = get_list_files(micro, folder)

            print(files)
            for curr_file in files:
                if isLattice:
                    copy_file_to_petabyte(curr_file, folder, micro)
#            # read text file and loop over files importing and moving
            for curr_file in files:

                f = open('log.log', 'w', 0)
                print("importing " + curr_file)
                out, err = import_file(curr_file, username, passw, f, complete, micro)
                f.close()
                filestomove = parse_log()

                for curr_file in filestomove:
                    move_file(curr_file, folder, micro)

#            print("test:",passw, username)
#

#

    unmount(micro)
    if (isLattice):
        unmount_petabyte()
    complete.close()

if __name__ == "__main__":
    IP = "137.205.90.190"
    from_win(IP, 3.0)

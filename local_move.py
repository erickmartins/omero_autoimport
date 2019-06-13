
def move_files(listfile):
    import subprocess
    import shlex
    import os
    f = open(listfile)
    lines = f.readlines()
    for line in lines:
        eachfile = line.split("\"")
        files = []
        for s in eachfile:
            if (s != '' and s!=' '):
                files.append(s)
        base = "/".join(files[0].split("/")[0:2])
        recreate_folder(files[0], base, base + "/imported/")
        command = "mv \"" + files[0] + "\" \"" + files[1]+"\""
        print(command)
        proc = subprocess.Popen(shlex.split(command))
        out, err = proc.communicate()
        if err:
            print(err)


def recreate_folder(filename, base, output):

    file_split = filename.split("/")
    base_split = base.split("/")
    i = len(base_split)

    fold_string = ""
    while i < len(file_split) - 1:
        folder = file_split[i]
        fold_string = fold_string + "/" + folder
        command = "mkdir \"" + output + "/" + fold_string + "\""
        proc = subprocess.Popen(shlex.split(
            command), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()
        i += 1
    return 


if __name__ == "__main__":
    from glob import glob
    import os
    import subprocess
    import shlex
    folders = glob("/data1/*/")
    for folder in folders:
        print(folder)
        if os.path.isfile(folder+".listimport.txt"):
            move_files(folder+".listimport.txt")
            command = "rm "+folder+".listimport.txt"
            print(command)
            proc = subprocess.Popen(shlex.split(command))
            out, err = proc.communicate()
            if err:
                print(err)
        else:
            print("no file found")

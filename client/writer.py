def write(file, msg, mode):
    f = open(file, mode)
    f.write(msg)
    f.close

def GetHashofDirs(directory, verbose=0):
    import hashlib, os
    SHAhash = hashlib.sha256()
    if not os.path.exists(directory):
        return -1

    try:
        for root, dirs, files in os.walk(directory):
            dirs.sort()
            for names in sorted(files):
                if verbose == 1:
                    print(
                    'Hashing', names)
                filepath = os.path.join(root, names)
                try:
                    f1 = open(filepath, 'rb')
                except:
                    # You can't open the file for some reason
                    f1.close()
                    continue

                while 1:
                    # Read file in as little chunks
                    buf = f1.read(4096)
                    if not buf: break
                    buf = str(buf).encode()
                    SHAhash.update(buf)
                f1.close()

    except:
        import traceback
        # Print the stack traceback
        traceback.print_exc()
        return -2

    return SHAhash.hexdigest()

print(GetHashofDirs('output', 1))

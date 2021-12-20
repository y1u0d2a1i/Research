def fix_orthogonal(path_to_target):
    with open(path_to_target, mode='r') as f:
        l_strip = [s.strip() for s in f.readlines()]
        for i, line in enumerate(l_strip):
            if 'zlo zhi' in line:
                fix_word = "0.0 0.0 0.0 xy xz yz"
                l_strip.insert(i + 1, fix_word)
    with open(path_to_target, mode='w') as f:
        for line in l_strip:
            f.write(line + '\n')

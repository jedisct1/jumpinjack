#! /usr/bin/env python

import getopt
import sys
import re

file, line_nb = None, 0

affected_files = {}


def tag_file(affected_file, affected_lines):
    with open(affected_file) as f:
        tagged_file = affected_file + ".tagged"
        with open(tagged_file, "w") as h:
            line_nb = 0
            for line in f:
                line_nb = line_nb + 1
                if line_nb in affected_lines:
                    detail = affected_lines[line_nb]
                    if re.match(".*(for|while|do|if|else|assert|break|continue|switch|return|\}).*", line):
                        line = line.rstrip() + "\t/*** JJ: JUMP (" + detail + ") ***/\n"
                    else:
                        line = line.rstrip() + "\t/*** JJ: JUMP! (" + detail + ") ***/\n"
                h.write(line)
            print(tagged_file)


def tag(base_dir, dump_file):
    file, line_nb = None, 0
    for line in open(dump_file):
        if re.match("^/.+[.].+:[0-9]+$", line):
            file_, line_nb_ = line.strip().split(':')
            if file_.startswith(base_dir):
                file, line_nb = file_, int(line_nb_)
            else:
                file, line_nb = None, 0
            continue

        if not file:
            continue

        parts = line.strip().split("\t")
        if len(parts) < 3:
            continue

        opcode = parts[2].split(' ')[0]

        if not re.match("^(ja|jae|jb|jbe|jc|jcxz|je|jecxz|jg|jge|jl|jle|jna|jnae|" +
                        "jnb|jnbe|jnc|jne|jng|jnge|jnl|jnle|jno|jnp|jns|jnz|jo|" +
                        "jp|jpe|jpo|js|jz)$", opcode):
            continue

        if file not in affected_files:
            affected_files[file] = {}

        affected_files[file][line_nb] = re.sub("\s+", " ", parts[2])

    for affected_file in affected_files:
        try:
            tag_file(affected_file, affected_files[affected_file])
        except IOError:
            pass


def usage():
    print("Usage: jumpinjack.py -b <base dir> -d <objdump file>")
    sys.exit(2)

try:
    opts, args = getopt.getopt(sys.argv[1:], "b:d:")
except getopt.GetoptError as err:
    usage()

base_dir, dump_file = None, None

for o, a in opts:
    if o == "-b":
        base_dir = a
    elif o == "-d":
        dump_file = a

if (not base_dir) or (not dump_file):
    usage()

tag(base_dir, dump_file)

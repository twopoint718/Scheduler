import os
from pyparsing import Word, alphas, nums, oneOf
import pyparsing
import sys

def parse_line(txt):
    # Pseudo BNF for config format
    #  <dow>,<start> <sectionPart> <end>
    #
    # dow         := "M" | "T" | "W" | "R" | "F"
    # start       := digits ":" digits
    # sectionPart := specSection | digits name | "c" | "C"
    # specSection := "(" digits ")" digits
    # end         := digits ":" digits
    # name        := alpha

    day_of_week = oneOf(list("MTWRF"))
    time        = Word(nums) + ":" + Word(nums)
    start_block = day_of_week + "," + time
    name        = Word(alphas + "'" + " " + "-")
    section     = Word(nums)
    specSection = "(" + Word(nums) + ")" + section
    sectionPart = specSection + name | section + name | oneOf(list("Cc"))
    line        = start_block + sectionPart + time

    # Parse Actions (run when a parse succeeds)
    # group the times and the start block as a single string, get rid of
    # possible trailing blanks on names
    time.setParseAction(lambda x: "".join(x))
    start_block.setParseAction(lambda x: "".join(x))
    name.setParseAction(lambda x: x[0].strip())
    # format the specSection better
    specSection.setParseAction(lambda x: "(%s) %s" % (x[1], x[3]))
    def if_c_then_uppercase(x):
        """If the sectionPart is a consultation block, always use an upper C"""
        if x[0] == "c" or x[0] == "C":
            return "C"
        else:
            return x
    sectionPart.setParseAction(if_c_then_uppercase)

    try:
        result = line.parseString(txt)
        return result
    except pyparsing.ParseException as e:
        print("error on text: [%s]" % txt)
        print(str(e))
        sys.exit(1)
    return


def parse_all_lines(txt):
    """Parse a block of text (has newlines), return as a dictionary mapping
    the first element of each line to the parsed line e.g.

    "T,7:45 305 Baz 9:40\n" --> {"T,7:45" : ['T,7:45', '305', 'Baz', '9:40'] }
    """
    txt = txt.split("\n")
    out = dict()
    for line in txt:
        line = line.strip()
        if line.startswith("#") or len(line) < 5:
            continue
        lst = parse_line(line)
        out[lst[0]] = lst[1:]
    return out

def parse_file(filename):
    """Return a dict like:

    {"103,4320":
      {"M,8:00":  ["M,8:00", "C", "11:00"],
       "M,12:05": ["M,12:05", "301", "McNally", "14:00"],
       ...
      }
    }

    The course and room number come from the name of the input file.
    """
    k = filename[:-4] # drop ".txt"
    course, room = k.split("_")
    with open(filename, "r") as f:
        d = parse_all_lines(f.read())
        return ("%s,%s" % (course, room), d)

def parse_all():
    files = filter(lambda f: f.endswith(".txt"), os.listdir("."))
    out = dict()
    for filename in files:
        k, d = parse_file(filename)
        out[k] = d
    return out

if __name__ == "__main__":

    import pprint
    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint(parse_all())

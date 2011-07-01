import os
from pyparsing import Word, alphas, nums, oneOf
from sched_util import Section

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
    name        = Word(alphas + "'" + " " + "/")  # what's in a name?
    section     = Word(nums)
    specSection = "(" + Word(nums) + ")" + section
    sectionPart = specSection + name | section + name | oneOf(list("Cc"))
    line        = start_block + sectionPart + time

    # Parse Actions (run when a parse succeeds)
    # group the times and the start block as a single string, get rid of
    # possible trailing blanks on names
    time.setParseAction(lambda x: [i for i in x if i != ':'])
    start_block.setParseAction(lambda x: [i for i in x if i != ','])
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

    # parse: ['M', '12', '05', '301', 'Ojalvo', '14', '00']
    day, h1, m1, sect, ta, h2, m2 = line.parseString(txt)
    return Section(day, (int(h1), int(m1)), int(sect), ta, (int(h2),int(m2)))

def parse_all_lines(txt):
    """Parse a block of text (has newlines), return as a list of Section
    objects
    """
    txt = txt.split("\n")
    out = list()
    for line in txt:
        line = line.strip()
        if line.startswith("#") or len(line) < 5:
            continue
        sect = parse_line(line)
        out.append(sect)
    return out

def parse_file(filename):
    """Return a dict like: 

    {(103,4320):
       [Section("M", (12, 5), 301, "McNally", (14, 0)),
       ...
       ]
      }
    }
    """
    k = filename[:-4] # drop ".txt"
    course, room = k.split("_")
    with open(filename, "r") as f:
        sect_list = parse_all_lines(f.read())
        return ((int(course), int(room)), sect_list)

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

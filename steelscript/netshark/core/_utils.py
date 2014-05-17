# Copyright (c) 2014 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.




def str_to_filename(s):
    s = s.replace(":", "-")
    s = s.replace("?", "-")
    s = s.replace("*", "-")
    s = s.replace(";", "-")
    s = s.replace("{", "-")
    s = s.replace("}", "-")
    s = s.replace("&", "-")
    s = s.replace("\\", "-")
    s = s.replace(".", "-")
    s = s.replace("/", "-")
    return s

def parse_encoded_avg(s, precise=False):

    comp = s.split(':')

    if precise:
        return float(comp[0]) / float(comp[1])
    else:
        return int(comp[0]) / int(comp[1])

def value_to_int(s, precise=False):
    comp = s.split(':')

    if len(comp) == 1:
        if precise:
            return float(s)
        else:
            return int(s)
    elif len(comp) == 2:
        if precise:
            return float(comp[0]) / float(comp[1])
        else:
            return int(comp[0]) / int(comp[1])
    else:
        return 0

import re
from editdistance import eval as lev_dist


def n_syllables(pronunciation):
    if isinstance(pronunciation, list):
        pronunciation = ' '.join(pronunciation)

    return sum(c.isdigit() for c in pronunciation)


def rhyme_pattern(pronunciation):
    if isinstance(pronunciation, list):
        pronunciation = ' '.join(pronunciation)
    
    match = re.search(r'\w{1,2}[12].*', pronunciation)

    if match is not None:
        return match.group(0)
    else:
        return pronunciation


def slant_distance(pattern1, pattern2):
    if isinstance(pattern1, str):
        pattern1 = pattern1.split(' ')

    if isinstance(pattern2, str):
        pattern2 = pattern2.split(' ')

    return lev_dist(pattern1, pattern2)

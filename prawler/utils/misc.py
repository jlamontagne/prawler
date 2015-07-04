import re
from bs4 import NavigableString

def decompose_all(s):
    for tag in s:
        if isinstance(tag, NavigableString):
            tag.replace_with('')
        else:
            tag.decompose()

def text(x):
    if isinstance(x, NavigableString):
        x = unicode(x)
    elif not isinstance(x, basestring):
        x = ' '.join(x.stripped_strings)

    x = re.sub('(\r\n)|\r|\n', '', x).replace('\t', ' ')
    return x.strip()

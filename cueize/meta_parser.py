import re
from song import Song

def parse_album(line):
    match = re.compile(r'\W*(\d+)(\w+)[「『](.*)[」』]$').match(line)
    return (False, match.group(1) + match.group(2) + ' ' + match.group(3)) if match else (True, '')

def parse_release_date(line):
    match = re.compile(r'^リリース\s*(\d+)年(\d+)月(\d+)日$').match(line)
    return '%d.%02d.%02d' % (int(match.group(1)), int(match.group(2)), int(match.group(3))) if match else ''

def parse_date(line):
    match = re.compile(r'^(\d+)年(\d+)月(\d+)日$').match(line)
    return '%d.%02d.%02d' % (int(match.group(1)), int(match.group(2)), int(match.group(3))) if match else ''

def parse_performer(line, terminal):
    match = re.compile(r'^(.*) の ' + terminal).match(line)
    return match.group(1) if match else ''

def parse_disc_no(line):
    match = re.compile(r'CD\s*[（\(]Disc\s*(\d+)[）)]$')
    return int(match.group(1)) if match else 0

def assign_new_track_id(collection):
    songs = sorted(collection, key=lambda song: (song.is_off_vocal, 
        song.thetype if song.thetype.startswith('Type') else ('Z' + song.thetype), song.track_id))
    idx = 1
    for song in songs:
        song.index = idx
        idx += 1
    return songs

def get_prefix(meta, others=None):
    title = meta['title'] + ('' if others is None or 'type_str' not in others else ('[%s]' % others['type_str']))
    if 'single_id' in meta:
        title = get_order(meta['single_id']) + ' ' + title
    return ['REM DATE %s' % meta['date'], 'PERFORMER "%s"' % meta['performer'], 'TITLE "%s"' % title]

def normalize_with_space(text):
    o_s = '０１２３４５６７８９ＡＢＤＥＧＨＪＫＭＮＳＴＵ〜～：／'
    n_s = '0123456789ABDEGHJKMNSTU~~:/'
    return text.translate(str.maketrans(o_s, n_s, '？?！!·…。“”\xa0'))

def normalize_full_width(text):    
    o_s = '０１２３４５６７８９ＡＢＤＥＧＨＪＫＭＮＳＴＵ〜～：／？！＃'
    n_s = '0123456789ABDEGHJKMNSTU~~:/?!#'
    return text.translate(str.maketrans(o_s, n_s))

def normalize(text):
    return normalize_with_space(text).translate(str.maketrans('', '', '　 \u3000'))

def purge_line(line):
    return re.sub('\[注 \d+\]', '', line)

def get_other_disc_type():
    return ['劇場盤', '剧场盘', '通常盤', '通常盘', 'NGT48 CD盤', 'セブン-イレブン限定盤', 'アニメ盤']

def get_order(single_id):
    surfix = ''
    if single_id % 100 >= 11 and single_id % 100 <= 13:
        surfix = 'th'
    elif single_id % 10 == 1:
        surfix = 'st'
    elif single_id % 10 == 2:
        surfix = 'nd'
    elif single_id % 10 == 3:
        surfix = 'rd'
    else:
        surfix = 'th'
    return '%d%s' % (single_id, surfix)

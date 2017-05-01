import re
from song import Song

def parse_album(line):
    match = re.compile(r'\W*(\d+)(\w+)[「『](.*)[」』]$').match(line)
    return (False, match.group(1) + match.group(2) + ' ' + match.group(3)) if match else (True, '')

def parse_release_date(line):
    match = re.compile(r'^リリース\s*(\d+)年(\d+)月(\d+)日$').match(line)
    return '%d.%02d.%02d' % (int(match.group(1)), int(match.group(2)), int(match.group(3))) if match else ''

def parse_performer(line, terminal):
    match = re.compile(r'^(.*) の ' + terminal).match(line)
    return match.group(1) if match else ''

def parse_disc_no(line):
    match = re.compile(r'CD\s*[（\(]Disc\s*(\d+)[）)]$')
    return int(match.group(1)) if match else 0

def assign_new_track_id(collection):
    songs = sorted(collection, key=lambda song: (song.is_off_vocal, 
        song.thetype if song.thetype.startswith('Type') else '劇場盤', song.track_id))
    idx = 1
    for song in songs:
        song.index = idx
        idx += 1
    return songs

def get_prefix(meta, others=None):
    title = meta['title'] + ('' if others is None or 'type_str' not in others else ('[%s]' % others['type_str']))
    return ['REM DATE %s' % meta['date'], 'PERFORMER "%s"' % meta['performer'], 'TITLE "%s"' % title]

def normalize(text):
    o_s = '０１２３４５６７８９ＡＢＤＥＧＨＪＫＭＮＳＴＵ'
    n_s = '0123456789ABDEGHJKMNSTU'
    return text.translate(str.maketrans(o_s, n_s, '　 ？?！!·…'))

def purge_line(line):
    return re.sub('\[注 \d+\]', '', line)

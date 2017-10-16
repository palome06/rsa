from song import Song
import meta_parser
import re

table={}
wiki_style=None

def decide_wiki_style(line):
    if line.startswith('#'):
        return
    global wiki_style
    match = re.compile(r'(?P<track_id>\d+)\..*\s+「(?P<title>.*)」(\((?P<performer>[\w\s]+)\))?.*(?P<length>\d+:\d+)').match(line)
    if match:
        wiki_style = 'standard'
        return
    wiki_style = 'others'

def handle_with_line(thetype, track_id, line):
    global wiki_style
    if not wiki_style:
        decide_wiki_style(line)
    if wiki_style == 'standard':
        handle_with_line_standard(thetype, line)
    elif wiki_style == 'others':
        handle_with_line_others(thetype, track_id, line)

def handle_with_line_others(thetype, track_id, line):
    if not line or line.startswith('作詞：') or line.startswith('作詞:') or thetype == None:
        return False
    with_performer = True
    match = re.compile(r'^\s*(?P<title>.+?)( - (?P<performer>.+?))?( \[(?P<length>\d+:\d+)\])?$').match(line)
    if not match:
        return False
    title = match.group('title')
    performer = match.group('performer')
    length = match.group('length')
    song = Song(track_id, title, performer, False, length)
    song.thetype = thetype
    no_title = meta_parser.normalize(title)
    if thetype not in table:
        table[thetype] = {}
    if no_title not in table[thetype]:
        table[thetype][no_title] = song
    return True

def handle_with_line_standard(thetype, line):
    if thetype == None:
        return False
    with_performer = True
    line = re.sub('\[注 \d+\]', '', line)
    match = re.compile(r'(?P<track_id>\d+)\..*\s+「(?P<title>.*)」(\((?P<performer>[\w\s]+)\))?.*(?P<length>\d+:\d+)').match(line)
    if not match:
        return False
    track_id = match.group('track_id')
    title = match.group('title')
    performer = match.group('performer')
    length = match.group('length')
    is_off_vocal = False
    print(line, 't', track_id, 'ti', title, 'p', performer, 'l', length, 'o', is_off_vocal)
    if title.lower().find("off vocal") >= 0:
        is_off_vocal = True
        title = re.sub('\s*[\-(（]?off vocal ver(\.)?[\-)）]?\s*$', '', title)
    song = Song(track_id, title, performer, is_off_vocal, length)
    song.thetype = thetype
    no_title = meta_parser.normalize(title)
    if thetype not in table:
        table[thetype] = {}
    if no_title not in table[thetype]:
        table[thetype][no_title] = song
    return True

def load_wikipedia(filename):
    meta = {}
    with open(filename, encoding='utf-8') as f:
        content = f.readlines()
        content = [x.strip() for x in content]
        will_read = False
        thetype = None
        first_line = True
        track_id = 0
        for line in content:
            if not will_read:
                if first_line:
                    first_line, album = meta_parser.parse_album(line)
                    meta['title'] = album
                if line.startswith('リリース'):
                    meta['date'] = meta_parser.parse_release_date(line)
                elif line.endswith('アルバム'):
                    meta['performer'] = meta_parser.parse_performer(line, 'スタジオ・アルバム')
            if line.startswith('Type') or line in ['劇場盤']:
                thetype = line
                track_id = 1
            elif line.lower().startswith('disc'):
                thetype = line
                if line.find('(') >= 0 and line.lower().count('type') >= 2:
                    thetype = line[:line.find('(')].strip()
                track_id = 1
            elif line.startswith('CD'):
                will_read = True
                # disc_no = parse_disc_no(line.lower())
            elif line.startswith('DVD'):
                will_read = False
            else:
                if will_read:
                    success = handle_with_line(thetype, track_id, meta_parser.purge_line(line))
                    if success:
                        track_id += 1
    return meta

def deal_with_all_files(root_path):
    import os
    for root, dirs, files in os.walk(root_path):
        if len(files) <= 0:
            continue
        rel_path_str = root[(len(root_path) + 1):]
        rel_path = rel_path_str.split(sep='\\')
        if len(rel_path) == 2 and rel_path[1].lower().startswith('disc'): # Genre 01: Type A/Disc 2
            rel_type_str = rel_path[0]
            if rel_type_str.startswith('Type'):
                type_str = 'Type-' + rel_type_str[len('Type-'):]
            elif rel_type_str in meta_parser.get_other_disc_type():
                type_str = rel_type_str
            else:
                continue
            rel_disc_str = rel_path_str[1]
            if rel_path_str.startswith('Disc '):
                disc_no = int(rel_disc_str[len('Disc '):])
            elif rel_path_str.startswith('Disc'):
                disc_no = int(rel_disc_str[len('Disc'):])
            if type_str not in table:
                continue
        elif len(rel_path) == 1 and rel_path[0].lower().startswith('disc'): # Genre 02: DISC 2 (Type-A)
            type_str = rel_path[0]
            left_branck = type_str.find('(') # of no use now, I thinks
            if left_branck >= 0:
                real_type = type_str[(left_branck + 1):(type_str.find(')'))].strip()
                disc_no_str = type_str[:left_branck].strip()
            else:
                real_type = ''
                disc_no_str = type_str
        else:
            continue
        for file in files:
            fn = meta_parser.normalize(file)            
            if not any(fn.endswith(suffix) for suffix in ['.wav', '.mp3', '.flac', '.ape', '.m4a']):
                continue
            for keyname, song in table[type_str].items():
                if (fn.find(keyname) >= 0):
                    if not song.pure_filename or len(song.pure_filename) > len(file):
                        song.set_file(rel_path_str, file)

def write_cue(root_path, meta):
    import os
    for type_str in table.keys():
        prefix = meta_parser.get_prefix(meta, {'type_str':type_str})
        with open(root_path + '/' + type_str + '-Set.cue', 'w', encoding='utf-8-sig') as f:
            f.writelines("%s\n" % l for l in prefix)
            for song in meta_parser.assign_new_track_id(table[type_str].values()):
                f.writelines("%s\n" % l for l in song.to_cue_item())

def run(wiki_path, root_path):
    print('Enter Type-B')
    print('Loading wikipedia...')
    meta = load_wikipedia(wiki_path)
    print('Deal with all files...')
    deal_with_all_files(root_path)
    print('Writing cue...')
    write_cue(root_path=root_path, meta=meta)

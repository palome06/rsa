# songs in different directory
from song import Song
import meta_parser
import re
import type_a

table={}

def handle_with_line(thetype, line):
    if thetype == None:
        return
    with_performer = True
    line = re.sub('\[注 \d+\]', '', line)
    match = re.compile(r'(?P<track_id>\d+)\..*\s+「(?P<title>.*)」(\((?P<performer>[\w\s]+)\))?.*(?P<length>\d+:\d+)').match(line)
    if not match:
        return
    track_id = match.group('track_id')
    title = match.group('title')
    performer = match.group('performer')
    length = match.group('length')
    is_off_vocal = False
    if title.lower().find("off vocal") >= 0:
        is_off_vocal = True
        title = re.sub('\s*[\-(（]?off vocal ver(\.)?[)）\-]?\s*$', '', title)
    song = Song(track_id, title, performer, is_off_vocal, length)
    song.thetype = thetype
    pair = (meta_parser.normalize(title), is_off_vocal)
    if thetype not in table:
        table[thetype] = {}
    if pair not in table[thetype]:
        table[thetype][pair] = song

def load_wikipedia(filename):
    meta = {}
    with open(filename, encoding='utf-8') as f:
        content = f.readlines()
        content = [x.strip() for x in content]
        will_read = False
        thetype = None
        first_line = True
        mode = 'meta_mode'
        patch_song = None
        for line in content:
            if line == '':
                continue
            elif line.startswith('シングル収録トラック'):
                mode = 'track_mode'
                will_read = False
                continue
            elif line.startswith('選抜メンバー'):
                mode = 'unit_mode'
                will_read = False
                continue

            if mode == 'meta_mode':
                if first_line:
                    first_line, album = meta_parser.parse_album(line)
                    meta['title'] = album
                if line.startswith('リリース'):
                    meta['date'] = meta_parser.parse_release_date(line)
                elif line.endswith('の シングル'):
                    meta['performer'] = meta_parser.parse_performer(line, 'シングル')
            elif mode == 'track_mode':
                if line.startswith('Type') or line in meta_parser.get_other_disc_type():
                    thetype = line
                elif line.startswith('CD'):
                    will_read = True
                elif line.startswith('DVD'):
                    will_read = False
                else:
                    if will_read:
                        handle_with_line(thetype, meta_parser.purge_line(line))
            elif mode == 'unit_mode':
                line = re.sub('\[[\s\w]+\]', '', line)
                nline = meta_parser.normalize(line)
                if (nline, False) in table:
                    will_read = True
                    patch_song = table[(nline, False)]
                elif will_read and patch_song and (not patch_song.performer or patch_song.performer == ''):
                    match = re.compile(r'.*ユニット：([^），、]+).*').match(line)
                    will_read = False
                    if match:
                        patch_song.performer = match.group(1)
                    elif line.find('、') < 0 and line.find('：') < 0:
                        patch_song.performer = line
                    else:
                        will_read = True
    return meta

def deal_with_all_files(root_path):
    import os
    for root, dirs, files in os.walk(root_path):
        if len(files) <= 0:
            continue
        rel_path_str = root[(len(root_path) + 1):]
        if len(rel_path_str) == 0 or rel_path_str.find('\\') >= 0:
            continue
        rel_type_str = rel_path_str
        if 'Type' in rel_type_str:
            type_str = 'Type-' + rel_type_str[rel_type_str.find('Type') + 5]
        elif any(disc_cd in rel_type_str for disc_cd in meta_parser.get_other_disc_type()):
            type_str = next(disc_cd for disc_cd in meta_parser.get_other_disc_type() if disc_cd in rel_type_str)
        else:
            continue
        if type_str not in table:
            continue
        for file in files:
            fn = meta_parser.normalize(file)
            is_off_vocal = any(word in file.lower() for word in ['off vocal', 'off cocal', 'off-vocal', 'instrument', 'music'])
            if not any(fn.endswith(suffix) for suffix in ['.wav', '.mp3', '.flac', '.ape', '.m4a']):
                continue
            for ((keyname, keyoff), song) in table[type_str].items():
                if fn.find(keyname) >= 0 and keyoff == is_off_vocal:
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
    print('Enter Type-C')
    print('Loading wikipedia...')
    meta = load_wikipedia(wiki_path)
    print('Deal with all files...')
    deal_with_all_files(root_path)
    print('Writing cue...')
    write_cue(root_path=root_path, meta=meta)

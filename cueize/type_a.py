# songs in the same directory
from song import Song
import meta_parser
import re

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
        title = re.sub('\s*[\-(（]?off vocal ver(\.)?[\-)）]?\s*$', '', title)
    song = Song(track_id, title, performer, is_off_vocal, length)
    song.thetype = thetype
    pair = (meta_parser.normalize(title), is_off_vocal)
    if pair not in table:
        table[pair] = song

# def load_web(url):
#     import html2text
#     import urllib.request
#     html = urllib.request.urlopen(url).read().decode("utf-8")
#     h2t = html2text.HTML2Text()
#     h2t.ignore_links = True
#     raw = h2t.handle(html)
#     # raw = html2text.html2text(html)
#     # response = requests.get(video_data['youtube_url'],proxies = proxy,verify=False)
#     # raw = html_to_text(html)
#     raw = raw.encode('GBK', 'ignore').decode('GBK');
#     with open('raw.txt', 'w') as f:
#         f.write(raw)

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
            if line.startswith('シングル収録トラック') or line.startswith('収録トラック'):
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
                elif line.endswith('アルバム'):
                    meta['performer'] = meta_parser.parse_performer(line, 'スタジオ・アルバム')
            elif mode == 'track_mode':
                if line.startswith('通常盤 Type'): # NMB-17th
                    thetype = line[4:]
                elif line.startswith('Type') or line in meta_parser.get_other_disc_type():
                    thetype = line
                elif line.startswith('DISC'):
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
        rel_path_str = root[(len(root_path) + 1):]
        for file in files:
            fn = meta_parser.normalize(file)
            is_off_vocal = any(word in file.lower() for word in ['off vocal', 'off-vocal', 'instrument', 'music', 'instrumental'])
            if not any(fn.endswith(suffix) for suffix in ['.wav', '.mp3', '.flac', '.ape', '.m4a']):
                continue
            for ((keyname, keyoff), song) in table.items():
                if fn.find(keyname) >= 0 and keyoff == is_off_vocal:
                    if not song.pure_filename or len(song.pure_filename) > len(file):
                        song.set_file(rel_path_str, file)

def write_cue(root_path, meta):
    import os
    prefix = meta_parser.get_prefix(meta)
    with open(root_path + '/Sets.cue', 'w', encoding='utf-8-sig') as f:
        f.writelines("%s\n" % l for l in prefix)
        for song in meta_parser.assign_new_track_id(table.values()):
            f.writelines("%s\n" % l for l in song.to_cue_item())

def run(wiki_path, root_path):
    print('Enter Type-A')
    print('Loading wikipedia...')
    meta = load_wikipedia(wiki_path)
    print('Deal with all files...')
    deal_with_all_files(root_path)
    print('Writing cue...')
    write_cue(root_path=root_path, meta=meta)

from bs4 import BeautifulSoup, NavigableString, Tag
from song import Song

import urllib.request
import meta_parser
import sys
import re

import type_a

groups = ['AKB48', 'SKE48', 'NMB48', 'HKT48', 'NGT48',
          '%e4%b9%83%e6%9c%a8%e5%9d%82%34%36',# 乃木坂46
          '%e6%ac%85%e5%9d%82%34%36', # 欅坂46
          'STU48']
wiki_base = 'https://ja.wikipedia.org'
menu_base = wiki_base + '/wiki/Template:'
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

table={}

class Single:
    def __init__(self, track_id, title, link):
        self.track_id = track_id
        self.title = title
        self.link = link

        self.group = None
        self.publish_date = None

def cout(content):
    print(str(content).encode('GBK', 'ignore').decode('GBK'))

def go_on_with_table(table):
    li_all = table.find_all('li')
    single_table = {}
    for li_elem in li_all:
        if len(li_elem.contents) == 2:
            track_str = li_elem.contents[0].strip()
            if track_str.endswith('.'):
                track_str = track_str[:-1]
            track_id = int(track_str) if track_str.isdigit() else -1
            node = li_elem.contents[1]
        elif len(li_elem.contents) == 1:
            track_id = -1
            node = li_elem.contents[0]
        else:
            continue
        if isinstance(node, NavigableString) or not 'title' in node.attrs or not 'href' in node.attrs:
            continue
        title = str(node.string)
        link = node['href']
        single_table[title] = Single(track_id, title, link)
    return single_table

def crawl_page(single):
    url = wiki_base + single.link
    print("crawling page: " + url)
    page = urllib.request.urlopen(url).read().decode('utf-8')
    pp = BeautifulSoup(page, 'html.parser')

    info_table = pp.find('table', {'class':'infobox'})
    if not info_table:
        return False
    single.publish_date = meta_parser.parse_date(info_table.find('time', {'itemprop':'datePublished'}).text)

    h3 = pp.find('span', class_='mw-headline', text='シングル収録トラック').parent
    thetype = None
    mode = 'track_mode'
    while mode == 'track_mode':
        h3 = h3.next_sibling
        if isinstance(h3, NavigableString):
            continue
        if h3.name == 'h3':
            type_text = str(h3.span.string)
            if type_text.startswith('Type') or type_text in meta_parser.get_other_disc_type():
                thetype = type_text
        elif h3.name == 'table' and h3.has_attr('class') and (h3['class'] == 'tracklist' or h3['class'] == ['tracklist']): 
            caption = h3.find('caption').text
            if not caption.startswith('CD'):
                continue
            for tr in h3.find_all('tr'):
                tds = tr.find_all('td')
                if len(tds) > 0:
                    track_match = re.compile(r'(?P<track_id>\d+)\.').match(tds[0].text)
                    if not track_match:
                        continue
                    track_id = track_match.group('track_id')
                    performer = tds[1].find('small').text[1:-1] if tds[1].find('small') else ''
                    title_match = re.compile(r'「(?P<title>.*)」').match(tds[1].find(text=True, recursive=False))
                    if not title_match:
                        continue
                    title = title_match.group('title')
                    is_off_vocal = False
                    if title.lower().find("off vocal") >= 0:
                        is_off_vocal = True
                        title = re.sub('\s*[\-(（～]?off vocal ver(\.)?[\-)）～]?\s*$', '', title)
                    # author[2],composer[3],combiner[4]
                    length_match = re.compile(r'(?P<length>\d+:\d+)').match(tds[5].text) if len(tds) > 5 else None
                    length = length_match.group('length') if length_match else '00:00:00'
                    song = Song(track_id, title, performer, is_off_vocal, length)
                    song.thetype = thetype
                    pair = (meta_parser.normalize(title), is_off_vocal)
                    if pair not in table:
                        table[pair] = song
        elif h3.name == 'h2' and (h3.text.startswith('選抜メンバー')):
            mode = 'unit_mode'
    return True

def load_from_wiki_template(album_title):
    for group in groups:
        url = menu_base + group
        print("crawling page: " + url)
        raw = urllib.request.urlopen(url).read().decode('utf-8')
        rp = BeautifulSoup(raw, 'html.parser')

        group_name = rp.find_all(class_='firstHeading')[0].string
        if group_name.startswith('Template:'):
            group_name = group_name[(group_name.find(':') + 1):]
        else:
            group_name = group
        # 48 style
        tables = rp.find_all(class_='nowraplinks hlist hlist-pipe collapsible collapsed navbox-subgroup')
        for table in tables:
            if table.span.string == 'CD作品' or table.span.string == '作品':
                single_table = go_on_with_table(table)
                if album_title in single_table:
                    group_name = rp.find_all(class_='navbox-title')[0].span.string
                    single_table[album_title].group = group_name
                    if crawl_page(single_table[album_title]):
                        return single_table[album_title]
                break

        # 46 style
        tables = rp.find_all(class_='nowraplinks hlist navbox-subgroup')
        for table in tables:
            if table.td.string == 'シングル' or table.td.string == 'アルバム':
                single_table = go_on_with_table(table)
                if album_title in single_table:
                    single_table[album_title].group = group_name
                    if crawl_page(single_table[album_title]):
                        return single_table[album_title]
                break

    return None

if __name__ == '__main__':
    title = sys.argv[1]
    path = sys.argv[2] if len(sys.argv) > 2 else '.'
    print('Loading wikipedia...')
    album = load_from_wiki_template(title)
    type_a.table = table
    print('Deal with all files in ({0})...'.format(path))
    type_a.deal_with_all_files(path)
    print('Writing cue...')
    type_a.write_cue(root_path=path, meta={'title':title, 'date':album.publish_date, 'performer':album.group, 'single_id':album.track_id})

# print soup.prettify()
# cout(raw)
import os

def header():
    return '''
[General]
MacroID=1d12f1dc-dfa1-4d11-9ca6-ebd2e385eaf8
SyntaxVersion=2
BeginHotkey=121
BeginHotkeyMod=4
PauseHotkey=122
PauseHotkeyMod=4
StopHotkey=123
StopHotkeyMod=4
RunOnce=1
EnableWindow=
Description=SGS_GDWithRSA
Enable=1
AutoRun=0
[Repeat]
Type=0
Number=1
[SetupUI]
Type=2
QUI=
[Relative]
SetupOCXFile=
[Comment]
[Script]
'''

def into_server(remeber):
    return '''
MoveTo 951, {0}
Delay 2085
LeftDoubleClick 1
Delay 101
MoveTo 951, 484
Delay 1552
LeftClick 1
Delay 700
'''.format(476 if remeber else 550)

def keep_input_block():
    return '''
LeftClick 1
Delay 219
'''

def a_account(username,backspace,password,ie=True):
    results = []
    shifted = False
    for i in range(0, backspace):
        results.append('KeyDown "Backspace", 1')
        results.append('Delay 16')
    for ch in username.upper():
        if ch == '^':
            shifted = True
            results.append('KeyDown "Shift", 1')
        else:
            results.append('KeyDown "{0}", 1'.format(ch))
            if shifted:
                results.append('Delay 14')
                results.append('KeyUp "Shift", 1')
                shifted = False                
        results.append('Delay 18')
    results.append('KeyDown "Tab", 1')
    results.append('Delay 100')
    results.append('KeyUp "Tab", 1')
    results.append('Delay 217')
    if ie:
        results.append('KeyDown "Tab", 1')
        results.append('Delay 100')
        results.append('KeyUp "Tab", 1')
        results.append('Delay 271')
    for ch in password.upper():
        if ch == '^':
            shifted = True
            results.append('KeyDown "Shift", 1')
        else:
            results.append('KeyDown "{0}", 1'.format(ch))
            if shifted:
                results.append('Delay 14')
                results.append('KeyUp "Shift", 1')
                shifted = False                
        results.append('Delay 19')
    results.append('KeyDown "Enter", 1')
    results.append('Delay 70')
    results.append('KeyUp "Enter", 1')
    results.append('Delay 800')
    return results

def enter_mode():
    return '''
MoveTo 822, 560
Delay 2064
LeftClick 1
MoveTo 978, 740
Delay 1079
LeftClick 1
'''

def signin():
    return '''
MoveTo 1012, 632
Delay 587
LeftClick 1
Delay 48
'''

def close_upsell():
    return '''
MoveTo 1417, 272
Delay 602
LeftClick 1
Delay 88
'''

def close_pad():
    return '''
MoveTo 1424, 269
Delay 593
LeftClick 1
Delay 88
'''

def a_close_page(time=1):
    results = []
    results.append('MoveTo 1437, 247')
    results.append('Delay 593')
    for i in range(0, time):
        results.append('LeftClick 1')
        results.append('Delay 88')
    return results

def commu(will_close_last_week=False):
    close_last_week=''
    if will_close_last_week:
        close_last_week='''
MoveTo 959, 595
Delay 1471
LeftClick 1
LeftClick 1
'''
    return '''
MoveTo 1216, 817
Delay 1155
LeftClick 1%s
MoveTo 870, 772
Delay 491
LeftClick 1
MoveTo 730, 753
Delay 710
LeftClick 1
Delay 509
LeftClick 1
Delay 508
LeftClick 1
''' % close_last_week

def open_pad():
    return '''
MoveTo 505, 400
Delay 943
LeftClick 1
'''

# 543, 317
def click_commu_task(pad_index):
    return '''
MoveTo 540, {0}
Delay 804
LeftClick 1
MoveTo 749, 744
Delay 711
LeftClick 1
'''.format(317 + pad_index * 50)

def click_item(pad_index, menu_index, block_count=0):
    return '''
MoveTo 536, {0}
Delay 991
LeftClick 1
MoveTo 673, {1}
Delay 640
LeftClick 1
MoveTo 1096, 766
Delay 698
LeftClick 1
'''.format(317 + pad_index * 50, 444 + menu_index * 31 + block_count * 36)

def accept_and_click_item(pad_index, menu_index, block_count, times):
    part1 = '''
MoveTo 536, {0}
Delay 991
LeftClick 1
MoveTo 673, {1}
Delay 640
LeftClick 1
'''.format(317 + pad_index * 50, 444 + menu_index * 31 + block_count * 36)
    part2 = '''
MoveTo 1096, 766
Delay 698
LeftClick 1
MoveTo 1111, 769
Delay 798
LeftClick 1
MoveTo 994, 600
Delay 398
LeftClick 1
Delay 598
LeftClick 1
''' # maybe 1083, 387' double click to fuck the award
    for i in range(0, times):
        part1 = part1 + part2
    return part1

def message():
    return '''
MoveTo 1370, 820
Delay 501
LeftClick 1
MoveTo 877, 385
Delay 1340
LeftClick 1
MoveTo 1011, 710
Delay 598
LeftClick 1
'''

def select_item(index, total):
    if total % 2 == 1:
        offset = int(-75 * (int(total / 2) - index))
    else:
        offset = int(-75 * (total / 2 - 0.5 - index))
    return '''
MoveTo {0}, 486
Delay 405
LeftClick 1
MoveTo 954, 558
Dealy 504
LeftClick 1
'''.format(958 + offset)

def run_fuck1(f, username, backspace, password, auto_signin=True):
    login_pos = 3
    item_pos = 4
    f.write(into_server(remeber=True))
    if backspace > 0:
        f.write(keep_input_block())
    f.writelines("%s\n" % l for l in a_account(username, backspace, password))
    f.write(enter_mode())
    f.write(close_upsell())
    if auto_signin:
        f.write(signin())
    f.write(close_pad())
    f.write(commu(False))
    # f.write(message())
    f.write(open_pad())
    # f.write(click_item(item_pos, 2))
    f.write(click_commu_task(item_pos + 2))
    # f.write(click_item(login_pos, 1, block_count=1))
    # f.write(click_item(item_pos, 1, block_count=2))
    f.write(click_item(login_pos, 0, block_count=1))
    # f.write(click_item(login_pos, 1, block_count=1))
    # f.write(accept_and_click_item(item_pos - 1, 8, block_count=2, times=7))
    # f.write(click_item(5, 0))
    # f.write(click_item(5, 0))
    # f.write(click_item(item_pos, 1, block_count=1))
    # f.write(click_item(4, 9))
    # f.write(click_item(4, 8))
    # f.write(select_item(0, 3))
    f.write(close_pad())
    f.writelines("%s\n" % l for l in a_close_page(4))

def run_monday_fuck1(f, username, backspace, password, keep=True):
    f.write(into_server(remeber=True))
    if keep:
        f.write(keep_input_block())
    f.writelines("%s\n" % l for l in a_account(username, backspace, password))
    f.write(enter_mode())
    f.write(close_pad())
    f.write(commu())
    f.write(open_pad())
    f.write(click_commu_task(5))
    f.write(click_item(3, 1))
    f.write(close_pad())
    f.write(open_pad())
    f.write(click_item(3, 0))
    f.write(click_item(3, 11))
    f.write(close_pad())
    f.writelines("%s\n" % l for l in a_close_page(4))

'''
call this funciton in mysgslogin.py
'''
def write_down(list, run_type):
    with open('sgsrsa.Q', 'w', encoding='utf-8-sig') as f:
        f.write(header())
        for item in list:
            if len(item) > 4:
                run_type(f, username=item[0], backspace=item[1], password=item[2], auto_signin=item[3], keep=item[3])
            elif len(item) > 3:
                run_type(f, username=item[0], backspace=item[1], password=item[2], auto_signin=item[3])
            else:
                run_type(f, username=item[0], backspace=item[1], password=item[2])

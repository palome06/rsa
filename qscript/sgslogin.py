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
Delay 1485
LeftDoubleClick 1
Delay 101
MoveTo 951, 484
Delay 1852
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
    results.append('Delay 900')
    return results

def enter_mode():
    return '''
MoveTo 822, 560
Delay 3164
LeftClick 1
MoveTo 978, 740
Delay 1079
LeftClick 1
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

def commu():
    return '''
MoveTo 1216, 817
Delay 655
LeftClick 1
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
'''

def open_pad():
    return '''
MoveTo 504, 475
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

def click_item(pad_index, menu_index):
    return '''
MoveTo 536, {0}
Delay 691
LeftClick 1
MoveTo 673, {1}
Delay 640
LeftClick 1
MoveTo 1096, 766
Delay 698
LeftClick 1
'''.format(317 + pad_index * 50, 444 + menu_index * 31)

def message():
    return '''
MoveTo 1370, 820
Delay 701
LeftClick 1
MoveTo 877, 385
Delay 640
LeftClick 1
MoveTo 1080, 710
Delay 698
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

def run_fuck1(f, username, backspace, password, keep=True):
    f.write(into_server(remeber=False))
    if keep:
        f.write(keep_input_block())
    f.writelines("%s\n" % l for l in a_account(username, backspace, password))
    f.write(enter_mode())
    f.write(close_pad())
    #f.write(message())
    f.write(commu())
    f.write(open_pad())
    f.write(click_commu_task(6))
    # f.write(click_item(4, 0))
    # f.write(click_item(4, 1))
    f.write(click_item(4, 0))
    f.write(click_item(4, 9))
    f.write(click_item(4, 8))
    f.write(select_item(0, 3))
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
            if len(item) > 3:
                run_type(f, username=item[0], backspace=item[1], password=item[2], keep=item[3])
            else:
                run_type(f, username=item[0], backspace=item[1], password=item[2])

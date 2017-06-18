import urllib.request
import time

zsf = 'http://web.sanguosha.com/220_9/assets/winnerGeneral/full/%s.png'
tsf = 'http://test.sanguosha.com/assets/winnerGeneral/full/%s.png'

for i in range(162, 400):
    for j in range(0, 15):
        sn = "%d%02d" % (i, j)
        print("crawling sn = %s" % sn)
        try:
            urllib.request.urlretrieve(zsf % sn, '%s.png' % sn)
        except:
            print('fail')
        time.sleep(0.1)
    time.sleep(1)
# http://web.sanguosha.com/220_9/assets/winnerGeneral/full/2112.png
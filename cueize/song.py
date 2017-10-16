class Song:
    def __init__(self, track_id, title, performer, is_off_vocal, length):
        self.track_id = int(track_id)
        self.title = title
        self.performer = performer
        self.is_off_vocal = is_off_vocal
        self.file = None
        self.pure_filename = None
        self.thetype = None
        self.voice_type = None
        self.index = None
        self.disc_no = None
        self.set_length(length)

    def cout(self):
        print(self.thetype, '-', self.track_id, '# ', self.title, 'off vocal ver.' if self.is_off_vocal else '',\
            ' //', self.performer, ' (', self.length, ') @ ', self.file)

    def set_file(self, root, filename):
        self.pure_filename = filename
        self.file = filename if root == '' else (root + '\\' + filename)
        if self.file.endswith('.flac') or self.file.endswith('.FLAC'):
            self.voice_type = 'FLAC'
        else:
            self.voice_type = 'WAVE'

    def set_length(self, length):
        if length:
            splits = length.split(':')
            minute = int(splits[0])
            second = int(splits[1])
            self.length = '00:%02d:%02d' % (minute, second)
        else:
            self.length = '00:00:00'

    def to_cue_item(self, with_length=False):
        line1 = 'FILE "%s" %s' % (self.file, self.voice_type)
        line2 = '  TRACK %02d AUDIO' % self.index
        line3 = '    TITLE "%s%s"' % (self.title, ' off vocal ver.' if self.is_off_vocal else '')
        line5 = '    INDEX 01 %s' % self.length if with_length else '    INDEX 01 00:00:00'
        if (self.performer is None or self.performer == ''):
            return [line1, line2, line3, line5]
        else:
            line4 = '    PERFORMER "%s"' % self.performer
            return [line1, line2, line3, line4, line5]

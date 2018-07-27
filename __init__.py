import os
import json
import shutil
import string
import unicodedata as ud
from cudatext import *
from cudax_lib import html_color_to_int

ini = os.path.join(app_path(APP_DIR_SETTINGS), 'cuda_color_text.ini')
ini0 = os.path.join(os.path.dirname(__file__), 'styles.sample.ini')

all_unicode = [chr(i) for i in range(0x10000)]
unicode_letters = ''.join([c for c in all_unicode if ud.category(c) in ('Lu', 'Ll')])

CHARS = string.ascii_letters + string.digits + '_' + unicode_letters
HELPER_EXT = '.cuda-colortext'

if os.path.isfile(ini0) and not os.path.isfile(ini):
    shutil.copyfile(ini0, ini)

#-------options
opt_all_words    = ini_read(ini, 'op', 'all_words'      , '0') == '1'
opt_whole_words  = ini_read(ini, 'op', 'whole_words'    , '0') == '1'
opt_case_sens    = ini_read(ini, 'op', 'case_sensitive' , '0') == '1'
#-----constants
TAG_UNIQ   = 4000 # must be unique for all ed.attr() plugins
TAG_MAX    = TAG_UNIQ + 10
#--------------

def is_word(s):

    if not s: return False
    for ch in s:
        if not ch in CHARS: return False
    return True

def get_word(ed, x, y):

    s = ed.get_text_line(y)
    if not s: return
    if x>=len(s): return

    x0 = x
    while (x0>0) and is_word(s[x0-1]):
        x0 -= 1

    x1 = x
    while (x1<len(s)) and is_word(s[x1]):
        x1 += 1

    return s[x0:x1]

def _curent_word(ed):

    if ed.get_sel_mode() != SEL_NORMAL: return
    s = ed.get_text_sel()
    if s: return s

    carets = ed.get_carets()
    if len(carets)!=1: return
    x0, y0, x1, y1 = carets[0]
    return get_word(ed, x0, y0)


def do_find_all(ed, text):

    res = []
    for i in range(ed.get_line_count()):
        line = ed.get_text_line(i)
        if not line: continue

        if not opt_case_sens:
            line = line.upper()
            text = text.upper()

        n = 0
        while True:
            n = line.find(text, n)
            if n<0: break
            allow = True
            if opt_whole_words:
                if n>0 and is_word(line[n-1]):
                    allow = False
                if allow:
                    n2 = n+len(text)
                    if n2<len(line) and is_word(line[n2]):
                        allow = False
            if allow:
                res += [(i, n)]
            n += len(text)
    return res


def set_sel_attribute(ed, item, nlen, attribs):

    tag, color, bold, italic, strikeout, border, color_border = attribs

    b_l = b_r = b_d = b_u = 0
    if border:
        b_l = b_r = b_d = b_u = 1

    if bold or italic or strikeout or border:
        fcolor = COLOR_NONE
    else:
        fcolor = ed.get_prop(PROP_COLOR, COLOR_ID_TextFont)

    ed.attr(MARKERS_ADD, tag, item[1], item[0], nlen, fcolor, color, color_border, bold, italic, strikeout, b_l, b_r, b_d, b_u)


def set_text_attribute(ed, attribs):

    ed.set_prop(PROP_MODIFIED, True)
    # need on_save call to save helper file

    word = _curent_word(ed)
    if not word:
        word = ed.get_text_sel()
    if not word: return

    if opt_all_words:
        items = do_find_all(ed, word)
        for item in items:
            set_sel_attribute(ed, item, len(word), attribs)
    else:
        carets = ed.get_carets()
        if len(carets)!=1: return
        x0, y0, x1, y1 = carets[0]
        #sort pairs
        if (y0, x0)>(y1, x1):
            x0, y0, x1, y1 = x1, y1, x0, y0
        set_sel_attribute(ed, [y0, x0], len(word), attribs)

# attribs array:
#[tag=n, color=COLOR_NONE, bold=0, italic=0, strikeout=0, border=0, color_border=COLOR_NONE]


def do_color(ed, n):

    ed.attr(MARKERS_DELETE_BY_TAG, TAG_UNIQ + n)

    color        = COLOR_NONE
    color_border = COLOR_NONE
    bold         = 0
    italic       = 0
    strikeout    = 0
    border       = 0

    st = ini_read(ini, 'colors', str(n), '')
    if st:
        color = html_color_to_int(st)

    st = ini_read(ini, 'border_colors', str(n), '')
    if st:
        color_border = html_color_to_int(st)

    st = ini_read(ini, 'styles', str(n), '')
    if st:
        if 'b' in st: bold      = 1 #attribs.extend([(ATTRIB_SET_BOLD,0)])
        if 'i' in st: italic    = 1 #attribs.extend([(ATTRIB_SET_ITALIC,0)])
        if 'u' in st: border    = 1 #attribs.extend([(ATTRIB_SET_UNDERLINE,0)])
        if 's' in st: strikeout = 1 #attribs.extend([(ATTRIB_SET_STRIKEOUT,0)])

    set_text_attribute(ed, [TAG_UNIQ + n, color, bold, italic, strikeout, border, color_border])


def clear_style(ed, n):

    ed.set_prop(PROP_MODIFIED, True) # need on_save call
    ed.attr(MARKERS_DELETE_BY_TAG, TAG_UNIQ + n)


def load_helper_file(ed):

    fn = ed.get_filename()
    if not fn: return

    fn_res = fn + HELPER_EXT
    if not os.path.isfile(fn_res):
        return

    with open(fn_res, 'r') as f:
        res = json.load(f)

    for r in res:
        ed.attr(MARKERS_ADD,
            tag = r['tag'],
            x = r['x'],
            y = r['y'],
            len = r['len'],
            color_font = r['c_font'],
            color_bg = r['c_bg'],
            color_border = r['c_border'],
            font_bold = 1 if r['f_b'] else 0,
            font_italic = 1 if r['f_i'] else 0,
            font_strikeout = 1 if r['f_s'] else 0,
            )

    print('Color Text: restored %d attribs for "%s"' % (len(res), os.path.basename(fn)))


def save_helper_file(ed):

    fn = ed.get_filename()
    if not fn: return

    fn_res = fn + HELPER_EXT
    if os.path.isfile(fn_res):
        os.remove(fn_res)

    marks = ed.attr(MARKERS_GET)
    if not marks:
        return

    res = []
    for (tag, x, y, len,
      color_font, color_bg, color_border,
      font_bold, font_italic, font_strikeout,
      border_left, border_right, border_down, border_up) in marks:
        if TAG_UNIQ<=tag<=TAG_MAX:
            res.append({
                'tag': tag,
                'x': x,
                'y': y,
                'len': len,
                'c_font': color_font,
                'c_bg': color_bg,
                'c_border': color_border,
                'f_b': font_bold!=0,
                'f_i': font_italic!=0,
                'f_s': font_strikeout!=0,
                })

    if not res:
        return

    with open(fn_res, 'w') as f:
        json.dump(res, fp=f, indent=2)


class Command:

    def color1(self): do_color(ed, 1)
    def color2(self): do_color(ed, 2)
    def color3(self): do_color(ed, 3)
    def color4(self): do_color(ed, 4)
    def color5(self): do_color(ed, 5)
    def color6(self): do_color(ed, 6)

    def format_bold(self):
        set_text_attribute(ed, [TAG_UNIQ, COLOR_NONE, 1, 0, 0, 0, COLOR_NONE])

    def format_italic(self):
        set_text_attribute(ed, [TAG_UNIQ, COLOR_NONE, 0, 1, 0, 0, COLOR_NONE])

    def format_strikeout(self):
        set_text_attribute(ed, [TAG_UNIQ, COLOR_NONE, 0, 0, 1, 0, COLOR_NONE])

    def clear_all(self):
        clear_style(ed, 0)
        clear_style(ed, 1)
        clear_style(ed, 2)
        clear_style(ed, 3)
        clear_style(ed, 4)
        clear_style(ed, 5)
        clear_style(ed, 6)

    def clear1(self): clear_style(ed, 1)
    def clear2(self): clear_style(ed, 2)
    def clear3(self): clear_style(ed, 3)
    def clear4(self): clear_style(ed, 4)
    def clear5(self): clear_style(ed, 5)
    def clear6(self): clear_style(ed, 6)

    def config(self):
        file_open(ini)

    def on_open(self, ed_self):
        load_helper_file(ed_self)

    def on_save(self, ed_self):
        save_helper_file(ed_self)

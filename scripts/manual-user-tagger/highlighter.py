import sys, tty, termios


class Colors:
    HEADER = '\033[95m'

    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'

    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class TagController:
    UP = '\x1b[A'
    DOWN = '\x1b[B'
    RIGHT = '\x1b[C'
    LEFT = '\x1b[D'

    @staticmethod
    def get_key():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            key = sys.stdin.read(3)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return key


def get_highlight_text(text, words=None, color=None):
    new_text = ''
    if color is None:
        color = Colors.YELLOW

    space = ''
    for text_word in text.split(' '):
        if words is None or text_word in words.keys():
            if words is None:
                color = Colors.YELLOW
            else:
                color = words[text_word]
            new_text += f'{space}{color}{Colors.BOLD}{text_word}{Colors.END}'
        else:
            new_text += f'{space}{text_word}'
        if not space:
            space = ' '
    return new_text


def highlight(text, words=None, color=None):
    print(get_highlight_text(text, words, color))


################################################################################
if len(sys.argv) < 2:
    print('Usage: python3 highlighter.py input_file.csv line_number')
    raise SystemExit

if len(sys.argv) < 3:
    start_line = 0
else:
    start_line = int(sys.argv[2])

import pandas as pd
sample = pd.read_csv(sys.argv[1])
################################################################################

line_counter = 0

for index, row in sample.iterrows():
    if line_counter < start_line:
        line_counter += 1
        continue
    line_counter += 1

    user = row['user']
    timestamp = row['timestamp']

    text = (row['title'] + '.' + row['body']).lower()\
        .replace('.', ' . ')\
        .replace(',', ' . ')\
        .replace(':', ' . ')\
        .replace(';', ' . ')\
        .strip()

    print(f'Text #{line_counter}\n')
    highlight(user, color=Colors.BLUE)
    print('\n')
    highlight(
        text, {
            'cut': Colors.RED,
            'cuts': Colors.RED,
            'cutting': Colors.RED,
            'die': Colors.RED,
            'blood': Colors.RED,
            'bloody': Colors.RED,
            'blades': Colors.RED,
            'yeeted': Colors.RED,
            'yeet': Colors.RED,
            'yeets': Colors.RED,
            'yeeting': Colors.RED,
            'anorexia': Colors.RED,
            'disorder': Colors.RED,
            'weight': Colors.RED,
            'sickness': Colors.RED,
            'psychological': Colors.RED,
            'vomiting': Colors.RED,
            'skinny': Colors.RED,
            'starvation': Colors.RED,
            'hunger': Colors.RED,
            'vomit': Colors.RED,
            'yot': Colors.RED,
            'razor': Colors.RED,
            'scars': Colors.RED,
            'scar': Colors.RED,
            'suicide': Colors.RED,
            'suicidal': Colors.RED,
            'harm': Colors.RED,
            'depressing': Colors.GREEN,
            'depression': Colors.GREEN,
            'depressed': Colors.GREEN,
        })
    print('\n')
    print(
        f'{Colors.BOLD}{Colors.GREEN}POSITIVE <{Colors.END}     {Colors.BOLD}{Colors.RED}> NEGATIVE{Colors.END}'
    )

    pressed_key = TagController.get_key()
    if pressed_key == TagController.LEFT:
        with open(f'positive', 'a') as output_file:
            output_file.write(f'{user}\n')
    elif pressed_key == TagController.RIGHT:
        with open(f'negative', 'a') as output_file:
            output_file.write(f'{user}\n')
    elif pressed_key == TagController.UP:
        raise SystemExit

    print(chr(27) + "[2J")

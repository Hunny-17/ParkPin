"""Compare actual UI Automator bounds before/after opening the software keyboard.

Usage: python artifacts/g1/check-keyboard.py normal.xml keyboard.xml
The navigation bar must not grow by an entire keyboard inset.
"""
import re
import sys
import xml.etree.ElementTree as ET

def height(path, view_id):
    root = ET.parse(path).getroot()
    node = next(n for n in root.iter('node')
                if n.get('resource-id', '').endswith('/' + view_id))
    _, top, _, bottom = map(int, re.findall(r'\d+', node.get('bounds')))
    return bottom - top

normal = height(sys.argv[1], 'bottom_nav')
keyboard = height(sys.argv[2], 'bottom_nav')
print(f'Bottom Navigation: normal={normal}px, keyboard={keyboard}px')
assert keyboard <= normal + normal // 4, 'FAIL: Bottom Navigation grows when keyboard opens'
print('PASS: Keyboard does not inflate Bottom Navigation')

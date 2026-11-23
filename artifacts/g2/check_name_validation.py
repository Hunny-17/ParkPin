"""Regression assertion on a real UI Automator capture after correcting a name."""
import sys
import xml.etree.ElementTree as ET

tree = ET.parse(sys.argv[1]).getroot()
name = next(n for n in tree.iter('node') if n.get('resource-id','').endswith('/input_place_name'))
assert name.get('text','').strip(), 'Capture must contain a corrected, nonblank place name'
errors = [n for n in tree.iter('node') if n.get('text') == 'Vui lòng nhập tên bãi đỗ']
print('Corrected nonblank name; stale required-name messages:', len(errors))
assert not errors, 'FAIL: required-name error remains after a valid name is entered'
print('PASS: required-name error clears when corrected')

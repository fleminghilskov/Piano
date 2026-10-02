from pathlib import Path
import ast
import hashlib
import json
import re
import sys

work = Path(__file__).resolve().parent
target = Path(r'E:\Dropbox\lyricsappl\html\windows\ego-klaver\My Way.html')
if '--install' in sys.argv:
    original = (work / 'original.html').read_bytes()
    assert target.read_bytes() == original, 'HTML-filen er ændret siden klargøringen.'
    target.write_bytes((work / 'preview.html').read_bytes())
    print('HTML-filen er opdateret.')
else:
    tree = ast.parse((work.parent / 'My Way.py').read_text(encoding='utf-8'))
    song = next(ast.literal_eval(node.value) for node in tree.body
                if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'SONG' for t in node.targets))
    source = target.read_bytes()
    assert b'my-way-piano:start' not in source
    (work / 'original.html').write_bytes(source)
    widget = (work / 'piano.html').read_text(encoding='utf-8').replace('__SONG_JSON__', json.dumps(song, ensure_ascii=True))
    markup, script = widget.split('<script>', 1)
    markup = markup.encode('ascii', errors='xmlcharrefreplace')
    script = ('<script>' + script).encode('cp1252')
    body = re.search(br'<body\b[^>]*>', source, flags=re.I)
    assert body
    result = source[:body.end()] + markup + source[body.end():]
    result = result.replace(b'</body>', script + b'</body>')
    assert result.replace(markup, b'', 1).replace(script, b'', 1) == source
    assert sum(len(chords) for _, chords in song) == 97
    (work / 'preview.html').write_bytes(result)
    print('Klargjort: 97 akkorder. Original HTML og tegnkodning er bevaret byte for byte.')

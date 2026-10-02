from pathlib import Path
import json
import re
import sys

work = Path(__file__).resolve().parent
target = Path(r'E:\Dropbox\lyricsappl\html\windows\ego-klaver\My Way.html')
if '--install' in sys.argv:
    assert target.read_bytes() == (work / 'embedded.html').read_bytes(), 'HTML er ændret.'
    for name in ('My Way.piano.js', 'My Way.piano.css'):
        assert not (target.parent / name).exists(), f'{name} findes allerede.'
    for name in ('My Way.piano.js', 'My Way.piano.css'):
        (target.parent / name).write_bytes((work / name).read_bytes())
    target.write_bytes((work / 'external.html').read_bytes())
    print('HTML henviser nu til separate JavaScript- og CSS-filer.')
else:
    original = target.read_bytes()
    text = original.decode('cp1252')
    start = text.index('<!-- my-way-piano:start -->')
    end = text.index('</section>', start) + len('</section>')
    markup = text[start:end]
    css = re.search(r'<style>(.*?)</style>', markup, re.S).group(1).strip()
    section = markup[markup.index('<section'):]
    script_start = text.index('<script>\n(() =>', end)
    script_end = text.index('<!-- my-way-piano:end -->', script_start) + len('<!-- my-way-piano:end -->')
    script = re.search(r'<script>(.*?)</script>', text[script_start:script_end], re.S).group(1).strip()
    script = script.replace("  'use strict';", "  'use strict';\n  document.body.insertAdjacentHTML('afterbegin', " + json.dumps(section) + ");", 1)
    result = text[:script_start] + '<script src="My%20Way.piano.js" charset="utf-8"></script>' + text[script_end:]
    result = result[:start] + result[end:]
    result = result.replace('</head>', '<link rel="stylesheet" href="My%20Way.piano.css">\n</head>', 1)
    assert 'const song =' not in result
    assert '<section id="my-way-piano"' not in result
    assert '#my-way-piano' not in result
    assert result.count('My%20Way.piano.js') == 1
    assert result.count('My%20Way.piano.css') == 1
    (work / 'embedded.html').write_bytes(original)
    (work / 'external.html').write_bytes(result.encode('cp1252'))
    (work / 'My Way.piano.js').write_text(script + '\n', encoding='utf-8')
    (work / 'My Way.piano.css').write_text(css + '\n', encoding='utf-8')
    print('Klargjort og kontrolleret: HTML indeholder kun to filhenvisninger.')


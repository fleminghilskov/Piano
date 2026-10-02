import importlib.util
import re
from pathlib import Path
from zipfile import ZipFile

HERE = Path(__file__).resolve().parent

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

old = load('old', r'E:\Dropbox\Python-Source\Lyrics\docx2html.py')
new = load('new', HERE / 'docx2html.py')
source = Path(r'E:\Dropbox\Tekster\Word\Ego-Klaver\Have You Ever Seen The Rain.docx')
old.convert_docx(source, HERE / 'before.html')
new.convert_docx(source, HERE / 'Have You Ever Seen The Rain.html')
before = (HERE / 'before.html').read_text(encoding='utf-8')
after = (HERE / 'Have You Ever Seen The Rain.html').read_text(encoding='utf-8')
assert re.sub(r' data-afsnit="[^"]*"', '', after) == before
sections = list(dict.fromkeys(re.findall(r'data-afsnit="([^"]*)"', after)))
assert sections == ['Intro', 'Vers 1', 'Vers 2', 'Chorus 1', 'Vers 3', 'Vers 4', 'Chorus 2', 'Chorus 3'], sections

ns = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
with ZipFile(HERE / 'fixture.docx', 'w') as z:
    z.writestr('word/styles.xml', f'<w:styles xmlns:w="{ns}"/>')
    z.writestr('word/document.xml', f'''<w:document xmlns:w="{ns}"><w:body>
      <w:p><w:r><w:t>Before</w:t></w:r><w:bookmarkStart w:name="Intro" w:id="0"/>
      <w:bookmarkEnd w:id="0"/><w:r><w:t>Intro text</w:t></w:r></w:p>
      <w:p><w:bookmarkStart w:name="_GoBack" w:id="1"/><w:r><w:t>Still intro</w:t></w:r>
      <w:bookmarkStart w:name="Akkord_Vers_1" w:id="2"/><w:r><w:t>Verse text</w:t></w:r></w:p>
      <w:p><w:r><w:t>Still verse</w:t></w:r></w:p>
    </w:body></w:document>''')
new.convert_docx(HERE / 'fixture.docx', HERE / 'fixture.html')
html = (HERE / 'fixture.html').read_text(encoding='utf-8')
assert '<span style="">Before</span>' in html
assert '<span data-afsnit="Intro" style="">Intro text</span>' in html
assert '<span data-afsnit="Intro" style="">Still intro</span>' in html
assert '<span data-afsnit="Vers 1" style="">Verse text</span>' in html
assert '<p data-afsnit="Vers 1" style=""><span data-afsnit="Vers 1" style="">Still verse</span></p>' in html
assert html.count('<p data-afsnit=') == 1
print('PASS: all 8 real sections; unchanged text/formatting; mid-paragraph boundaries; continuation; unrelated bookmarks.')

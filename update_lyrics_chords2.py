"""
  Indbyg klikbar klaviaturvisning i sangens HTML fra de aktuelle Exceldata.
  Det vil sige Sangens docx-dokument skal være konverteret vha. docx2html.py
  Akkorderne læses fra fanen klar via AddChords2.py.

  Kør igen efter en ny Word-eksport eller ændringer i Excel.
  Eksempel: python update_lyrics_chords2.py "My Way"
  Hele mappen: python update_lyrics_chords2.py "E:\\Dropbox\\lyricsappl\\html\\windows\\ego-klaver"
"""

import argparse
import json
import re
import runpy
import tempfile
from html import escape
from html.parser import HTMLParser
from pathlib import Path

# title = "My Way"
# title = "Alone Again Naturally"
# title = "Cant Help Falling In Love"
# title = "I Dont Want To Talk About It"
# title = "Have You Ever Seen The Rain"
# title = "My Way"
# title = "Cant Help Falling In Love"
# title = "Comfortably Numb"
# title = "House Of The Rising Sun"
# title = "Hotel California"
# title = "Hurt"
# title = "Im Not In Love"
# title = "Imagine"
# title = "Knockin On Heavens Door"
# title = "Let It Be"
# title = "Mad World - Gary Jules"
# title = "Perfect"
# title = "Take Me Home Country Roads"
# title = "Tennessee Whiskey"
# title = "The Boxer"
# title = "What a Wonderful World"
# title = "Yesterday"
# title = "Hallelujah Nate Version"
# title = "Sound of Silence"
# title = "Langebro"
# title = "Suzanne"

title = "So Long Marianne"



ROOT = Path(__file__).resolve().parent
HTML_FOLDER = Path(r"E:\Dropbox\lyricsappl\html\windows\ego-klaver")
title = globals().get('title', '')
DEFAULT_HTML = HTML_FOLDER / f'{title}.html' if title else None
# IDE: valgt sang, eller hele mappen når ingen title-linje er aktiv.
# Brug SOURCE = HTML_FOLDER for altid at behandle hele mappen.
SOURCE = DEFAULT_HTML if DEFAULT_HTML is not None else HTML_FOLDER
START = '<!-- BEGIN PIANO CHORD VIEWER -->'
END = '<!-- END PIANO CHORD VIEWER -->'


class ChordFields(HTMLParser):
    """Find knapper og tomme parenteser uden at omskrive sangens øvrige HTML."""
    def __init__(self, document):
        super().__init__(convert_charrefs=True)
        self.document = document
        self.lines = [0]
        for match in re.finditer('\n', document):
            self.lines.append(match.end())
        self.stack = []
        self.nodes = []
        self.feed(document)

    def source_offset(self):
        line, column = self.getpos()
        return self.lines[line - 1] + column

    def handle_starttag(self, tag, attrs):
        if tag in ('area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
                   'link', 'meta', 'param', 'source', 'track', 'wbr'):
            return
        attrs = dict(attrs)
        parent = self.stack[-1] if self.stack else {}
        if self.stack:
            parent['leaf'] = False
        self.stack.append(dict(tag=tag, attrs=attrs, start=self.source_offset(), text='', leaf=True,
                               section=attrs.get('data-afsnit', parent.get('section')),
                               bar=attrs.get('data-takt', parent.get('bar'))))

    def handle_startendtag(self, tag, attrs):
        pass

    def handle_data(self, text):
        for node in self.stack:
            if node['tag'] in ('span', 'button'):
                node['text'] += text

    def handle_endtag(self, tag):
        if not self.stack or self.stack[-1]['tag'] != tag:
            return
        node = self.stack.pop()
        node['end'] = self.document.index('>', self.source_offset()) + 1
        in_button = any(n['tag'] == 'button' for n in self.stack)
        if (tag == 'button' and 'data-akkord' in node['attrs'] or
                tag == 'span' and node['leaf'] and not in_button):
            self.nodes.append(node)

    def fields(self):
        nodes = sorted(self.nodes, key=lambda n: n['start'])
        result = []
        i = 0
        while i < len(nodes):
            node = nodes[i]
            text = node['text'].strip()
            if text == '(' and i + 1 < len(nodes):
                following = nodes[i + 1]
                if (following['text'].strip() == ')' and
                        (node['section'], node['bar']) == (following['section'], following['bar']) and
                        not self.document[node['end']:following['start']].strip()):
                    node = dict(node, end=following['end'], text='()')
                    text = '()'
                    i += 1
            if node['tag'] == 'button' or re.fullmatch(r'\(\s*\)', text):
                result.append(node)
            i += 1
        return result


def section_key(name):
    name = re.sub(r'(?<=[A-Za-z])(?=\d)', ' ', (name or '').replace('_', ' '))
    return ' '.join(name.casefold().split())


UI = r'''
<style>
button[data-akkord] { cursor:pointer; border-radius:4px; outline-offset:2px; }
button[data-akkord]:hover { background:#eee3fa; }
button[data-akkord]:focus-visible { outline:2px solid #7030a0; }
button[data-akkord][aria-pressed="true"] { background:#ead9ff; box-shadow:0 0 0 2px #7030a0; }
#piano-panel { position:fixed; top:50%; left:50%; transform:translate(-50%,-50%); width:min(1400px,calc(100vw - 32px)); max-height:calc(100vh - 32px); overflow:auto; box-sizing:border-box; padding:20px 24px; border:1px solid #666; border-radius:10px; background:#181818; color:white; box-shadow:0 4px 24px #0006; z-index:10000; font:16px Arial,sans-serif; }
#piano-panel[hidden] { display:none; }
#piano-panel header { display:flex; align-items:center; justify-content:space-between; gap:12px; margin-bottom:12px; }
#piano-title { margin:0; font-size:24px; }
#piano-close { background:#333; color:white; border:1px solid #999; border-radius:4px; padding:5px 12px; cursor:pointer; font:inherit; }
#piano-keys svg { display:block; width:100%; height:auto; }
@media print { #piano-panel { display:none; } body { padding-bottom:0 !important; } button[data-akkord] { box-shadow:none !important; background:none !important; } }
</style>
<aside id="piano-panel" aria-label="Valgt pianoakkord" hidden>
  <header><h2 id="piano-title" aria-live="polite"></h2><button id="piano-close" type="button" aria-label="Luk akkordvisning">Luk ×</button></header>
  <div id="piano-keys"></div>
</aside>
<script id="piano-data" type="application/json">__CHORD_DATA__</script>
<script>
(() => {
  const data = JSON.parse(document.getElementById('piano-data').textContent);
  const panel = document.getElementById('piano-panel');
  const title = document.getElementById('piano-title');
  const keyboard = document.getElementById('piano-keys');
  const buttons = document.querySelectorAll('button[data-akkord]');
  let selected = null;
  function close() {
    panel.hidden = true;
    if (selected) {
      selected.setAttribute('aria-pressed', 'false');
      selected.focus({preventScroll:true});
      selected = null;
    }
  }
  buttons.forEach(button => {
    const section = button.dataset.afsnit;
    const chord = data[section][Number(button.dataset.akkord)];
    const label = button.textContent.trim().replace(/^\(|\)$/g, '');
    button.setAttribute('aria-controls', 'piano-panel');
    button.setAttribute('aria-pressed', 'false');
    button.setAttribute('aria-label', 'Vis ' + label + ' · ' + section);
    button.title = 'Vis pianoakkord: ' + label;
    button.addEventListener('click', () => {
      if (selected) selected.setAttribute('aria-pressed', 'false');
      selected = button;
      selected.setAttribute('aria-pressed', 'true');
      title.textContent = label + ' · ' + section;
      keyboard.innerHTML = chord.svg;
      panel.hidden = false;
    });
  });
  document.getElementById('piano-close').addEventListener('click', close);
  // Handle button keys before the existing lyrics script's Enter autoscroll.
  window.addEventListener('keydown', event => {
    if (event.key === 'Escape' && !panel.hidden) {
      event.preventDefault(); event.stopImmediatePropagation(); close();
    } else if (event.target.closest('button[data-akkord], #piano-close') &&
               (event.key === 'Enter' || event.key === ' ')) {
      event.preventDefault(); event.stopImmediatePropagation();
      if (!event.repeat) event.target.closest('button').click();
    }
  }, true);
})();
</script>
'''


def fill_fields(document, sections):
    """Match afsnit/takt og derefter akkordens rækkefølge inden for takten."""
    fields = ChordFields(document).fields()
    if not fields:
        raise ValueError('HTML-filen mangler tomme akkordfelter () eller akkordknapper.')
    # Word-eksporten kan udelade data-takt på første takt. Udfyld kun
    # et indledende hul, når næste felt udtrykkeligt begynder takt 2.
    section_fields = {}
    for field in fields:
        section_fields.setdefault(section_key(field['section']), []).append(field)
    for group in section_fields.values():
        first_numbered = next((i for i, f in enumerate(group) if f['bar'] is not None), None)
        if (first_numbered and group[first_numbered]['bar'] == '2'
                and not any(f['bar'] == '1' for f in group)):
            for field in group[:first_numbered]:
                field['bar'] = '1'
    lookup = {}
    for section, chords in sections.items():
        key = section_key(section)
        if key in lookup:
            raise ValueError(f'Tvetydigt afsnitsnavn i Excel: {section!r}.')
        lookup[key] = {}
        for index, chord in enumerate(chords):
            bar = str(chord['bar'])
            entries = lookup[key].setdefault(bar, [])
            if any(c['slot'] == chord['slot'] for _, c in entries):
                raise ValueError(f'{section}, takt {bar}: Gentaget akkordplads i Excel.')
            entries.append((index, chord))
    used = {}
    data = {}
    edits = []
    for field in fields:
        section, bar = field['section'], field['bar']
        key = section_key(section)
        if key not in lookup and key + ' 1' in lookup:
            numbered = [k for k in lookup if re.fullmatch(re.escape(key) + r' \d+', k)]
            if numbered == [key + ' 1']:
                key += ' 1'
        entries = lookup.get(key, {}).get(bar, [])
        position = used.get((key, bar), 0)
        if position >= len(entries):
            raise ValueError(f'{section}, takt {bar}: HTML har flere akkordfelter end Excel ({len(entries)} akkorder); felt {position + 1} kan ikke udfyldes.')
        index, chord = entries[position]
        label = field['text'].strip().removeprefix('(').removesuffix(')').strip()
        if label and field['attrs'].get('data-klar') != 'true' and label.rstrip('*') != chord['name'].rstrip('*'):
            raise ValueError(f'{section}, takt {bar}: HTML viser {label!r}, Excel viser {chord["name"]!r}.')
        used[key, bar] = position + 1
        # JSON bruger HTML-afsnittets navn, ligesom browserens dataset-opslag.
        if section not in data:
            original = next(s for s in sections if section_key(s) == key)
            data[section] = sections[original]
        style = field['attrs'].get('style', '')
        if field['tag'] == 'button':
            style = style or 'color:#7030A0;font-weight:bold'
        else:
            style += ';color:#7030A0;font-weight:bold'
        button = (f'<button type="button" data-klar="true" data-afsnit="{escape(section, quote=True)}" '
                  f'data-takt="{escape(bar, quote=True)}" data-akkord="{index}" '
                  f'style="{escape(style, quote=True)}">({escape(chord["name"])})</button>')
        edits.append((field['start'], field['end'], button))
    for key, bars in lookup.items():
        for bar, entries in bars.items():
            count = used.get((key, bar), 0)
            if count != len(entries):
                raise ValueError(f'{key}, takt {bar}: HTML har {count} akkordfelter, Excel har {len(entries)}. Tilføj de manglende () i sangen.')
    for start, end, button in reversed(edits):
        document = document[:start] + button + document[end:]
    return document, data, len(fields)


def update(source, destination):
    source, destination = Path(source), Path(destination)
    module = runpy.run_path(str(ROOT / 'AddChords2.py'), init_globals={'title': source.stem})
    with tempfile.TemporaryDirectory() as folder:
        rendered = module['export_html'](Path(folder) / 'chords.html').read_text(encoding='utf-8')
    svgs = iter(re.findall(r'<svg\b.*?</svg>', rendered, re.S))
    sections = {section: [dict(name=c.name, left=c.left, right=c.right,
                              bar=c.bar, slot=c.slot, svg=next(svgs))
                          for c in chords] for section, chords in module['SONG']}
    document = source.read_text(encoding='utf-8')
    document = re.sub(re.escape(START) + r'.*?' + re.escape(END) + r'\n?', '', document, flags=re.S)
    document, data, count = fill_fields(document, sections)
    encoded = json.dumps(data, ensure_ascii=False).replace('<', '\\u003c')
    bundle = START + UI.replace('__CHORD_DATA__', encoded) + END
    if '</body>' not in document:
        raise ValueError('HTML-filen mangler </body>.')
    destination.write_text(document.replace('</body>', bundle + '\n</body>', 1), encoding='utf-8')
    print(f'Opdateret {count} akkordfelter fra fanen klar: {destination}')



def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', nargs='?', default=str(SOURCE),
                        help='Sangtitel, HTML-fil eller mappe (standard: %(default)s).')
    outputs = parser.add_mutually_exclusive_group()
    outputs.add_argument('--output', type=Path, help='Outputfil ved én sang.')
    outputs.add_argument('--output-dir', type=Path, help='Gem HTML-filer i en anden mappe.')
    args = parser.parse_args(argv)
    source = Path(args.source)
    if not source.exists() and source.parent == Path('.'):
        source = HTML_FOLDER / (source.name if source.suffix.lower() in ('.html', '.htm')
                                else source.name + '.html')
    batch = source.is_dir()
    if batch:
        if args.output:
            parser.error('Brug --output-dir ved mappekørsel; --output gælder kun én sang.')
        files = sorted((p for p in source.iterdir()
                        if p.is_file() and p.suffix.lower() in ('.html', '.htm')
                        and not p.stem.casefold().endswith(' - akkorder')),
                       key=lambda p: p.name.casefold())
        if not files:
            parser.exit(1, f'Fejl: Ingen sang-HTML-filer fundet i {source}.\n')
    else:
        if not source.is_file() or source.suffix.lower() not in ('.html', '.htm'):
            parser.exit(1, f'Fejl: Angiv en eksisterende HTML-fil eller mappe: {source}\n')
        files = [source]
    try:
        if args.output_dir:
            args.output_dir.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        parser.exit(1, f'Fejl: {error}\n')
    succeeded = failed = 0
    for path in files:
        destination = args.output_dir / path.name if args.output_dir else (args.output or path)
        try:
            update(path, destination)
        except Exception as error:
            failed += 1
            print(f'Fejl i {path.name}: {error}')
        else:
            succeeded += 1
    if batch:
        print(f'Færdig: {succeeded} opdateret, {failed} fejl.')
    return 1 if failed else 0


if __name__ == '__main__':
    raise SystemExit(main())

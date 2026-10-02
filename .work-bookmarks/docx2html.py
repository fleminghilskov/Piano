"""
Export formatted lyrics from DOCX using only the Python standard library.

Preserves paragraph and text formatting; does not reproduce floating objects,
tables, headers, footers or Word pagination.
Usage: python docx2html.py [source_folder_or_docx] [destination_folder_or_html]
"""
import argparse
import os
import re
from html import escape
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
# SOURCE = Path(r'E:\Dropbox\Tekster\Word\Ego')
SOURCE = Path(r'E:\Dropbox\Tekster\Word\Ego-Klaver')
# OUTPUT = Path(r'E:\Dropbox\lyricsappl\html\windows-Python\ego')
OUTPUT = Path(r'E:\Dropbox\lyricsappl\html\windows\ego-klaver')

SCRIPTS = Path(r'E:\Dropbox\lyricsappl\scripts\Windows')


def val(node, key='val', default=None):
    return node.get(W + key, default) if node is not None else default


def props(node):
    return {c.tag.removeprefix(W): dict(c.attrib) for c in node} if node is not None else {}


def merge(*layers):
    result = {}
    for layer in layers:
        for key, attrs in layer.items():
            result.setdefault(key, {}).update(attrs)
    return result


def css(p):
    result = {}
    def get(key, name='val', default=None):
        return p.get(key, {}).get(W + name, default)
    font = get('rFonts', 'ascii') or get('rFonts', 'hAnsi')
    if font:
        result['font-family'] = '"' + font.replace('"', '').replace('\\', '') + '"'
    if get('sz'):
        result['font-size'] = f"{int(get('sz')) / 2:g}pt"
    for key, name, on, off in [('b', 'font-weight', 'bold', 'normal'),
                              ('i', 'font-style', 'italic', 'normal')]:
        if key in p:
            result[name] = off if get(key) in ('0', 'false', 'off') else on
    if get('color'):
        result['color'] = '#' + get('color') if get('color') != 'auto' else '#000000'
    if 'u' in p:
        result['text-decoration'] = 'none' if get('u') == 'none' else 'underline'
    if get('jc'):
        result['text-align'] = {'both': 'justify'}.get(get('jc'), get('jc'))
    for word, name in [('before', 'margin-top'), ('after', 'margin-bottom')]:
        if get('spacing', word) is not None:
            result[name] = f"{int(get('spacing', word)) / 20:g}pt"
    if get('spacing', 'line'):
        line = int(get('spacing', 'line'))
        result['line-height'] = (f'{line / 240:g}' if get('spacing', 'lineRule', 'auto') == 'auto'
                                 else f'{line / 20:g}pt')
    return result


def attribute(style):
    return escape(';'.join(f'{k}:{v}' for k, v in style.items()), quote=True)


def bookmark_section(name):
    """Song bookmarks mark section starts, lasting until the next song bookmark.

    Accept Intro, Vers1, Vers_1, Chorus1, Mellemspil, etc. Akkord_ also allows custom
    section names. Ignore unrelated bookmarks, including Word's own names.
    """
    if name.startswith('Akkord_'):
        name = name[len('Akkord_'):]
    elif not re.fullmatch(r'(?:Intro|Vers|Verse|Chorus|Bridge|Mellemspil|Outro|Outtro)(?:_?\d+)?', name, re.I):
        return None
    name = name.replace('_', ' ')
    name = re.sub(r'(?<=[A-Za-z])(?=\d)', ' ', name).strip()
    return name or None


def chord_spans(spans, counters):
    """Wrap parenthesized chords, including chords split across Word runs."""
    text = ''.join(part[0] for part in spans)
    chord_pattern = r'\([A-H](?:[#b♯♭])?(?:(?:maj|min|dim|aug|sus|add|m)|[0-9+#b♯♭°ø*-])*(?:/[A-H][#b♯♭]?)?\*?\)'
    ranges = []
    offset = 0
    for content, attrs, section in spans:
        ranges.append((offset, offset + len(content), content, attrs, section))
        offset += len(content)

    def render(start, end):
        return ''.join(f'<span{attrs}>{content[max(start - left, 0):end - left]}</span>'
                       for left, right, content, attrs, section in ranges
                       if left < end and right > start)

    result = []
    position = 0
    for match in re.finditer(chord_pattern, text):
        sections = {section for left, right, _, _, section in ranges
                    if left < match.end() and right > match.start()}
        if len(sections) != 1 or None in sections:
            continue
        section = sections.pop()
        number = counters.get(section, 0)
        counters[section] = number + 1
        result.append(render(position, match.start()))
        result.append(f'<button type="button" data-afsnit="{escape(section, quote=True)}"'
                      f' data-akkord="{number}">{render(match.start(), match.end())}</button>')
        position = match.end()
    result.append(render(position, len(text)))
    return ''.join(result)


def convert_docx(source, destination):
    with ZipFile(source) as archive:
        document = ET.fromstring(archive.read('word/document.xml'))
        root = ET.fromstring(archive.read('word/styles.xml'))
    styles = {val(s, 'styleId'): s for s in root.findall(W + 'style')}
    normal = next((val(s, 'styleId') for s in styles.values()
                   if val(s, 'type') == 'paragraph' and val(s, 'default') == '1'), 'Normal')
    defaults = root.find(W + 'docDefaults')
    dr = props(defaults.find(f'{W}rPrDefault/{W}rPr')) if defaults is not None else {}
    dp = props(defaults.find(f'{W}pPrDefault/{W}pPr')) if defaults is not None else {}

    def inherited(sid, tag, seen=None):
        seen = set() if seen is None else seen
        if sid not in styles or sid in seen:
            return {}
        seen.add(sid)
        s = styles[sid]
        return merge(inherited(val(s.find(W + 'basedOn')), tag, seen), props(s.find(W + tag)))

    body = document.find(W + 'body')
    drawings = body.findall('.//' + W + 'drawing')
    nonempty_drawings = any(
        any((t.text or '').strip() for t in drawing.iter(W + 't'))
        or drawing.find('.//{http://schemas.openxmlformats.org/drawingml/2006/main}blip') is not None
        for drawing in drawings)
    if body.find(W + 'tbl') is not None or nonempty_drawings:
        raise ValueError('This text converter does not support tables or drawings.')
    paragraphs = []
    chord_counters = {}
    current_section = None
    for p in body.findall(W + 'p'):
        pp = p.find(W + 'pPr')
        sid = val(pp.find(W + 'pStyle'), default=normal) if pp is not None else normal
        rp = merge(dr, inherited(sid, 'rPr'))
        mark = merge(rp, props(pp.find(W + 'rPr')) if pp is not None else {})
        style = css(mark)
        style.update(css(merge(dp, inherited(sid, 'pPr'), props(pp))))
        spans = []
        span_sections = []
        # Walk in document order so a bookmark inside a paragraph only applies
        # to the text after it. Bookmark ends deliberately do not reset state.
        for run in p.iter():
            if run.tag == W + 'bookmarkStart':
                section_name = bookmark_section(val(run, 'name', ''))
                if section_name is not None:
                    current_section = section_name
                continue
            if run.tag != W + 'r':
                continue
            rpr = run.find(W + 'rPr')
            rsid = val(rpr.find(W + 'rStyle')) if rpr is not None else None
            formatting = css(merge(rp, inherited(rsid, 'rPr'), props(rpr)))
            text = ''.join(escape(c.text or '') if c.tag == W + 't' else
                           '<br>' if c.tag in (W + 'br', W + 'cr') else
                           '&#9;' if c.tag == W + 'tab' else '' for c in run)
            if text:
                section_attr = (f' data-afsnit="{escape(current_section, quote=True)}"'
                                if current_section is not None else '')
                spans.append((text, f'{section_attr} style="{attribute(formatting)}"', current_section))
                span_sections.append(current_section)
        # A paragraph gets a section only if all its text belongs to it.
        # Mixed paragraphs carry the precise sections on their spans instead.
        paragraph_section = span_sections[0] if span_sections else current_section
        section_attr = (f' data-afsnit="{escape(paragraph_section, quote=True)}"'
                        if paragraph_section is not None
                        and all(s == paragraph_section for s in span_sections) else '')
        content = chord_spans(spans, chord_counters)
        paragraphs.append(f'<p{section_attr} style="{attribute(style)}">{content or "<br>"}</p>')
    sections = body.findall('.//' + W + 'sectPr')
    page = {}
    if sections:
        section = sections[-1]
        page['width'] = f"{int(val(section.find(W + 'pgSz'), 'w', '11906')) / 20:g}pt"
        for side in ('top', 'right', 'bottom', 'left'):
            page['padding-' + side] = f"{int(val(section.find(W + 'pgMar'), side, '0')) / 20:g}pt"
    script_dir = Path(os.path.relpath(SCRIPTS, destination.resolve().parent)).as_posix()
    html = ('<!doctype html>\n<html lang="da"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<title>{escape(source.stem)}</title><style>'
            'body{margin:0;background:white;color:black}'
            'main{box-sizing:border-box;margin:0 auto}'
            'p{margin:0;white-space:pre-wrap}'
            'button[data-akkord]{font:inherit;color:inherit;background:none;border:0;padding:0;white-space:pre-wrap}'
            '</style></head><body>'
            f'<main style="{attribute(page)}">\n' + '\n'.join(paragraphs)
            + '\n</main>\n'
            f'<script src="{escape(script_dir, quote=True)}/jquery-1.11.1.min.js"></script>\n'
            f'<script type="text/javascript" src="{escape(script_dir, quote=True)}/lyrics_scripts.js"></script>\n'
            '</body></html>\n')
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(html, encoding='utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path, nargs='?', default=SOURCE)
    parser.add_argument('destination', type=Path, nargs='?', default=OUTPUT)
    args = parser.parse_args()
    if args.source.is_dir():
        files = sorted(p for p in args.source.rglob('*')
                       if p.is_file() and p.suffix.lower() == '.docx'
                       and not p.name.startswith('~$'))
        converted = 0
        failed = 0
        for source in files:
            destination = args.destination / source.relative_to(args.source).with_suffix('.html')
            try:
                convert_docx(source, destination)
            except Exception as error:
                failed += 1
                print(f'FEJL: {source}: {error}')
            else:
                converted += 1
                print(f'HTML gemt i: {destination}')
        print(f'Færdig: {converted} konverteret, {failed} fejl, {len(files)} DOCX-filer fundet.')
        if failed:
            raise SystemExit(1)
    else:
        destination = args.destination
        if destination.suffix.lower() != '.html':
            destination = destination / args.source.with_suffix('.html').name
        convert_docx(args.source, destination)
        print(f'HTML gemt i: {destination}')

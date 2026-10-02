"""Læs Afsnit/Akkord/VH/RH fra kolonne A/C/D/E i første ark i en xlsx-fil."""

import posixpath
import re
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile


def load_song(path):
    """Bevar rækkefølge og gentagelser; tomt afsnit viderefører det forrige.

    Tom VH eller RH betyder ingen toner i den hånd. Helt tomme rækker springes
    over. NC (No Chord) har ingen toner og tillader begge hænder tomme.
    NA er et gyldigt akkordnavn, også uden toner i hænderne.
    UNK i VH eller RH betyder ukendte toner for den hånd.
    A er afsnit, C er akkord, D er VH og E er RH. B (taktnummer) ignoreres.
    Arket skal indeholde tekstværdier, ikke formler, i de fire brugte kolonner.
    """
    path = Path(path)
    ns = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    rel_ns = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'
    with ZipFile(path) as archive:
        workbook = ET.fromstring(archive.read('xl/workbook.xml'))
        sheet = workbook.find('s:sheets/s:sheet', ns)
        if sheet is None:
            raise ValueError(f'{path.name}: Excel-filen har ingen ark.')
        relationships = ET.fromstring(archive.read('xl/_rels/workbook.xml.rels'))
        target = next(r.get('Target') for r in relationships
                      if r.get('Id') == sheet.get(rel_ns + 'id'))
        sheet_path = (target.lstrip('/') if target.startswith('/') else
                      posixpath.normpath(posixpath.join('xl', target)))
        shared = []
        if 'xl/sharedStrings.xml' in archive.namelist():
            shared = [''.join(t.text or '' for t in item.findall('.//s:t', ns))
                      for item in ET.fromstring(archive.read('xl/sharedStrings.xml'))]
        rows = ET.fromstring(archive.read(sheet_path)).findall('s:sheetData/s:row', ns)

    song = []
    section = None
    header_seen = False
    for row in rows:
        values = {}
        location = f'{path.name}, {sheet.get("name")}, række {row.get("r")}'
        for cell in row.findall('s:c', ns):
            column = re.sub(r'\d', '', cell.get('r', ''))
            if column not in ('A', 'C', 'D', 'E'):
                continue
            if cell.find('s:f', ns) is not None:
                raise ValueError(f'{location}: Brug tekst i {cell.get("r")}, ikke en formel.')
            value = cell.findtext('s:v', '', ns)
            if cell.get('t') == 's':
                value = shared[int(value)]
            elif cell.get('t') == 'inlineStr':
                value = ''.join(t.text or '' for t in cell.findall('.//s:t', ns))
            elif cell.get('t') == 'e':
                raise ValueError(f'{location}: Excel-fejl i {cell.get("r")}: {value}')
            values[column] = value.strip()
        fields = [values.get(c, '') for c in ('A', 'C', 'D', 'E')]
        if not any(fields):
            continue
        if not header_seen:
            if [v.casefold() for v in fields] != ['afsnit', 'akkord', 'vh', 'rh']:
                raise ValueError(f'{location}: Forventede Afsnit i A, Akkord i C, VH i D og RH i E. B (taktnummer) ignoreres.')
            header_seen = True
            continue
        name, chord, left, right = fields
        if name:
            section = re.sub(r'(?<=[A-Za-z])(?=\d)', ' ', name.replace('_', ' '))
        no_chord = chord.upper() == 'NC'
        allows_empty_hands = chord.upper() in ('NC', 'NA')
        if not chord or not section or (not allows_empty_hands and not (left or right)):
            raise ValueError(f'{location}: Angiv afsnit, akkord og toner i mindst én hånd (eller NC/NA uden toner).')
        if no_chord:
            if left or right:
                raise ValueError(f'{location}: NC betyder No Chord. Lad VH og RH være tomme.')
            chord = 'NC'
        hands = []
        for hand, notes in [('VH', left), ('RH', right)]:
            if notes.upper() == 'UNK':
                hands.append('UNK')
                continue
            tones = [n.strip() for n in notes.split('-')] if notes else []
            if any(not re.fullmatch(r'(?:[A-G]|[CDFGA]#|[DEGAB]b)[1-5]', n) for n in tones):
                raise ValueError(f'{location}: Ugyldige toner i {hand}: {notes!r}. Brug C1–B5 adskilt med bindestreg eller UNK for ukendte toner.')
            hands.append('-'.join(tones))
        if not song or song[-1][0] != section:
            if any(previous == section for previous, _ in song):
                raise ValueError(f'{location}: Afsnittet {section!r} gentages efter et andet afsnit. Brug et unikt navn.')
            song.append((section, []))
        song[-1][1].append((chord, *hands))
    if not song:
        raise ValueError(f'{path.name}: Ingen akkorder fundet.')
    return song

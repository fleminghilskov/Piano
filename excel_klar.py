"""Læs fanen Klar: én takt pr. række og op til fire akkorder med egne hænder."""

import posixpath
import re
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile


@dataclass(frozen=True)
class Chord:
    name: str
    left: str
    right: str
    bar: str
    slot: int

    @property
    def label(self):
        return f'Takt {self.bar} · {self.name}'


def load_song(path, *, text_column=False):
    """Læs .xlsx/.xlsm uden at ændre filen eller udføre makroer.

    A/B: afsnit/takt, C–F: Akkord1–4, G–N: VH1/RH1 ... VH4/RH4.
    Tomt afsnit viderefører det forrige. Tomme akkordfelter springes over.
    Tomme hænder er tilladt og giver ingen markerede tangenter.
    Med text_column=True forventes Tekst i C; akkorder og hænder findes
    ud fra overskrifterne i D–O. Tekst bruges ikke i akkordvisningen.
    """
    path = Path(path)
    ns = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    with ZipFile(path) as archive:
        workbook = ET.fromstring(archive.read('xl/workbook.xml'))
        sheet = next((s for s in workbook.findall('s:sheets/s:sheet', ns)
                      if s.get('name', '').casefold() == 'klar'), None)
        if sheet is None:
            raise ValueError(f'{path.name}: Fanen "klar" mangler.')
        relationships = ET.fromstring(archive.read('xl/_rels/workbook.xml.rels'))
        sheet_id = sheet.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
        target = next(r.get('Target') for r in relationships if r.get('Id') == sheet_id)
        sheet_path = (target.lstrip('/') if target.startswith('/') else
                      posixpath.normpath(posixpath.join('xl', target)))
        shared = []
        if 'xl/sharedStrings.xml' in archive.namelist():
            shared = [''.join(t.text or '' for t in item.findall('.//s:t', ns))
                      for item in ET.fromstring(archive.read('xl/sharedStrings.xml'))]
        rows = ET.fromstring(archive.read(sheet_path)).findall('s:sheetData/s:row', ns)

    columns = 'ABCDEFGHIJKLMNO' if text_column else 'ABCDEFGHIJKLMN'
    headers = ['afsnit', 'takt', 'akkord1', 'akkord2', 'akkord3', 'akkord4',
               'vh1', 'rh1', 'vh2', 'rh2', 'vh3', 'rh3', 'vh4', 'rh4']
    song = []
    section = None
    header_seen = False
    field_columns = columns
    for row in rows:
        location = f'{path.name}, {sheet.get("name")}, række {row.get("r")}'
        values = {}
        for cell in row.findall('s:c', ns):
            column = re.sub(r'\d', '', cell.get('r', ''))
            if column not in columns or len(column) != 1:
                continue
            if cell.find('s:f', ns) is not None:
                raise ValueError(f'{location}: Brug værdier i {cell.get("r")}, ikke en formel.')
            value = cell.findtext('s:v', '', ns)
            if cell.get('t') == 's':
                value = shared[int(value)]
            elif cell.get('t') == 'inlineStr':
                value = ''.join(t.text or '' for t in cell.findall('.//s:t', ns))
            elif cell.get('t') == 'e':
                raise ValueError(f'{location}: Excel-fejl i {cell.get("r")}: {value}')
            values[column] = value.strip()
        fields = [values.get(c, '') for c in columns]
        if not any(fields):
            continue
        if not header_seen:
            actual_headers = [v.casefold() for v in fields]
            if text_column:
                expected = headers[:2] + ['tekst'] + headers[2:]
                if (actual_headers[:3] != expected[:3]
                        or sorted(actual_headers[3:]) != sorted(expected[3:])):
                    raise ValueError(f'{location}: Forventede Afsnit, Takt, Tekst i A–C '
                                     'og Akkord1–4 samt VH1–4/RH1–4 i D–O.')
                field_columns = [columns[actual_headers.index(header)] for header in headers]
            elif actual_headers != headers:
                raise ValueError(f'{location}: Forventede kolonner: {", ".join(headers)}.')
            header_seen = True
            continue
        fields = [values.get(c, '') for c in field_columns]
        name, bar = fields[:2]
        if name:
            section = re.sub(r'(?<=[A-Za-z])(?=\d)', ' ', name.replace('_', ' '))
        if not section or not bar or not any(fields[2:6]):
            raise ValueError(f'{location}: Angiv afsnit, takt og mindst én akkord.')
        chords = []
        for slot in range(4):
            chord = fields[2 + slot]
            left, right = fields[6 + 2 * slot:8 + 2 * slot]
            if not chord:
                if left or right:
                    raise ValueError(f'{location}: VH/RH{slot + 1} har toner, men Akkord{slot + 1} er tom.')
                continue
            if chord.upper() == 'NC':
                if left or right:
                    raise ValueError(f'{location}: NC betyder No Chord. Lad VH/RH{slot + 1} være tomme.')
                chord = 'NC'
            hands = []
            for hand, notes in [('VH', left), ('RH', right)]:
                if notes.upper() == 'UNK':
                    hands.append('UNK')
                    continue
                tones = [n.strip() for n in notes.split('-')] if notes else []
                if any(not re.fullmatch(r'(?:[A-G]|[CDFGA]#|[DEGAB]b)[1-5]', n) for n in tones):
                    raise ValueError(f'{location}: Ugyldige toner i {hand}{slot + 1}: {notes!r}. Brug C1–B5 adskilt med bindestreg eller UNK.')
                hands.append('-'.join(tones))
            chords.append(Chord(chord, *hands, bar, slot + 1))
        if not song or song[-1][0] != section:
            if any(previous == section for previous, _ in song):
                raise ValueError(f'{location}: Afsnittet {section!r} gentages efter et andet afsnit. Brug et unikt navn.')
            song.append((section, []))
        song[-1][1].extend(chords)
    if not song:
        raise ValueError(f'{path.name}: Ingen akkorder fundet i fanen klar.')
    return song

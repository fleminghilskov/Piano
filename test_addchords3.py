"""Kontrollér kolonnemapping for både det gamle og det nye Klar-format."""
import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

from excel_klar import load_song


class ColumnMappingTests(unittest.TestCase):
    def test_all_four_chords_keep_their_hands_in_each_layout(self):
        old = ['Afsnit', 'Takt', 'Akkord1', 'Akkord2', 'Akkord3', 'Akkord4',
               'VH1', 'RH1', 'VH2', 'RH2', 'VH3', 'RH3', 'VH4', 'RH4']
        layouts = [(False, old), (True, old[:2] + ['Tekst'] + old[2:]),
                   (True, old[:2] + ['Tekst'] + old[2:6]
                    + ['VH1', 'VH2', 'VH3', 'VH4', 'RH1', 'RH2', 'RH3', 'RH4'])]
        values = dict(Afsnit='vers1', Takt='7', Tekst='Sangtekst, ikke en akkord',
                      Akkord1='C', Akkord2='D', Akkord3='E', Akkord4='F',
                      VH1='C2', VH2='D2', VH3='E2', VH4='F2',
                      RH1='C4', RH2='D4', RH3='E4', RH4='F4')
        for text_column, headers in layouts:
            with self.subTest(headers=headers), tempfile.TemporaryDirectory() as folder:
                path = Path(folder) / 'song.xlsx'
                ns = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
                sheet = ET.Element('worksheet', xmlns=ns)
                data = ET.SubElement(sheet, 'sheetData')
                for number, items in enumerate([headers, [values[h] for h in headers]], 1):
                    row = ET.SubElement(data, 'row', r=str(number))
                    for index, value in enumerate(items):
                        cell = ET.SubElement(row, 'c', r=f'{chr(65 + index)}{number}', t='inlineStr')
                        ET.SubElement(ET.SubElement(cell, 'is'), 't').text = value
                with ZipFile(path, 'w') as archive:
                    archive.writestr('xl/workbook.xml', f'<workbook xmlns="{ns}" '
                                     'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
                                     '<sheets><sheet name="klar" sheetId="1" r:id="rId1"/></sheets></workbook>')
                    archive.writestr('xl/_rels/workbook.xml.rels',
                                     '<Relationships><Relationship Id="rId1" Target="worksheets/sheet1.xml"/></Relationships>')
                    archive.writestr('xl/worksheets/sheet1.xml', ET.tostring(sheet))
                song = load_song(path, text_column=text_column)
                self.assertEqual(song[0][0], 'vers 1')
                self.assertEqual([(c.name, c.left, c.right, c.bar, c.slot) for c in song[0][1]],
                                 [(note, note + '2', note + '4', '7', slot)
                                  for slot, note in enumerate('CDEF', 1)])


if __name__ == '__main__':
    unittest.main()

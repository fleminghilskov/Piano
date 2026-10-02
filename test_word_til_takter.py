import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

from word_til_takter import WORD_NS, SHEET_NS, extract_bars, read_lines, write_xlsx
from word_til_takter import extract_section_bars, read_section_lines


class WordTilTakterTests(unittest.TestCase):
    def test_empty_bars_and_trailing_barline(self):
        self.assertEqual(extract_bars(["|a| |", "|", "|  |  |", "|b"]),
                         ["a", "", "", "", "", "", "", "b"])

    def test_bird_on_the_wire_first_verse_has_17_bars(self):
        lines = ["|_ _ Li|ke a_a |bird", " |_ on the |wire",
                 "|_ _ like a |drunk in a", "|_ midnight |choir",
                 "|_ I have |tried", "|_ in my |way", "|_ _to be |free | |"]
        rows = extract_section_bars([("vers1", line) for line in lines]
                                    + [("vers2", "|_ _Like a |worm")])
        self.assertEqual([row[1] for row in rows[:17]], list(range(1, 18)))
        self.assertEqual(rows[14:18], [("vers1", 15, "free"),
                                      ("vers1", 16, ""), ("vers1", 17, ""),
                                      ("vers2", 1, "_ _Like a")])

    def test_lyrics_and_headings(self):
        self.assertEqual(extract_bars(["Intro 0 takter:", "3/4 Takt:",
                                      "|_ _ Li|ke a_a |bird", "", "end|___|"]),
                         ["_ _ Li", "ke a_a", "bird", "end", "___", ""])

    def test_word_runs_breaks_tables_and_deleted_text(self):
        xml = f'''<w:document xmlns:w="{WORD_NS}"><w:body>
        <w:p><w:r><w:t>|før</w:t></w:r><w:r><w:t>ste|anden</w:t>
        <w:br/><w:t>|tredje</w:t></w:r><w:del><w:r><w:t>|slettet</w:t></w:r></w:del></w:p>
        <w:tbl><w:tr><w:tc><w:p><w:r><w:t>|fjerde|</w:t></w:r></w:p></w:tc></w:tr></w:tbl>
        </w:body></w:document>'''
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "song.docx"
            with ZipFile(path, "w") as archive:
                archive.writestr("word/document.xml", xml)
            self.assertEqual(extract_bars(read_lines(path)),
                             ["første", "anden", "tredje", "fjerde", ""])

    def test_excel_preserves_empty_rows_and_literal_text(self):
        bars = [("vers1", 1, "æøå & < >"), ("vers1", 2, ""),
                ("chorus1", 1, "=A1"), ("chorus1", 2, "_  __")]
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "song.xlsx"
            write_xlsx(path, bars)
            with ZipFile(path) as archive:
                root = ET.fromstring(archive.read("xl/worksheets/sheet1.xml"))
            ns = {"s": SHEET_NS}
            rows = root.findall("s:sheetData/s:row", ns)[1:]
            self.assertEqual([r.find("s:c/s:v", ns).text for r in rows], ["1", "2", "1", "2"])
            self.assertEqual([r.findall("s:c", ns)[0].findtext("s:is/s:t", "", ns)
                              for r in rows], [bar[0] for bar in bars])
            self.assertEqual([r.findall("s:c", ns)[2].findtext("s:is/s:t", "", ns)
                              for r in rows], [bar[2] for bar in bars])
            self.assertEqual(root.findall(".//s:f", ns), [])
            original = path.read_bytes()
            with self.assertRaises(FileExistsError):
                write_xlsx(path, [("vers1", 1, "ændret")])
            self.assertEqual(path.read_bytes(), original)

    def test_bookmarks_headings_hidden_bookmarks_and_section_numbering(self):
        xml = f'''<w:document xmlns:w="{WORD_NS}"><w:body>
        <w:p><w:r><w:t>|før bogmærke</w:t></w:r></w:p>
        <w:p><w:bookmarkStart w:id="0" w:name="vers1"/>
        <w:bookmarkEnd w:id="0"/><w:r><w:t>Overskrift</w:t></w:r></w:p>
        <w:p><w:r><w:t>|en|</w:t></w:r><w:bookmarkStart w:id="1" w:name="_GoBack"/>
        <w:r><w:t>to</w:t><w:br/><w:t>|tre</w:t></w:r></w:p>
        <w:p><w:bookmarkStart w:id="2" w:name="mellemspil"/>
        <w:r><w:t>| | |</w:t></w:r></w:p>
        <w:tbl><w:tr><w:tc><w:p><w:bookmarkStart w:id="3" w:name="vers2"/>
        <w:r><w:t>|fire</w:t></w:r><w:bookmarkEnd w:id="3"/></w:p></w:tc></w:tr></w:tbl>
        <w:p><w:r><w:t>|fem</w:t></w:r></w:p>
        </w:body></w:document>'''
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "song.docx"
            with ZipFile(path, "w") as archive:
                archive.writestr("word/document.xml", xml)
            self.assertEqual(extract_section_bars(read_section_lines(path)), [
                ("", 1, "før bogmærke"), ("vers1", 1, "en"), ("vers1", 2, "to"),
                ("vers1", 3, "tre"), ("mellemspil", 1, ""), ("mellemspil", 2, ""),
                ("mellemspil", 3, ""),
                ("vers2", 1, "fire"), ("vers2", 2, "fem")])

    def test_without_bookmarks_numbering_is_continuous(self):
        self.assertEqual(extract_section_bars([("", "Titel"), ("", "|en|to"),
                                               ("", "|tre")]),
                         [("", 1, "en"), ("", 2, "to"), ("", 3, "tre")])


if __name__ == "__main__":
    unittest.main()

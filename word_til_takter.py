"""Udtræk | -adskilte takter fra Word til Excel uden ekstra Python-pakker.

Kør fx:
    python word_til_takter.py "E:\\Dropbox\\Tekster\\Word\\Ego-Klaver\\Bird on The Wire.docx"

Uden argumenter bruges SOURCE nedenfor. Excel-filen gemmes som
<sangnavn>_takter.xlsx i den aktuelle mappe. Vælg en anden fil med -o.
Eksisterende filer overskrives kun med --overwrite.

Hver Word-linje behandles særskilt: hver | starter en takt, også sidst på
linjen. Tomme felter mellem og efter streger bevares som tomme takter.
En linje med kun | regnes som én tom takt. Linjer uden | (fx overskrifter)
springes over. Gentagelser kopieres som skrevet, ikke som afspillet.
Navngivne bogmærker starter nye afsnit. Afsnitsnavnet videreføres indtil
næste bogmærke, og taktnummereringen starter ved 1 i hvert afsnit.
Skjulte Word-bogmærker (navne med _) ignoreres. Takter før første bogmærke
får et tomt afsnitsnavn. Kolonnerne er Afsnit, Takt og Tekst.
Programmet læser tekst i dokumentets brødtekst og tabeller, ikke billeder,
sidehoveder eller sidefødder. Word-formatering overføres ikke.
"""

import argparse
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import BadZipFile, ZIP_DEFLATED, ZipFile


SOURCE = Path(r"E:\Dropbox\Tekster\Word\Ego-Klaver\Bird on The Wire.docx")
WORD_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
SHEET_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"


def read_section_lines(path):
    """Læs (afsnitsnavn, linje); bookmarkStart gælder indtil næste start.

    bookmarkEnd afslutter ikke sangafsnittet: et bogmærke kan blot være
    et punkt eller omfatte afsnittets overskrift.
    """
    with ZipFile(path) as archive:
        root = ET.fromstring(archive.read("word/document.xml"))
    body = root.find(f"{{{WORD_NS}}}body")
    if body is None:
        raise ValueError("Word-filen har ingen brødtekst.")

    def paragraph_text(element):
        # Undgå slettet tekst og indlejrede tekstbokse (egne afsnit).
        for child in element:
            tag = child.tag.removeprefix(f"{{{WORD_NS}}}")
            if tag in ("del", "moveFrom", "txbxContent"):
                continue
            if tag == "bookmarkStart":
                name = child.get(f"{{{WORD_NS}}}name", "")
                if name and not name.startswith("_"):
                    yield "section", name
            elif tag == "t":
                yield "text", child.text or ""
            elif tag == "tab":
                yield "text", "\t"
            elif tag in ("br", "cr"):
                yield "text", "\n"
            else:
                yield from paragraph_text(child)

    def paragraphs(element):
        for child in element:
            if child.tag in (f"{{{WORD_NS}}}del", f"{{{WORD_NS}}}moveFrom"):
                continue
            if child.tag == f"{{{WORD_NS}}}p":
                yield child
            else:
                yield from paragraphs(child)

    section = ""
    for paragraph in paragraphs(body):
        text = ""
        for kind, value in paragraph_text(paragraph):
            if kind == "section":
                if text.strip():
                    yield section, text
                text = ""
                section = value
            else:
                text += value
                while "\n" in text:
                    line, text = text.split("\n", 1)
                    yield section, line
        if text:
            yield section, text


def read_lines(path):
    """Læs linjerne uden afsnitsnavne."""
    for _, line in read_section_lines(path):
        yield line


def extract_bars(lines):
    """Hver | starter en takt, inklusive en tom takt sidst på linjen."""
    bars = []
    for line in lines:
        line = line.strip()
        if "|" not in line:
            continue
        if line == "|":
            bars.append("")
            continue
        fields = line.split("|")
        if line.startswith("|"):
            fields = fields[1:]
        bars.extend(field.strip() for field in fields)
    return bars


def extract_section_bars(lines):
    """Returnér (afsnit, lokalt taktnummer, tekst) i dokumentrækkefølge."""
    rows = []
    previous_section = None
    number = 0
    for section, line in lines:
        if section != previous_section:
            number = 0
            previous_section = section
        for text in extract_bars([line]):
            number += 1
            rows.append((section, number, text))
    return rows


def write_xlsx(path, bars, overwrite=False):
    """Skriv rækker af (afsnit, taktnummer, tekst) til Excel."""
    if len(bars) > 1_048_575:
        raise ValueError("For mange takter til ét Excel-ark.")
    if any(len(value) > 32767 for bar in bars for value in (bar[0], bar[2])):
        raise ValueError("Et afsnit eller en takt overskrider Excels grænse på 32767 tegn.")
    sheet = ET.Element("worksheet", xmlns=SHEET_NS)
    views = ET.SubElement(sheet, "sheetViews")
    view = ET.SubElement(views, "sheetView", workbookViewId="0")
    ET.SubElement(view, "pane", ySplit="1", topLeftCell="A2",
                  activePane="bottomLeft", state="frozen")
    columns = ET.SubElement(sheet, "cols")
    for column, width in ((1, 24), (2, 10), (3, 70)):
        ET.SubElement(columns, "col", min=str(column), max=str(column),
                      width=str(width), customWidth="1")
    data = ET.SubElement(sheet, "sheetData")
    for number, values in enumerate([("Afsnit", "Takt", "Tekst"), *bars], 1):
        row = ET.SubElement(data, "row", r=str(number))
        for column, value in zip("ABC", values):
            cell = ET.SubElement(row, "c", r=f"{column}{number}",
                                 s="1" if number == 1 else "2")
            if isinstance(value, int):
                ET.SubElement(cell, "v").text = str(value)
            else:
                # Inline tekst bevarer bl.a. =, + og - uden formeltolkning.
                cell.set("t", "inlineStr")
                text = ET.SubElement(ET.SubElement(cell, "is"), "t")
                text.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
                text.text = value
    ET.SubElement(sheet, "autoFilter", ref=f"A1:C{len(bars) + 1}")
    parts = {
        "[Content_Types].xml": '''<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/><Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/></Types>''',
        "_rels/.rels": '''<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>''',
        "xl/workbook.xml": f'''<workbook xmlns="{SHEET_NS}" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Takter" sheetId="1" r:id="rId1"/></sheets></workbook>''',
        "xl/_rels/workbook.xml.rels": '''<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>''',
        "xl/styles.xml": f'''<styleSheet xmlns="{SHEET_NS}"><fonts count="2"><font><sz val="11"/><name val="Calibri"/></font><font><b/><sz val="11"/><color rgb="FFFFFFFF"/><name val="Calibri"/></font></fonts><fills count="3"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill><fill><patternFill patternType="solid"><fgColor rgb="FF24476A"/><bgColor indexed="64"/></patternFill></fill></fills><borders count="1"><border/></borders><cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs><cellXfs count="3"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/><xf numFmtId="0" fontId="1" fillId="2" borderId="0" xfId="0"/><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0" applyAlignment="1"><alignment vertical="top" wrapText="1"/></xf></cellXfs><cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles></styleSheet>''',
        "xl/worksheets/sheet1.xml": ET.tostring(sheet, encoding="utf-8", xml_declaration=True),
    }
    with ZipFile(path, "w" if overwrite else "x", compression=ZIP_DEFLATED) as archive:
        for name, content in parts.items():
            archive.writestr(name, content)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("source", nargs="?", type=Path, default=SOURCE)
    parser.add_argument("-o", "--output", type=Path, help="Excel-filens placering (.xlsx)")
    parser.add_argument("--overwrite", action="store_true", help="Overskriv eksisterende Excel-fil")
    args = parser.parse_args(argv)
    output = args.output or Path.cwd() / f"{args.source.stem}_takter.xlsx"
    if args.source.suffix.lower() != ".docx" or output.suffix.lower() != ".xlsx":
        parser.error("Kilden skal være .docx, og resultatet skal være .xlsx.")
    try:
        bars = extract_section_bars(read_section_lines(args.source))
        if not bars:
            raise ValueError("Ingen takter fundet. Takter skal være adskilt med |.")
        write_xlsx(output, bars, args.overwrite)
    except FileExistsError:
        parser.exit(1, f"Filen findes allerede: {output}. Brug --overwrite for at erstatte den.\n")
    except (OSError, BadZipFile, KeyError, ET.ParseError, ValueError) as error:
        parser.exit(1, f"Kunne ikke konvertere: {error}\n")
    print(f"Skrev {len(bars)} takter til {output.resolve()}")


if __name__ == "__main__":
    main()

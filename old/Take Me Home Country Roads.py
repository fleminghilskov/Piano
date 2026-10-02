import tkinter as tk
from tkinter import ttk
from pathlib import Path

title = "Take Me Home Country Roads"
HTML_FOLDER = Path(r"E:\Dropbox\lyricsappl\html\windows\ego-klaver")

SONG = [
    ('Intro', [
        ('G', 'G2-D2', 'D3-G3-B3'),
        ('G', 'G2-D2', 'D3-G3-B3'),
    ]),
    ('Vers 1', [
        ('G', 'G2-D2', 'D3-G3-B3'),
        ('Em', 'E2-G1', 'E3-G3-B3'),
        ('D', 'D2-A1', 'D3-F#3-A3'),
        ('C', 'C2-G1', 'C3-E3-G3'),
        ('G', 'G2-D2', 'D3-G3-B3'),
        ('Em', 'E2-G1', 'E3-G3-B3'),
        ('D', 'D2-A1', 'D3-F#3-A3'),
        ('C', 'C2-G1', 'C3-E3-G3'),
    ]),
    ('Chorus', [
        ('G', 'G2-D2', 'D3-G3-B3'),
        ('D', 'D2-A1', 'D3-F#3-A3'),
        ('Em', 'E2-G1', 'E3-G3-B3'),
        ('C', 'C2-G1', 'C3-E3-G3'),
        ('G', 'G2-D2', 'D3-G3-B3'),
        ('D', 'D2-A1', 'D3-F#3-A3'),
        ('C', 'C2-G1', 'C3-E3-G3'),
        ('G', 'G2-D2', 'D3-G3-B3'),
    ]),
    ('Vers 2', [
        ('G', 'G2-D2', 'D3-G3-B3'),
        ('Em', 'E2-G1', 'E3-G3-B3'),
        ('D', 'D2-A1', 'D3-F#3-A3'),
        ('C', 'C2-G1', 'C3-E3-G3'),
        ('G', 'G2-D2', 'D3-G3-B3'),
        ('Em', 'E2-G1', 'E3-G3-B3'),
        ('D', 'D2-A1', 'D3-F#3-A3'),
        ('C', 'C2-G1', 'C3-E3-G3'),
    ]),
    ('Chorus', [
        ('G', 'G2-D2', 'D3-G3-B3'),
        ('D', 'D2-A1', 'D3-F#3-A3'),
        ('Em', 'E2-G1', 'E3-G3-B3'),
        ('C', 'C2-G1', 'C3-E3-G3'),
        ('G', 'G2-D2', 'D3-G3-B3'),
        ('D', 'D2-A1', 'D3-F#3-A3'),
        ('C', 'C2-G1', 'C3-E3-G3'),
        ('G', 'G2-D2', 'D3-G3-B3'),
    ]),
    ('Bridge', [
        ('Em', 'E2-G1', 'E3-G3-B3'),
        ('D/F#', 'F#2', 'D3-F#3-A3'),
        ('G', 'G2-D2', 'D3-G3-B3'),
        ('C', 'C2-G1', 'C3-E3-G3'),
        ('G', 'G2-D2', 'D3-G3-B3'),
        ('D', 'D2-A1', 'D3-F#3-A3'),
        ('Em', 'E2-G1', 'E3-G3-B3'),
        ('F', 'F2-A1', 'F3-A3-C3'),
        ('C', 'C2', 'C3-E3-G3'),
        ('G', 'G2-D2', 'D3-G3-B3'),
        ('D', 'D2-A1', 'D3-F#3-A3'),
        ('D7', 'D2', 'D3-F#3-A3-C4'),
    ]),
    ('Chorus', [
        ('G', 'G2-D2', 'D3-G3-B3'),
        ('D', 'D2-A1', 'D3-F#3-A3'),
        ('Em', 'E2-G1', 'E3-G3-B3'),
        ('C', 'C2-G1', 'C3-E3-G3'),
        ('G', 'G2-D2', 'D3-G3-B3'),
        ('D', 'D2-A1', 'D3-F#3-A3'),
        ('C', 'C2-G1', 'C3-E3-G3'),
        ('G', 'G2-D2', 'D3-G3-B3'),
        ('G', 'G2-D2', 'D3-G3-B3'),
        ('D', 'D2-A1', 'D3-F#3-A3'),
        ('Em', 'E2-G1', 'E3-G3-B3'),
        ('C', 'C2-G1', 'C3-E3-G3'),
        ('G', 'G2-D2', 'D3-G3-B3'),
        ('D', 'D2-A1', 'D3-F#3-A3'),
        ('C', 'C2-G1', 'C3-E3-G3'),
        ('G', 'G2-D2', 'D3-G3-B3'),
    ]),
    ('Outtro', [
        ('G', 'G2-D2', 'D3-G3-B3'),
        ('D', 'D2-A1', 'D3-F#3-A3'),
        ('G', 'G2-D2', 'D3-G3-B3'),
        ('D', 'D2-A1', 'D3-F#3-A3'),
    ]),
]


# Indstillinger
WHITE_W = 18              # Bredden af de hvide tangenter
WHITE_H = 80              # Højden af de hvide tangenter
BLACK_W = WHITE_W / 1.75  # Bredden af de sorte tangenter
BLACK_H = WHITE_H / 1.625 # Højden af de sorte tangenter
KEYBOARD_Y = 45
LEFT_COLOR = "#ff4040"
RIGHT_COLOR = "#ffe72e"
GRID_COLUMNS = 3


# C1–B5 omfatter også F#1, G1, A1 og B1 fra vers 3 og 5.
white_notes = [
    f"{note}{octave}"
    for octave in range(1, 6)
    for note in ("C", "D", "E", "F", "G", "A", "B")
]
black_notes = {
    octave_index * 7 + position: f"{note}{octave}"
    for octave_index, octave in enumerate(range(1, 6))
    for position, note in ((0, "C#"), (1, "D#"), (3, "F#"), (4, "G#"), (5, "A#"))
}
keys = {note: ("white", i) for i, note in enumerate(white_notes)}
keys.update({note: ("black", i) for i, note in black_notes.items()})


def normalize_note(note):
    """Oversæt regnearkets b-toner til samme tangent som den tilsvarende #-tone."""
    flats = {"Db": "C#", "Eb": "D#", "Gb": "F#", "Ab": "G#", "Bb": "A#"}
    return flats.get(note[:-1], note[:-1]) + note[-1]


def chord_colors(left, right):
    colors = {}
    # Venstre hånd har forrang, hvis begge hænder bruger samme tangent.
    for notes, color in ((right, RIGHT_COLOR), (left, LEFT_COLOR)):
        for note in notes.split("-"):
            normalized = normalize_note(note)
            if normalized not in keys:
                raise ValueError(f"Ukendt tone {note!r}. Brug toner fra C1 til B5.")
            colors[keys[normalized]] = color
    return colors


class ChordViewer:
    def __init__(self, root):
        self.root = root
        self.index = 0
        self.chords = [
            (section, number, name, left, right)
            for section, chords in SONG
            for number, (name, left, right) in enumerate(chords, 1)
        ]
        root.title(title)
        root.configure(bg="#181818")
        root.geometry(f"{min(1320, root.winfo_screenwidth() - 80)}x{min(940, root.winfo_screenheight() - 100)}")

        controls = ttk.Frame(root)
        controls.pack(fill="x", padx=20, pady=(15, 0))
        self.previous = ttk.Button(controls, text="Forrige afsnit", command=lambda: self.move(-1))
        self.previous.pack(side="left")
        self.section = ttk.Combobox(
            controls, state="readonly", width=10, values=[name for name, _ in SONG]
        )
        self.section.pack(side="left", padx=10)
        self.section.bind("<<ComboboxSelected>>", self.select_section)
        self.selection = ttk.Combobox(
            controls, state="readonly", width=42,
            values=[f"{section} · {number}: {name}" for section, number, name, _, _ in self.chords],
        )
        self.selection.pack(side="left", fill="x", expand=True)
        self.selection.bind("<<ComboboxSelected>>", self.select_chord)
        self.next = ttk.Button(controls, text="Næste afsnit", command=lambda: self.move(1))
        self.next.pack(side="left", padx=(10, 0))

        self.width = len(white_notes) * WHITE_W
        self.canvas = tk.Canvas(
            root, width=self.width * 2, height=780, bg="#181818", highlightthickness=0
        )
        self.canvas.pack(padx=20, pady=10, fill="both", expand=True)
        self.canvas.bind("<Configure>", lambda event: self.draw_page())
        self.progress = tk.Label(root, bg="#181818", fg="white", font=("Arial", 10))
        self.progress.pack(pady=(8, 15))
        root.bind("<Left>", lambda event: self.move(-1))
        root.bind("<Right>", lambda event: self.move(1))
        self.show_chord()

    def move(self, step):
        start, end = self.page_bounds()
        if step > 0:
            if end == len(self.chords):
                return "break"
            self.index = end
        else:
            self.index = max(0, start - 1)
            self.index = self.page_bounds()[0]
        self.show_chord()
        return "break"

    def page_bounds(self):
        """Vis alle akkorder i det valgte afsnit på én side."""
        section, number, *_ = self.chords[self.index]
        section_start = self.index - (number - 1)
        section_size = next(len(chords) for name, chords in SONG if name == section)
        return section_start, section_start + section_size

    def select_section(self, event=None):
        self.index = next(i for i, chord in enumerate(self.chords) if chord[0] == self.section.get())
        self.show_chord()

    def select_chord(self, event=None):
        self.index = self.selection.current()
        self.show_chord()

    def show_chord(self):
        section = self.chords[self.index][0]
        self.section.set(section)
        self.selection.current(self.index)
        start, end = self.page_bounds()
        self.root.title(f"{title} – {section}")
        self.previous.configure(state="disabled" if start == 0 else "normal")
        self.next.configure(state="disabled" if end == len(self.chords) else "normal")
        self.progress.configure(text=f"{section} · {end - start} akkorder   |   Skift afsnit med ← / →")
        self.draw_page()

    def draw_page(self):
        canvas = self.canvas
        canvas.delete("all")
        start, end = self.page_bounds()
        columns = GRID_COLUMNS
        rows = (end - start + columns - 1) // columns
        cell_width = canvas.winfo_width() / columns
        # Tilpas rækkehøjden til klaviaturet med lidt luft under hver række.
        compact_height = 28 + WHITE_H * max(0, (cell_width - 20) / self.width) + 12
        cell_height = min(canvas.winfo_height() / rows, compact_height)
        if cell_width < 2 or cell_height < 2:
            return
        for offset, chord in enumerate(self.chords[start:end]):
            row, column = divmod(offset, columns)
            self.draw_chord(chord, column * cell_width, row * cell_height, cell_width, cell_height)

    def draw_chord(self, chord, x, y, width, height):
        section, number, name, left, right = chord
        colors = chord_colors(left, right)
        canvas = self.canvas
        scale = min((width - 20) / self.width, (height - 34) / WHITE_H)
        scale = max(0.05, scale)
        key_width = WHITE_W * scale
        key_height = WHITE_H * scale
        black_width = BLACK_W * scale
        black_height = BLACK_H * scale
        keyboard_x = x + (width - self.width * scale) / 2
        keyboard_y = y + 28
        canvas.create_text(x + width / 2, y + 13, text=name, fill="white", font=("Arial", 12, "bold"))
        for i, note in enumerate(white_notes):
            x1 = keyboard_x + i * key_width
            canvas.create_rectangle(
                x1, keyboard_y, x1 + key_width, keyboard_y + key_height,
                fill=colors.get(("white", i), "white"), outline="#333333", width=1,
            )
            if note.startswith("C"):
                canvas.create_text(
                    x1 + key_width / 2, keyboard_y + key_height - 7,
                    text=note, fill="#333333", font=("Arial", 7),
                )
        for position in black_notes:
            center = keyboard_x + (position + 1) * key_width
            canvas.create_rectangle(
                center - black_width / 2, keyboard_y,
                center + black_width / 2, keyboard_y + black_height,
                fill=colors.get(("black", position), "#222222"), outline="#444444", width=1,
            )


def export_html(path=None):
    """Gem alle afsnit som en selvstændig HTML-fil med SVG-klaviaturer."""
    from html import escape
    if path is None:
        path = HTML_FOLDER / f"{title} - Akkorder.html"

    sections = []
    keyboard_width = len(white_notes) * WHITE_W
    for section, chords in SONG:
        cards = []
        for name, left, right in chords:
            colors = chord_colors(left, right)
            shapes = []
            for i, note in enumerate(white_notes):
                x = i * WHITE_W
                color = colors.get(("white", i), "white")
                shapes.append(f'<rect x="{x}" y="1" width="{WHITE_W}" height="{WHITE_H}" fill="{color}" stroke="#333"/>')
                if note.startswith("C"):
                    shapes.append(f'<text x="{x + WHITE_W / 2}" y="{WHITE_H - 5}" text-anchor="middle" fill="#333" font-size="9">{note}</text>')
            for position in black_notes:
                x = (position + 1) * WHITE_W - BLACK_W / 2
                color = colors.get(("black", position), "#222222")
                shapes.append(f'<rect x="{x}" y="1" width="{BLACK_W}" height="{BLACK_H}" fill="{color}" stroke="#444"/>')
            label = escape(f"{name}. Venstre hånd: {left}. Højre hånd: {right}.", quote=True)
            cards.append(
                f'<article><h2>{escape(name)}</h2>'
                f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-1 0 {keyboard_width + 2} {WHITE_H + 2}" role="img" aria-label="{label}">'
                + ''.join(shapes) + '</svg></article>'
            )
        sections.append(f'<section data-name="{escape(section)}" aria-label="{escape(section)}"><div class="chords">' + ''.join(cards) + '</div></section>')
    options = ''.join(f'<option value="{i}">{escape(name)}</option>' for i, (name, _) in enumerate(SONG))
    document = '''<!doctype html>
<html lang="da">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>''' + escape(title) + ''' – Akkorder</title>
<style>
* { box-sizing:border-box; }
body { margin:0; padding:16px 24px; background:#181818; color:white; font-family:Arial,sans-serif; }
nav { display:flex; align-items:center; gap:12px; position:sticky; top:0; background:#181818; padding:0 0 12px; z-index:1; }
button,select { font:inherit; padding:6px 12px; }
select { flex:1; min-width:0; }
.chords { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:12px 24px; }
article { min-width:0; }
h2 { font-size:18px; text-align:center; margin:0 0 8px; }
svg { display:block; width:100%; height:auto; }
section { margin-bottom:24px; }
[hidden] { display:none !important; }
@media print {
  nav { display:none; }
  section[hidden] { display:block !important; }
  section { break-before:page; }
  section:first-of-type { break-before:auto; }
  article { break-inside:avoid; }
  body { print-color-adjust:exact; -webkit-print-color-adjust:exact; }
}
</style>
</head>
<body>
<nav aria-label="Vælg afsnit">
<button id="previous" type="button">Forrige afsnit</button>
<select id="section" aria-label="Afsnit">''' + options + '''</select>
<button id="next" type="button">Næste afsnit</button>
</nav>
''' + '\n'.join(sections) + '''
<script>
(() => {
  const songTitle = document.title.replace(/ – Akkorder$/, '');
  const sections = Array.from(document.querySelectorAll('section'));
  const select = document.getElementById('section');
  const previous = document.getElementById('previous');
  const next = document.getElementById('next');
  let current = 0;
  function show(index) {
    current = Math.max(0, Math.min(sections.length - 1, index));
    sections.forEach((section, i) => { section.hidden = i !== current; });
    select.value = String(current);
    previous.disabled = current === 0;
    next.disabled = current === sections.length - 1;
    document.title = songTitle + ' – ' + sections[current].dataset.name;
    window.scrollTo(0, 0);
  }
  select.addEventListener('change', () => show(Number(select.value)));
  previous.addEventListener('click', () => show(current - 1));
  next.addEventListener('click', () => show(current + 1));
  document.addEventListener('keydown', event => {
    if (event.target.matches('select,input,textarea')) return;
    if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
      event.preventDefault();
      show(current + (event.key === 'ArrowRight' ? 1 : -1));
    }
  });
  show(0);
})();
</script>
</body>
</html>
'''
    Path(path).write_text(document, encoding="utf-8")
    return Path(path)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=f"Vis eller eksportér akkorderne til {title}.")
    parser.add_argument("--html", action="store_true", help="Gem kun HTML-filen uden at åbne vinduet.")
    args = parser.parse_args()
    output = export_html()
    print(f"HTML gemt: {output}")
    if not args.html:
        root = tk.Tk()
        ChordViewer(root)
        root.mainloop()

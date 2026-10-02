import unittest

from update_lyrics_chords2 import ChordFields, fill_fields


def chord(name, bar, slot, left='C3'):
    return dict(name=name, bar=bar, slot=slot, left=left, right='', svg='<svg/>')


class FillFieldsTests(unittest.TestCase):
    def test_split_parentheses_and_multiple_voicings(self):
        html = ('<p data-afsnit="vers 1"><span data-takt="6">|</span>'
                '<span data-takt="6">(</span><span data-takt="6">)</span>'
                '<span>lyrics &amp; more</span><span data-takt="6">()</span></p>')
        chords = [chord('B', '6', 1, 'B2'), chord('F#', '6', 2, 'F#2')]
        result, data, count = fill_fields(html, {'Vers1': chords})
        self.assertEqual(count, 2)
        fields = ChordFields(result).fields()
        self.assertEqual([f['text'] for f in fields], ['(B)', '(F#)'])
        self.assertEqual([f['attrs']['data-akkord'] for f in fields], ['0', '1'])
        self.assertEqual(data['vers 1'][1]['left'], 'F#2')
        self.assertIn('<span>lyrics &amp; more</span>', result)
        self.assertEqual(fill_fields(result, {'Vers1': chords})[0], result)
        updated = [chord('C', '6', 1), chords[1]]
        self.assertIn('(C)</button>', fill_fields(result, {'Vers1': updated})[0])

    def test_match_bar_not_global_position(self):
        html = '<p data-afsnit="intro"><span data-takt="2">()</span><span data-takt="1">()</span></p>'
        result, _, _ = fill_fields(html, {'Intro': [chord('C', '1', 1), chord('G', '2', 1)]})
        self.assertEqual([f['text'] for f in ChordFields(result).fields()], ['(G)', '(C)'])

    def test_missing_first_bar_in_interlude(self):
        html = ('<p data-afsnit="mellemspil 1"><span>|</span><span>()</span>'
                '<span data-takt="2">()</span><span data-takt="3">()</span>'
                '<span data-takt="4">()</span></p>')
        chords = [chord(name, str(bar), 1) for bar, name in
                  enumerate(['Asus4', 'A', 'Asus4', 'A'], 1)]
        result, _, count = fill_fields(html, {'mellemspil1': chords})
        self.assertEqual(count, 4)
        fields = ChordFields(result).fields()
        self.assertEqual([f['bar'] for f in fields], ['1', '2', '3', '4'])
        self.assertEqual([f['text'] for f in fields], ['(Asus4)', '(A)', '(Asus4)', '(A)'])
        self.assertEqual(fill_fields(result, {'mellemspil1': chords})[0], result)

    def test_ambiguous_missing_bar_still_fails(self):
        for bars in [(None, '3'), ('1', None, '2'), (None, '2', '1')]:
            html = '<p data-afsnit="intro">' + ''.join(
                '<span' + (f' data-takt="{bar}"' if bar else '') + '>()</span>'
                for bar in bars) + '</p>'
            with self.subTest(bars=bars), self.assertRaises(ValueError):
                fill_fields(html, {'Intro': [chord('C', str(i), 1) for i in range(1, 4)]})

    def test_mismatched_counts_and_manual_chords_fail(self):
        cases = [
            '<span data-afsnit="intro" data-takt="1">()</span>' * 2,
            '<span data-afsnit="intro" data-takt="2">()</span>',
            '<button data-afsnit="intro" data-takt="1" data-akkord="0">(Am)</button>',
        ]
        for html in cases:
            with self.subTest(html=html), self.assertRaises(ValueError):
                fill_fields(html, {'Intro': [chord('C', '1', 1)]})
        with self.assertRaisesRegex(ValueError, 'manglende'):
            fill_fields(cases[0][:len(cases[0]) // 2],
                        {'Intro': [chord('C', '1', 1), chord('G', '1', 2)]})


if __name__ == '__main__':
    unittest.main()

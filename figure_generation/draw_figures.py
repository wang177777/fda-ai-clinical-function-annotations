#!/usr/bin/env python3
"""Render the two Data Descriptor figures from the distributed CSV tables.

Outputs vector PDF, 300 dpi PNG, 600 dpi TIFF, and a local figure_qa.json.
No author-workspace paths, private cardinality files, or external renderer are used.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
import os
from collections import Counter, defaultdict
from pathlib import Path

from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white
from reportlab.pdfbase.pdfmetrics import stringWidth, registerFont
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image
from pypdf import PdfReader
import pypdfium2 as pdfium

ROOT = Path(__file__).resolve().parents[1]
WIDTH = 16.4 / 2.54 * 72
INK = HexColor('#173345')
MUTED = HexColor('#526877')
TEAL = HexColor('#187C91')
BORDER = HexColor('#93AAB6')
FILL = HexColor('#F1F6F8')
RULE = HexColor('#D7E2E7')
EXACT_NAMES = {'EXACT_RECORDED_SPAN_MATCH', 'EXACT_QUOTE_MATCH_CORRECTED_SPAN_SAME_PAGE',
               'EXACT_QUOTE_MATCH_CORRECTED_PAGE_OR_SPAN'}
TABLE_NAMES = ('authorizations', 'field_annotations', 'positive_labels', 'evidence_links',
               'source_records', 'associated_source_relationships', 'source_bridges',
               'semantic_review_records', 'semantic_review_sources')


def select_fonts(args):
    """Prefer Arial, then installed open-source TrueType, then PDF Helvetica."""
    if bool(args.font_regular) != bool(args.font_bold):
        raise ValueError('Supply --font-regular and --font-bold together.')
    if args.font_family == 'helvetica' and args.font_regular:
        raise ValueError('Custom fonts cannot be combined with --font-family helvetica.')
    if args.font_regular:
        candidates = [('Custom', args.font_regular, args.font_bold)]
    elif args.font_family == 'helvetica':
        candidates = []
    else:
        candidates = []
        if args.font_family in ('auto', 'arial'):
            for directory in (Path('/System/Library/Fonts/Supplemental'),
                              Path('/Library/Fonts'),
                              Path(os.environ.get('WINDIR', 'C:/Windows')) / 'Fonts'):
                candidates.extend([('Arial', directory / 'Arial.ttf', directory / 'Arial Bold.ttf'),
                                   ('Arial', directory / 'arial.ttf', directory / 'arialbd.ttf')])
        if args.font_family in ('auto', 'open-source'):
            for directory in (Path('/usr/share/fonts/truetype/dejavu'),
                              Path('/usr/share/fonts/dejavu'),
                              Path('/usr/local/share/fonts'), Path('/Library/Fonts')):
                candidates.append(('DejaVu Sans', directory / 'DejaVuSans.ttf',
                                   directory / 'DejaVuSans-Bold.ttf'))
            for directory in (Path('/usr/share/fonts/truetype/liberation2'),
                              Path('/usr/share/fonts/truetype/liberation')):
                candidates.append(('Liberation Sans', directory / 'LiberationSans-Regular.ttf',
                                   directory / 'LiberationSans-Bold.ttf'))
    for name, regular, bold in candidates:
        if regular.is_file() and bold.is_file():
            registerFont(TTFont('FigureRegular', str(regular)))
            registerFont(TTFont('FigureBold', str(bold)))
            return 'FigureRegular', 'FigureBold', {
                'family': name, 'regular_sha256': hashlib.sha256(regular.read_bytes()).hexdigest(),
                'bold_sha256': hashlib.sha256(bold.read_bytes()).hexdigest(), 'embedded': True}
    if args.font_regular or args.font_family == 'arial':
        raise FileNotFoundError('Requested TrueType font pair was not found.')
    return 'Helvetica', 'Helvetica-Bold', {'family': 'Helvetica', 'embedded': False,
                                          'note': 'PDF Standard 14 font fallback'}


def load_tables(data_dir):
    tables = {}
    for name in TABLE_NAMES:
        with (data_dir / f'{name}.csv').open(newline='', encoding='utf-8-sig') as f:
            tables[name] = list(csv.DictReader(f))
    return tables


def check_data_hashes(data_dir):
    manifest = data_dir.parent / 'checksums.sha256'
    expected = {}
    for line in manifest.read_text(encoding='utf-8').splitlines():
        digest, relative = line.split(maxsplit=1)
        expected[relative.lstrip('*')] = digest
    observed = {}
    for name in TABLE_NAMES:
        relative = f'data/{name}.csv'
        digest = hashlib.sha256((data_dir / f'{name}.csv').read_bytes()).hexdigest()
        if expected.get(relative) != digest:
            raise ValueError(f'Input checksum missing or mismatched: {relative}')
        observed[relative] = digest
    return observed


def cardinalities(tables):
    """Recompute all structural assertions used to draw the figure relationships."""
    ids = {}
    for name, key in (('authorizations', 'submission_number'),
                      ('field_annotations', 'annotation_id'), ('evidence_links', 'annotation_id'),
                      ('source_records', 'source_record_id'), ('source_bridges', 'bridge_id'),
                      ('associated_source_relationships', 'annotation_id')):
        ids[name] = {r[key] for r in tables[name]}
        assert len(ids[name]) == len(tables[name]), (name, 'duplicate key')
    assert ids['field_annotations'] == ids['evidence_links']
    annotations = ids['field_annotations']
    auths = Counter(r['submission_number'] for r in tables['field_annotations'])
    assert set(auths) == ids['authorizations'] and set(auths.values()) == {6}
    assert all(r['annotation_id'] == f"{r['submission_number']}:{r['field']}"
               for r in tables['field_annotations'])
    label_keys = {(r['annotation_id'], r['label']) for r in tables['positive_labels']}
    assert len(label_keys) == len(tables['positive_labels'])
    assert {r['annotation_id'] for r in tables['positive_labels']} <= annotations
    label_counts = Counter(r['annotation_id'] for r in tables['positive_labels'])
    assert all(r['field'] != 'component_status' for r in tables['positive_labels'])
    # Positive memberships must exactly expand the five coded annotation fields.
    expanded = {(r['annotation_id'], code) for r in tables['field_annotations']
                if r['field'] != 'component_status' and r['annotation_state'] == 'CODED'
                for code in r['codes'].split(';') if code}
    assert label_keys == expanded
    source_counts, ref_counts, subjects = {}, {}, defaultdict(set)
    for name in ('evidence_links', 'source_bridges'):
        records = tables[name]
        counter, references = Counter(), Counter()
        for row in records:
            assert row['annotation_id'] in annotations
            source_ids = [s for s in row['source_record_ids'].split(';') if s]
            assert source_ids and len(source_ids) == len(set(source_ids))
            assert set(source_ids) <= ids['source_records']
            counter[len(source_ids)] += 1
            references.update(source_ids)
            if name == 'evidence_links':
                for source_id in source_ids:
                    subjects[source_id].add(row['annotation_id'].split(':')[0])
        source_counts[name] = references
        ref_counts[name] = counter
    bridges = Counter(r['annotation_id'] for r in tables['source_bridges'])
    assert set(bridges) == ids['associated_source_relationships']
    unique_spans = len({(r['text_sha256'], r['physical_page'], r['normalized_char_start'],
                        r['normalized_char_end']) for r in tables['source_bridges']})
    ev_uses = Counter(source_counts['evidence_links'].get(s, 0) for s in ids['source_records'])
    return {
        'authorization_to_field_records': {'exactly_per_authorization': 6},
        'field_annotation_to_evidence_link': {'exactly_per_field': 1},
        'field_annotation_to_positive_label_memberships': {
            'min': min(label_counts.get(a, 0) for a in annotations),
            'max': max(label_counts.values()), 'component_status_memberships': 0},
        'evidence_record_to_source_record_references': {
            'counts_by_references_per_record': dict(ref_counts['evidence_links']),
            'expanded_edges': sum(source_counts['evidence_links'].values()),
            'distinct_referenced_source_records': len(source_counts['evidence_links'])},
        'source_record_to_evidence_records': {'counts_by_evidence_records_per_source': dict(ev_uses),
                                             'max': max(ev_uses)},
        'source_records_linked_to_more_than_one_subject_authorization':
            sum(len(v) > 1 for v in subjects.values()),
        'annotation_to_bridge_records': {'referenced_annotations': len(bridges),
            'counts_by_bridge_records_per_referenced_annotation': dict(Counter(bridges.values())),
            'annotations_without_bridge_records': len(annotations) - len(bridges)},
        'bridge_record_to_source_record_references': {
            'counts_by_references_per_bridge_record': dict(ref_counts['source_bridges']),
            'expanded_edges': sum(source_counts['source_bridges'].values()),
            'distinct_referenced_source_records': len(source_counts['source_bridges'])},
        'bridge_unique_text_spans_by_hash_page_start_end': unique_spans,
        'annotation_to_associated_source_relationship_rows': {
            'exactly_one_for_affected_annotations': len(ids['associated_source_relationships']),
            'zero_for_other_annotations': len(annotations) - len(ids['associated_source_relationships'])},
        'join_instruction': "Explode semicolon-delimited source_record_ids before joining to "
            "source_records.source_record_id; do not join the unsplit string as a scalar key. "
            "evidence_links and source_bridges both permit one-to-many source references."
    }


class Drawing:
    def __init__(self, stem, height):
        self.stem, self.height = stem, height
        self.path = OUT / f'{stem}.pdf'
        self.c = canvas.Canvas(str(self.path), pagesize=(WIDTH, height), pageCompression=1, invariant=1,
                               initialFontName=FONT, initialFontSize=8.4)
        self.c.setTitle(stem.replace('_', ' '))
        self.c.setAuthor('Scientific Data manuscript')
        self.min_font = 100
        self.text_count = 0

    def text(self, x, y, value, size=8.4, bold=False, color=INK, align='left', max_width=None):
        """Top-origin baseline coordinates, with deterministic bounds checks."""
        assert size >= 8.0, (value, size)
        face = BOLD if bold else FONT
        w = stringWidth(value, face, size)
        if max_width is not None:
            assert w <= max_width + .01, (value, w, max_width)
        left = x - (w / 2 if align == 'center' else w if align == 'right' else 0)
        assert left >= 0 and left + w <= WIDTH and size <= y <= self.height - 3, (value, left, y)
        self.c.setFillColor(color)
        self.c.setFont(face, size)
        self.c.drawString(left, self.height - y, value)
        self.min_font = min(size, self.min_font)
        self.text_count += 1

    def rect(self, x, y, w, h, fill=FILL, stroke=None, radius=0):
        self.c.setFillColor(fill)
        if stroke is not None:
            self.c.setStrokeColor(stroke)
            self.c.setLineWidth(.75)
        if radius:
            self.c.roundRect(x, self.height-y-h, w, h, radius, fill=1, stroke=int(stroke is not None))
        else:
            self.c.rect(x, self.height-y-h, w, h, fill=1, stroke=int(stroke is not None))

    def line(self, points, color=RULE, width=.75, arrow=False):
        self.c.setStrokeColor(color)
        self.c.setFillColor(color)
        self.c.setLineWidth(width)
        p = self.c.beginPath()
        p.moveTo(points[0][0], self.height-points[0][1])
        for x, y in points[1:]:
            p.lineTo(x, self.height-y)
        self.c.drawPath(p)
        if arrow:
            (x0,y0),(x1,y1) = points[-2:]
            angle = math.atan2(y1-y0,x1-x0)
            length, half = 5.0, 2.35
            bx,by=x1-length*math.cos(angle),y1-length*math.sin(angle)
            p=self.c.beginPath(); p.moveTo(x1,self.height-y1)
            p.lineTo(bx+half*math.sin(angle),self.height-(by-half*math.cos(angle)))
            p.lineTo(bx-half*math.sin(angle),self.height-(by+half*math.cos(angle)))
            p.close(); self.c.drawPath(p,fill=1,stroke=0)

    def box(self,x,y,w,h,title,count,body):
        self.rect(x,y,w,h,fill=FILL,stroke=BORDER,radius=4)
        title = [title] if isinstance(title,str) else title
        for i,t in enumerate(title):
            self.text(x+9,y+17+i*11,t,size=9.4,bold=True,max_width=w-18)
        count_y=y+33+(len(title)-1)*11
        self.text(x+9,count_y,f'{count:,} rows',size=10.4,bold=True,color=TEAL,max_width=w-18)
        for i,line in enumerate(body):
            self.text(x+9,count_y+19+i*11,line,size=8.1,max_width=w-18)

    def finish(self):
        self.c.showPage(); self.c.save()
        document = pdfium.PdfDocument(self.path)
        page = document[0]
        for ext, dpi in (('png', 300), ('tiff', 600)):
            bitmap = page.render(scale=dpi / 72, rev_byteorder=True)
            im = bitmap.to_pil().convert('RGB')
            options = {'compression': 'tiff_lzw'} if ext == 'tiff' else {}
            im.save(OUT / f'{self.stem}.{ext}', dpi=(dpi, dpi), **options)
            im.close()
            bitmap.close()
        page.close()
        document.close()
        results = {'width_cm': 16.4, 'height_pt': self.height,
                   'minimum_font_pt': self.min_font, 'text_objects': self.text_count,
                   'vector_pdf': self.path.name, 'font_selection': FONT_SELECTION}
        for ext, dpi in (('png', 300), ('tiff', 600)):
            with Image.open(OUT / f'{self.stem}.{ext}') as im:
                results[ext] = {'pixels': list(im.size),
                               'dpi': [float(v) for v in im.info.get('dpi', (dpi, dpi))],
                               'mode': im.mode}
        reader = PdfReader(self.path)
        page = reader.pages[0]
        fonts = {}
        for ref in page['/Resources']['/Font'].values():
            font = ref.get_object()
            descriptor = font.get('/FontDescriptor')
            fonts[str(font['/BaseFont'])] = bool(descriptor and any(
                key in descriptor.get_object() for key in ('/FontFile', '/FontFile2', '/FontFile3')))
        if FONT != 'Helvetica':
            assert all(fonts.values()), fonts
        assert len(reader.pages) == 1
        assert abs(float(page.mediabox.width) - WIDTH) < 0.001
        results.update(pdf_pages=len(reader.pages), pdf_fonts_embedded=fonts,
                       standard_14_font_fallback=FONT == 'Helvetica',
                       pdf_image_xobjects=len(page['/Resources'].get('/XObject', {})))
        return results


def figure1():
    d=Drawing('Figure_1_data_relations',423)
    x1,x2,x3,w=10,169,328,127
    d.box(x1,15,w,99,'Authorizations',N['authorizations'],[
        'submission_number','Scope; function grouping','Baseline + current values'])
    d.box(x2,15,w,99,'Field annotations',N['field_annotations'],[
        'annotation_id','Six fields per authorization','Codes + explicit field state'])
    d.box(x3,15,w,99,'Positive labels',N['positive_labels'],[
        'annotation_id + code','First five fields only','Nonexclusive memberships'])
    d.line([(x1+w,68),(x2,68)],TEAL,1.15,True)
    d.text((x1+w+x2)/2,58,'1 : 6',8.3,align='center')
    d.line([(x2+w,68),(x3,68)],TEAL,1.15,True)
    d.text((x2+w+x3)/2,58,'0..many',8.0,align='center')
    d.line([(x2+w/2,114),(x2+w/2,153)],TEAL,1.15,True)
    d.text(x2+w/2+10,138,'1 : 1',8.3)
    d.box(x1,153,w,114,'Source records',N['source_records'],[
        'source_record_id','Public URL; retrieval date','Document + text hashes','Shared across field records'])
    d.box(x2,153,w,114,'Evidence links',N['evidence_links'],[
        'annotation_id','Recorded + verified locators','Quote + text hashes','Source relation + check status'])
    d.box(x3,153,w,114,['Associated-source','relationships'],N['associated_source_relationships'],[
        'annotation_id','Continuity or integration','Scope + configuration'])
    d.line([(x2,209),(x1+w,209)],TEAL,1.15,True)
    d.text((x1+w+x2)/2,199,'IDs',8.3,align='center')
    d.line([(x2+w,209),(x3,209)],TEAL,1.15,True)
    d.text((x2+w+x3)/2,199,'0..1',8.3,align='center')
    d.rect(x2,307,286,69,FILL,BORDER,4)
    d.text(x2+9,324,'Source bridges',9.4,True)
    d.text(x2+92,324,f'{N["source_bridges"]:,} rows',10.4,True,color=TEAL)
    d.text(x2+9,341,'annotation_id; source_record_ids',8.1)
    d.text(x2+9,353,f'{BRIDGE_SPANS} distinct text locations across current and associated sources',8.1,max_width=268)
    d.text(x2+9,365,'Page + normalized span; source + quote hashes',8.1,max_width=268)
    d.line([(x3+w/2,267),(x3+w/2,307)],TEAL,1.15,True)
    d.text(x3+w/2+8,292,'1..many',8.1)
    d.line([(x2,343),(x1+w/2,343),(x1+w/2,267)],TEAL,1.15,True)
    d.text(137,335,'IDs',8.3,align='center')
    d.text(10,391,"Source joins: split source_record_ids at ';', then join to source_record_id.",8.0)
    d.text(10,403,'Evidence and bridge ID lists allow multiple sources; each list has one ID in this release.',8.0)
    d.text(10,416,REVIEW_NOTE,8.0,color=MUTED,max_width=WIDTH-20)
    return d.finish()


def figure2():
    d=Drawing('Figure_2_validation_layers',473)
    d.text(10,21,'a',11.3,True)
    d.text(27,21,f'Retained locator checks | {N["evidence_links"]:,} field records',10.5,True,max_width=WIDTH-37)
    statuses=[
        ('EXACT_RECORDED_SPAN_MATCH','Recorded span matched','#187C91'),
        ('EXACT_QUOTE_MATCH_CORRECTED_SPAN_SAME_PAGE','Exact span added on recorded page','#59A4AE'),
        ('EXACT_QUOTE_MATCH_CORRECTED_PAGE_OR_SPAN','Exact page or span added','#A1C9CE'),
        ('QUOTE_PRESENT_MULTIPLE_PAGES_NO_AUTOMATIC_CORRECTION','Quote found on multiple pages','#A6783D'),
        ('RECORDED_IMAGE_TRANSCRIPTION_NOT_RECHECKED','Image-transcription locator not rechecked','#D7B277'),
        ('NO_MACHINE_TEXT_ANCHOR','Page-only reference','#929A9F'),
    ]
    d.text(27,37,'Stored-text matching in the retained coordinate audit',8.6,color=MUTED)
    start,barw=10,WIDTH-20
    for code,label,color in statuses:
        width=barw*STATUS[code]/N['evidence_links']
        d.rect(start,50,width,19,HexColor(color))
        start+=width
    matched = STATUS['EXACT_RECORDED_SPAN_MATCH']
    d.text(20,63,f'{matched:,} recorded spans matched',9.0,True,color=white)
    d.text(WIDTH-10,82,f'{N["evidence_links"]-matched:,} records in other states',8.2,color=MUTED,align='right')
    d.text(10,82,f'Single linear scale: 0 to {N["evidence_links"]:,} records',8.2,color=MUTED)
    d.text(27,102,'Locator state',8.5,True)
    d.text(404,102,'Records',8.5,True,align='right')
    d.text(WIDTH-10,102,'%',8.5,True,align='right')
    d.line([(10,108),(WIDTH-10,108)])
    for i,(code,label,color) in enumerate(statuses):
        y=123+i*15
        d.rect(11,y-7,7,7,HexColor(color))
        d.text(27,y,label,8.6,max_width=339)
        d.text(404,y,f'{STATUS[code]:,}',8.6,align='right')
        d.text(WIDTH-10,y,f'{100*STATUS[code]/N["evidence_links"]:.2f}',8.6,align='right')
    d.line([(10,210),(WIDTH-10,210)])
    d.text(10,235,'b',11.3,True)
    d.text(27,235,f'Exact text anchors | {sum(EXACT_SOURCES.values()):,} field records',10.5,True)
    same_page = STATUS['EXACT_QUOTE_MATCH_CORRECTED_SPAN_SAME_PAGE']
    page_span = STATUS['EXACT_QUOTE_MATCH_CORRECTED_PAGE_OR_SPAN']
    d.text(27,251,f'{matched:,} recorded spans + {same_page} same-page spans + {page_span} page/span updates',8.5,color=MUTED)
    kinds=[
        ('FDA_PDF_TEXT_EXTRACT',('FDA PDF','text extract')),
        ('FDA_HTML_EXTRACT',('FDA HTML','extract')),
        ('STORED_WEB_EXCERPT',('Stored web','excerpt')),
        ('STORED_IMAGE_TRANSCRIPTION',('Stored image','transcription')),
    ]
    gap=9
    tilew=(WIDTH-20-3*gap)/4
    for i,(kind,labels) in enumerate(kinds):
        x=10+i*(tilew+gap)
        d.rect(x,263,tilew,64,FILL,None,3)
        d.text(x+9,280,labels[0],8.6,bold=True,max_width=tilew-18)
        d.text(x+9,292,labels[1],8.6,max_width=tilew-18)
        d.text(x+9,314,f'{EXACT_SOURCES[kind]:,}',13.0,bold=True,color=TEAL)
    d.text(10,352,'c',11.3,True)
    d.text(27,352,'Structure and associated-source coverage',10.5,True)
    d.text(10,375,'Release structure',9.1,True)
    d.text(245,375,'Associated-source relationships',9.1,True)
    d.line([(232,368),(232,428)])
    left=[f'{N["authorizations"]:,} authorizations × 6 fields',
          f'{N["positive_labels"]:,} positive label memberships',
          'Unique keys; allowed codes; explicit states',
          'Joins, counts and data checksums: pass']
    right=[f'{N["associated_source_relationships"]} field records across {REL_SUBJECTS} authorizations',
           f'{N["source_bridges"]} bridge rows; {BRIDGE_SPANS} distinct text locations',
           'Continuity and integration relationships',
           'Scope and configuration recorded']
    for i,line in enumerate(left): d.text(10,390+i*12,line,8.45,max_width=214)
    for i,line in enumerate(right): d.text(245,390+i*12,line,8.45,max_width=WIDTH-255)
    d.text(10,449,'Text anchors are field-linked records; source passages can recur across fields.',8.1,color=MUTED)
    d.text(10,464,REVIEW_NOTE,8.1,color=MUTED,max_width=WIDTH-20)
    return d.finish()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir', type=Path, default=ROOT / 'data')
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'manuscript' / 'figures')
    parser.add_argument('--font-family', choices=('auto', 'arial', 'open-source', 'helvetica'),
                        default='auto')
    parser.add_argument('--font-regular', type=Path)
    parser.add_argument('--font-bold', type=Path)
    args = parser.parse_args()
    global OUT, FONT, BOLD, FONT_SELECTION, TABLES, N, REVIEW_NOTE, STATUS, EXACT_SOURCES
    global CARD, REL_SUBJECTS, BRIDGE_SPANS
    OUT = args.output_dir
    OUT.mkdir(parents=True, exist_ok=True)
    FONT, BOLD, FONT_SELECTION = select_fonts(args)
    TABLES = load_tables(args.data_dir)
    input_hashes = check_data_hashes(args.data_dir)
    N = {name: len(value) for name, value in TABLES.items()}
    CARD = cardinalities(TABLES)
    STATUS = Counter(r['locator_check_status'] for r in TABLES['evidence_links'])
    EXACT_SOURCES = Counter(r['text_source_kind'] for r in TABLES['evidence_links']
                           if r['locator_check_status'] in EXACT_NAMES)
    REL_SUBJECTS = len({r['annotation_id'].split(':')[0]
                       for r in TABLES['associated_source_relationships']})
    BRIDGE_SPANS = CARD['bridge_unique_text_spans_by_hash_page_start_end']
    REVIEW_NOTE = (f'Targeted semantic review: {N["semantic_review_records"]} field records; '
                   f'{N["semantic_review_sources"]} source references (Table 1).')
    # Guard the release-specific graphic against silently accepting changed data.
    assert N['authorizations'] * 6 == N['field_annotations'] == N['evidence_links'] == 9144
    assert N['positive_labels'] == 11120
    assert N['semantic_review_records'] == 12 and N['semantic_review_sources'] == 6
    assert len(STATUS) == 6 and sum(STATUS.values()) == 9144
    assert sum(EXACT_SOURCES.values()) == 9015 and BRIDGE_SPANS == 43
    assert REL_SUBJECTS == 20
    assert all(len(r['source_record_ids'].split(';')) == 1
               for name in ('evidence_links', 'source_bridges') for r in TABLES[name])
    qa = {'Figure_1': figure1(), 'Figure_2': figure2(), 'table_counts': N,
          'locator_counts': dict(STATUS), 'exact_anchor_sources': dict(EXACT_SOURCES),
          'structural_cardinalities': CARD,
          'semantic_review_separate_from_retained_coordinate_counts': True,
          'data_source': 'data/*.csv', 'verified_input_sha256': input_hashes,
          'text_bounds_checked': True, 'all_text_at_least_8_pt': True}
    (OUT / 'figure_qa.json').write_text(json.dumps(qa, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps(qa, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()

# Reproduce the manuscript figures

This script renders Figures 1 and 2 directly from nine distributed CSV tables. It recomputes the relation cardinalities, locator-state counts and source-type counts, and verifies each input against `checksums.sha256`. The stored coordinate checks and the targeted semantic-review records retain their separate reporting layers.

From the repository root, using Python 3.10 or later:

```sh
python -m pip install -r figure_generation/requirements.txt
python scripts/validate_resource.py
python figure_generation/draw_figures.py
```

The default inputs are `data/`; the default output directory is `manuscript/figures/`. The source-document archives are not needed to render these figures. To write a separate local export:

```sh
python figure_generation/draw_figures.py --output-dir /tmp/clinical-function-figures
```

For each figure, the script writes a vector PDF, a 300 dpi PNG and a 600 dpi LZW-compressed TIFF. The figure width is 16.4 cm, with all text at least 8 pt. Figure 1 is 423 pt high and Figure 2 is 473 pt high. `figure_qa.json` records dimensions, font sizes, font embedding, verified input hashes, table counts and the freshly computed structural cardinalities. This QA file is written beside the figure outputs; the script does not modify `validation/` or refresh the release checksums.

## Fonts and rendering

The default font search prefers installed Arial, then installed DejaVu Sans or Liberation Sans, and finally the PDF Standard 14 Helvetica font. The published Arial layout can be selected explicitly with `--font-family arial`; this option fails clearly if Arial is unavailable. Fonts are not redistributed in this repository. An installed open-source TrueType pair can also be supplied directly:

```sh
python figure_generation/draw_figures.py \
  --font-regular /path/to/LiberationSans-Regular.ttf \
  --font-bold /path/to/LiberationSans-Bold.ttf
```

To reproduce the portable fallback without any installed font files:

```sh
python figure_generation/draw_figures.py --font-family helvetica
```

TrueType fonts are embedded in the PDF. Helvetica uses the PDF Standard 14 font set and is identified as unembedded in the QA record. All font choices undergo text-bound checks; a different font must fit the fixed layout without reducing text below 8 pt. PDFium, supplied by `pypdfium2`, renders both raster formats; no `pdftoppm`, operating-system font configuration or external PDF utility is required. PDF metadata are fixed for repeatable exports with the same dependencies and font files. Font-family changes can alter glyph appearance and raster pixels while preserving data and layout.

The dependencies in `requirements.txt` record the versions used for release preparation. Code is distributed under the repository's MIT license; the generated figures are covered by CC BY 4.0 as described in `LICENSE.md`.

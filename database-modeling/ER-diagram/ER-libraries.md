# ER-diagram i LaTeX – biblioteker og pakker

## I bruk nå

- **tikz-er2** – lastes inn med `\usepackage{tikz-er2}`. Pakken ligger lokalt i `database-modeling/tikz-er2.sty` (hentet fra GitHub). Gir bl.a. `entity`, `weak entity`, `relationship`, `ident relationship`, `\key{}`, `\discriminator`.
- **TikZ** + **er-biblioteket** (`\usetikzlibrary{er}`)  
  Diagrammet utvider/overstyrer med egne definisjoner (f.eks. `rectangle split`, farger, kardinaliteter).

- **shapes.multipart** – for entiteter som én node med header + attributter (rectangle split).
- **shapes.geometric** – for diamant-form på relasjoner.

## Alternativer

### TikZ innebygd `er` (allerede i bruk)

- **Lastes inn med:** `\usetikzlibrary{er}`
- **Fordeler:** Ingen ekstra installasjon, følger med TeX Live.
- **Styrker:** Tydelige stilenavn (`entity`, `relationship`), enkel å tilpasse med `every entity` / `every relationship`.
- **Begrensninger:** Ingen ferdig støtte for weak entity eller identifiserende relasjon; det bygges manuelt (som i dette prosjektet).

### tikz-er2 (installert lokalt)

- **Lastes inn med:** `\usepackage{tikz-er2}`.
- **Plassering:** `database-modeling/tikz-er2.sty` (samme mappe som `ER-diagram.tex`), så pdflatex finner den uten ekstra sti.
- **Fordeler:** Støtte for weak entity, ident relationship, `\key{}`, `\discriminator`, osv.

### Graphviz (automatisk layout) – testet

- **Filer:** `ER-diagram.dot` (kilde), `ER-diagram-gv.pdf` og `ER-diagram-neato.pdf` (generert).
- **Kjør:**  
  `dot -Tpdf -o ER-diagram-gv.pdf ER-diagram.dot`  
  eller  
  `neato -Tpdf -o ER-diagram-neato.pdf ER-diagram.dot`  
  (neato gir ofte færre kryssende kanter.)
- **Fordeler:** Automatisk plassering av noder, ingen manuelle koordinater.
- **Begrensninger:** Ingen attributter i nodene, ingen kardinaliteter på kantene; kun struktur (entiteter + relasjoner). Passer som rask layout-inspirasjon eller for å redusere kryss.

### LuaLaTeX + TikZ graph drawing

- **Pakke:** `texlive-luatex` (installeres med `sudo apt install texlive-luatex`).
- **Font-cache:** LuaLaTeX trenger en skrivbar cache for luaotfload. I dette prosjektet er cache bygget i `database-modeling/.texlive-var/`. Kjør derfra:
  - **Første gang (eller etter oppdatering):**  
    `TEXMFVAR=$(pwd)/.texlive-var luaotfload-tool --update`
  - **Kompilering:**  
    `TEXMFVAR=$(pwd)/.texlive-var lualatex ER-diagram.tex`
- **TikZ graph drawing:** Med LuaLaTeX kan du bruke `\usetikzlibrary{graphdrawing}` + `\usegdlibrary{force}` for automatisk layout.

### Andre verktøy (ikke LaTeX)

- **draw.io / diagrams.net** – kan eksportere til PDF eller bilde for innsetting i rapport.
- **dbdiagram.io** – tekst-basert ER, eksport til bilde/PDF.
- **pgAdmin / DBeaver** – kan generere ER fra eksisterende databaser.

## Anbefaling

- For ren LaTeX og minimal avhengighet: **fortsett med TikZ + `er`** som nå (med de egne stilene for weak entity og relasjoner).
- For mer avansert ER-notasjon og færre manuelle definisjoner: vurder **tikz-er2** med lokal installasjon i prosjektmappen.

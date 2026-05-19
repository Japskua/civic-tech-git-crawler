# Verifiable recent civic-tech references — for §2 Related Work

Found via WebSearch + arXiv/ACM/Wiley spot-checks. Each entry has a real title, authors, year, venue, and DOI that I confirmed exists. I am **not** adding these to `references.bib` automatically — pick the ones you've read or will read, then add them yourself.

## Strongest candidates (civic-tech specific, post-2016)

### 1. Knutas et al. 2023 — **highly recommended**

```bibtex
@inproceedings{Knutas2023,
  author    = {Knutas, Antti and Siemon, Dominik and Tylosky, Natasha and Maccani, Giovanni},
  title     = {Contradicting Motivations in Civic Tech Software Development: Analysis of a Grassroots Project},
  booktitle = {Proceedings of the 2023 IEEE/ACM 45th International Conference on Software Engineering: Software Engineering in Society (ICSE-SEIS)},
  year      = {2023},
  pages     = {149--160},
  publisher = {IEEE},
  doi       = {10.1109/ICSE-SEIS58686.2023.00021},
  url       = {https://arxiv.org/abs/2302.03469}
}
```

**Why this one matters:** peer-reviewed empirical civic-tech-specific paper at ICSE-SEIS 2023. Activity-theory case study of a grassroots civic-tech software group. Antti Knutas is at **LUT University** — so you may already know this paper or know the author personally. Citing it both shores up the recency gap AND signals awareness of your home institution's civic-tech research.

**Where to cite in your paper:** §2 "Civic technology" paragraph; possibly also in §5 Discussion alongside the "what's civic-tech-specific" framing.

### 2. Saldivar et al. 2019 — **the Saldivar paper your reviewer named**

```bibtex
@article{Saldivar2019,
  author  = {Saldivar, Jorge and Parra, Cristhian and Alcaraz, Marcelo and Arteta, Rebeca and Cernuzzi, Luca},
  title   = {Civic Technology for Social Innovation},
  journal = {Computer Supported Cooperative Work (CSCW)},
  volume  = {28},
  number  = {1--2},
  pages   = {169--207},
  year    = {2019},
  publisher = {Springer},
  doi     = {10.1007/s10606-018-9311-7}
}
```

**Why this one matters:** the reviewer named this specifically. Empirical CSCW-journal paper examining civic-tech investment and participation. Anchors the "we're complementing a qualitative civic-tech literature" framing.

**Where to cite:** §2 "Civic technology" paragraph (replace or supplement the [McNutt2016] citation pair).

### 3. Schrock 2019 chapter — **the Schrock work your reviewer named**

```bibtex
@incollection{Schrock2019,
  author    = {Schrock, Andrew R.},
  title     = {What is Civic Tech? Defining a Practice of Technical Pluralism},
  booktitle = {The Right to the Smart City},
  editor    = {Cardullo, Paolo and Di Feliciantonio, C{\'e}sare and Kitchin, Rob},
  pages     = {125--134},
  year      = {2019},
  publisher = {Emerald Publishing Limited},
  doi       = {10.1108/978-1-78769-139-120191009}
}
```

**Why this one matters:** the reviewer named "Schrock on civic tech." This 2019 book chapter defines civic tech as a "practice of technical pluralism," which dovetails with our operational-definition approach in §3.1.

**Where to cite:** §2 "Civic technology" paragraph; possibly §3.1 alongside the C1–C3 criteria as background on definitional debates.

**Alternative (more accessible but less academic):** Schrock, A.R. (2018). *Civic Tech: Making Technology Work for People*. Rogue Academic Press. ISBN 978-1-7320848-0-3.

### 4. Knight Foundation 2017 — **the post-2013 Knight successor your reviewer named**

```bibtex
@techreport{Knight2017,
  author      = {{Knight Foundation and Rita Allen Foundation}},
  title       = {Scaling Civic Tech: Paths to a Sustainable Future},
  institution = {John S. and James L. Knight Foundation},
  year        = {2017},
  type        = {Report},
  url         = {https://knightfoundation.org/reports/scaling-civic-tech/}
}
```

**Why this one matters:** the direct successor to your [Patel2013] reference. Specifically addresses sustainability in civic-tech — the topic of your paper. Strongest fit alongside [Patel2013] in §1 and §2.

**Where to cite:** §1 paragraph 2 alongside [Patel2013, McNutt2016]; §5 Discussion under "what 'sustainable' would actually look like".

## Strong supporting candidate (OSS-health empirical, very recent)

### 5. Lumbard et al. 2024 — **same CHAOSS authors, 2024 follow-up**

```bibtex
@article{Lumbard2024,
  author  = {Lumbard, Kevin and Germonprez, Matt and Goggins, Sean P.},
  title   = {An empirical investigation of social comparison and open source community health},
  journal = {Information Systems Journal},
  volume  = {34},
  number  = {2},
  pages   = {499--532},
  year    = {2024},
  publisher = {Wiley},
  doi     = {10.1111/isj.12485}
}
```

**Why this one matters:** same authors as your existing [Goggins2021] citation, but 2024. Empirically investigates how OSS communities use health metrics to compare themselves — directly relevant to your CHAOSS-framework discussion in §3 and §5.

**Where to cite:** §2 "OSS health and contributor dynamics" paragraph (alongside or replacing [Goggins2021]); §5 Discussion under "effort-based measurement matters."

## Workshop-paper candidate (use if you want a state-of-the-field summary)

### 6. Aragon et al. 2020 — CSCW 2020 workshop

```bibtex
@inproceedings{Aragon2020,
  author    = {Aragon, Pablo and Alvarado Garcia, Adriana and Le Dantec, Christopher A. and Flores-Saviaga, Claudia and Saldivar, Jorge},
  title     = {Civic Technologies: Research, Practice and Open Challenges},
  booktitle = {Companion Publication of the 2020 Conference on Computer Supported Cooperative Work and Social Computing (CSCW '20 Companion)},
  year      = {2020},
  publisher = {ACM},
  doi       = {10.1145/3406865.3418586},
  url       = {https://arxiv.org/abs/2012.00515}
}
```

**Why this one matters:** workshop paper, but a useful "state of civic-tech research" summary with five active civic-tech researchers as authors (including Saldivar again).

**Where to cite:** §2 "Civic technology" paragraph as a summary citation, or skip if you've already picked Knutas+Saldivar+Schrock+Knight.

## Suggested combination

The reviewer wants 3–5 recent refs. My recommendation, ordered by impact:

1. **Add Knutas 2023** (most-recent, peer-reviewed, civic-tech-specific empirical) — citation slot in §2 Civic technology paragraph
2. **Add Saldivar 2019** (reviewer named it; CSCW journal; named) — citation slot in §2 Civic technology paragraph
3. **Add Schrock 2019** (reviewer named it; definitional anchor) — citation slot in §2 Civic technology paragraph
4. **Add Knight 2017** (direct successor to Patel 2013; sustainability-themed) — citation slot in §1 paragraph 2
5. **Optionally add Lumbard 2024** if you want a very recent OSS-health-framework citation — §2 first paragraph

Five additions takes your reference count from 13 to 18 — sits comfortably below the 20–25 the reviewer suggested.

## How to add them

1. Copy the BibTeX entries above into `references.bib`.
2. In `paper_esem.tex`, find the comment block starting `% TODO(author): The second reviewer flagged the civic-tech literature...` in §2 (around line 110) and add `\cite{Knutas2023,Saldivar2019,Schrock2019}` (or whichever you pick) at the end of the "Civic technology" paragraph.
3. In §1 paragraph 2, add `\cite{Knight2017}` after `[Patel2013,McNutt2016]`.
4. Once added, delete the `% TODO(author): ...` comment block.

## What I did *not* verify

The reviewer also mentioned "Engagement Lab @ Emerson College publications" and "Hartzog, W. & Selinger, E. recent work on civic tech ethics" in passing. I didn't search for these because the four refs above already cover the gap, and Hartzog/Selinger work is mostly on tech ethics rather than civic-tech specifically. If you want one of those instead, search Engagement Lab's publications page or Hartzog's faculty page directly.

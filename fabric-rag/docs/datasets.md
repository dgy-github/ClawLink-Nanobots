# Textile/Fabric Dataset References

Goal: list candidate public datasets or references useful for fabric/texture retrieval.

## Quick Summary

| Dataset | Focus | License / Access | Notes |
| --- | --- | --- | --- |
| DTD | General describable textures | Creative Commons Attribution 4.0 | Diverse categories, good for texture descriptors
| MIT VisTex | Scanned textures incl. fabrics | Research-only (check page) | Classic benchmark, stable per-class structure
| CUReT | Reflectance + texture variations | Requires request form | Captures illumination + pose changes
| KTH-TIPS2 | Material recognition (fabrics, paper, etc.) | Research (non-commercial) | Provides scale + pose variation
| DeepFashion2 | Clothing detection + attributes | Non-commercial, license approval | Large multi-attribute dataset, includes fabric patterns
| Fabric Defect (AITEX/NEU/TILDA) | Industrial fabric defect detection | Research usage, request terms | Useful for anomaly cases
| Kylberg Texture | High-res textures | Creative Commons Attribution | Balanced classes, easy to load
| Kaggle Fabric Textures | Synthetic/collected fabric swatches | Depends on uploader (often CC BY-NC) | Quick bootstrap dataset, verify per uploader

## Dataset Notes

### 1. Describable Textures Dataset (DTD)
- **Size:** 5,640 images (47 texture categories).
- **Download:** `wget -r -N -c -np https://www.robots.ox.ac.uk/~vgg/data/dtd/`
- **License:** CC-BY 4.0 (must credit VGG Oxford).
- **Why useful:** Baseline texture variability and descriptors; not fabric-specific but good for model sanity checks.

### 2. MIT VisTex
- **Size:** 167 texture classes, many fabric/weave scans.
- **Download:** Provided as `.tar.gz` archives per class on the official site; simple `wget` loops work.
- **License:** Research-only; citation required.
- **Why useful:** Controlled capture, uniform lighting; great for retrieval prototypes.

### 3. CUReT (Columbia-Utrecht Reflectance and Texture Dataset)
- **Size:** 61 materials with 205 images each under varying illumination/viewpoints.
- **Download:** Requires filling a short agreement form; once approved, download via HTTP link.
- **License:** Research use only; do not redistribute raw images publicly.
- **Why useful:** Tests robustness of embeddings to lighting/view changes, relevant for real-world cloth photography.

### 4. KTH-TIPS2
- **Size:** ~11 materials × 4 samples × 9 scales × 4 poses (~4,752 images).
- **Download:** Provided via KTH server (zip bundles). Mirror available on some academic mirrors.
- **License:** Non-commercial research; cite the original paper.
- **Why useful:** Includes multiple fabric-like categories (linen, cotton) and scale variation for zoom-level robustness.

### 5. DeepFashion2 / FabricNet (clothing-focused)
- **Size:** 491k images with masks, attributes, landmarks.
- **Download:** Requires submitting a Google Form and getting approval; download via provided URLs.
- **License:** Non-commercial research, must avoid re-distribution.
- **Why useful:** Rich metadata (attributes such as "striped", "plaid", "lace") that can supervise text-to-fabric retrieval.
- **Caveat:** Large storage requirement (>50 GB) and may contain human subjects; review privacy constraints.

### 6. Fabric Defect / Industrial Datasets (AITEX, NEU, TILDA)
- **AITEX Textile Defect Database**
  - 7 defect categories (e.g., double pick, knot) captured with industrial cameras.
  - Useful for anomaly detection branch of the retrieval system.
- **NEU Surface Defect Database**
  - Not strictly fabric, but includes surface defects; use as negative/contrastive examples.
- **TILDA Textile Database**
  - Focused on quality inspection tasks.
- **Access:** Typically through academic request or Kaggle mirrors; verify each.

### 7. Kylberg Texture Dataset
- **Size:** 28 classes × 160 images per class (128 × 128 px, grayscale).
- **Download:** Direct zip from Uppsala University site.
- **License:** CC-BY; easy to redistribute internally.
- **Why useful:** Simple dataset for debugging pipelines or benchmarking FAISS search quickly.

### 8. Kaggle Fabric Texture Collections (community uploads)
- **Examples:** "Fabric Pattern Dataset", "Fabric Images" (various contributors).
- **Usage:** Great for quick demos, but license varies—most are CC BY-NC or custom terms.
- **Action:** Keep metadata CSV with uploader + citation; respect non-commercial clauses.

### 9. Additional References to Check
- **ZJU-Leather / PU Leather Defect datasets** for leather-like surfaces.
- **HNU Fabric dataset** (Hunan University) for weaving defects.
- **COCO-Stuff textile subset** — treat as broad background data for contrastive training.

## Action Items
- Confirm availability and license for each dataset.
- Document download commands/scripts once network access is permitted (put scripts under `data/scripts/`).
- Decide minimal subset to bootstrap local retrieval demo (likely DTD + VisTex + one Kaggle set).
- Track approvals (DeepFashion2, CUReT) in `docs/approvals.md` once submitted.

## Bootstrap Pack (<=10 GB target)
| Dataset | Est. Size | Role | License / Status | Next Step |
| --- | --- | --- | --- | --- |
| DTD | ~1.8 GB | Texture variety sanity check | CC-BY 4.0 / direct download | Script `wget` recipe inside `data/scripts/download_public.sh` |
| MIT VisTex | ~2.5 GB | Controlled weave + pattern references | Research-only / manual download | Mirror URLs + note citation text |
| Kaggle Fabric Pattern Set | 1-3 GB | More fabric-specific samples | Varies (often CC BY-NC) / manual approval via Kaggle | Pick one uploader, record license verbatim |
| Kylberg Texture | <0.5 GB | Quick debug dataset (grayscale) | CC-BY / direct zip | Add extraction command |
| AITEX Textile Defect subset | <2 GB | Negative/anomaly examples | Research-only / request | Identify contact + approval steps |

> Goal: keep combined footprint under 10 GB so baseline index fits on dev laptop SSD.

### Access Checklist (2026-03-23)
| Dataset | Access Path | Notes / TODO |
| --- | --- | --- |
| DTD | `scripts/download_dtd_sample.py` already usable; full tarball needs reliable network | Small subset (200 imgs) verified inside repo; document retry/backoff for blocked hosts |
| MIT VisTex | http://vismod.media.mit.edu/vismod/imagery/VisTex (per-class `.tar.gz`) | Need scripted downloader + citation text; confirm redistribution policy before mirroring |
| Kylberg Texture | https://www.cb.uu.se/~gustaf/texture/ | Direct zip download permitted (CC-BY). Add `scripts/download_kylberg.py` placeholder + SHA256 for integrity |
| Kaggle Fabric Pattern | Kaggle CLI (`kaggle datasets download ...`) | Requires Kaggle token stored in env; track chosen uploader + license verbatim in `docs/approvals.md` |
| AITEX / TILDA | University contact form/email | Collect POC email + justification template referencing Baidu replacement plan |
| DeepFashion2 | Google Form request | Prep org letter, list privacy safeguards, storage size (~50 GB) requirement |

## Approval / Access Tracker
- **DeepFashion2:** Approval form pending — draft request once baseline proves value.
- **CUReT:** Needs agreement form; compile rationale referencing fabric lighting variations.
- **AITEX/TILDA:** Confirm latest download URLs; add point-of-contact emails to future `docs/approvals.md`.

## Dataset Priorities (alpha release)
1. **DTD + VisTex** — minimal yet diverse set to validate OpenCLIP embeddings.
2. **Kaggle Fabric Patterns** — adds real cloth textures; ensure metadata CSV retained for filtering.
3. **Defect-based sets (AITEX/TILDA)** — support anomaly-focused queries later.
4. **DeepFashion2 (attributes)** — unlock text-driven retrieval once storage + approvals sorted.

# ClockWork photographic asset attribution

## Included photographs (downloaded and inspected 2026-10-25)

Four actual JPEG photographs are stored in `frontend/public/photos/`. The earlier Wikimedia source was not retried. These new assets came from Pexels after its source pages and [Pexels License](https://www.pexels.com/license/) were reviewed.

The Pexels License permits free use and modification in apps and presentations, with attribution appreciated rather than required. It prohibits implied endorsement, offensive use of identifiable people, resale of unaltered copies, stock-platform redistribution, and trademark use. These images are integrated illustrations inside ClockWork, not a stock-photo product, institutional endorsement or inspection evidence. No claim of verified facilities, accreditation or association with the real photographed campus is made.

Every full photo/gallery is labeled **Illustrative photo — not inspection evidence**. EVC facilities are explicitly not verified inspection evidence. Photographer/source credits are retained here even though not required by the license.

| Local file | Photographer | Source | Dimensions | Bytes |
|---|---|---|---|---|
| `campus.jpg` | DΛVΞ GΛRCIΛ | [Modern University Building by Lakeside](https://www.pexels.com/photo/modern-university-building-by-lakeside-31085766/) | 800 x 533 | 75,201 |
| `laboratory.jpg` | Kindel Media | [A Microscope and Laboratory Equipments](https://www.pexels.com/photo/a-microscope-and-laboratory-equipments-8325750/) | 800 x 600 | 34,045 |
| `classroom.jpg` | mitbg000 | [Rows of Desks and Chairs in a Classroom](https://www.pexels.com/photo/rows-of-desks-and-chairs-in-a-classroom-19199263/) | 800 x 438 | 47,745 |
| `library.jpg` | Element5 Digital | [Bookshelves in the Library](https://www.pexels.com/photo/bookshelves-in-the-library-1370292/) | 800 x 1198 | 145,885 |

## Local/offline delivery and optimization

Only bounded 800px-wide CDN variants were downloaded (`auto=compress&cs=tinysrgb&w=800&q=75`), not full-resolution originals. All four together are **302,876 bytes** (about 296 KiB). No new image dependency was installed. Runtime URLs are local `/photos/*.jpg`; there is no Pexels hotlink or remote fetch in the application. The app still needs its local/static host; offline assets do not imply a service-worker/offline-install feature.

Photography is restricted to institution profiles and EVC facilities. campus.jpg maps only to INST-2 (Cedar Technical Institute). All other institutions use stable colored initials covers until a distinct licensed exterior is available. Application, institution and Today lists have no photographs. Laboratory, classroom and library images remain exclusively facility illustrations, never campus exteriors. No new assets or licenses were added in this refinement.

The prior inline SVG fallback remains if loading/decoding fails, labeled photo unavailable rather than claiming a photograph is present. Old original SVG source assets remain preserved but are no longer the normal campus image.

## Reproducible source URLs and checksums

- `campus.jpg`: [downloaded variant](https://images.pexels.com/photos/31085766/pexels-photo-31085766.jpeg?auto=compress&cs=tinysrgb&w=800&q=75); SHA-256 `f49ccebba2001b0ea40f2ddde3d67de8dbd9d7d8df5dcaa530926f6cc170271f`.
- `laboratory.jpg`: [downloaded variant](https://images.pexels.com/photos/8325750/pexels-photo-8325750.jpeg?auto=compress&cs=tinysrgb&w=800&q=75); SHA-256 `280addd1fbf6fe6e116d7c1a398fa494e35bf04e0aeaab0ab9a67d937785d9d8`.
- `classroom.jpg`: [downloaded variant](https://images.pexels.com/photos/19199263/pexels-photo-19199263.jpeg?auto=compress&cs=tinysrgb&w=800&q=75); SHA-256 `41ad7d6201014e3a06a0573b44742ffb71f5e08da1aff60ddd20a631034d1268`.
- `library.jpg`: [downloaded variant](https://images.pexels.com/photos/1370292/pexels-photo-1370292.jpeg?auto=compress&cs=tinysrgb&w=800&q=75); SHA-256 `26fadea131d9a5da942ffdc8df3b55ee2876a691f5c4f33b4961d082fbc525d7`.

## Replacement instructions

All downloads succeeded; manual placement is not required. To replace a photograph later, use a suitably licensed optimized JPEG in exactly:

- `frontend/public/photos/campus.jpg`
- `frontend/public/photos/laboratory.jpg`
- `frontend/public/photos/classroom.jpg`
- `frontend/public/photos/library.jpg`

Record the replacement source, photographer, license and changes here, then rerun image checks. Do not substitute real institution evidence without a separately authorized evidence-storage workflow. Missing files safely use the fallback.

## Earlier source limitation

Wikimedia download attempts in earlier work returned HTTP 429. Those photographs were never included, and no blocked Commons URL was retried in this focused change. The earlier statement that the application contains only SVG illustrations is now superseded by the four downloaded JPEGs listed above.

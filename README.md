# C2S2 website

An English-only website for the **Center for Computational Social Science and Human Dynamics**, University of Trento and Fondazione Bruno Kessler.

Adapted from the local `css-synosys_website-main` template, using its Hugo Blox Bootstrap v5 foundation, landing-page renderer, section parser and purple/green visual direction. The C2S2 navigation, page layouts and content blocks are local customisations. The original template folder is unchanged.

## Preview locally

On macOS or Linux, open a terminal in this repository:

```sh
./scripts/setup.sh       # once per computer; downloads verified project-local tools
./scripts/preview.sh     # starts the preview; keep this terminal open
```

Open the URL printed by Hugo, usually <http://localhost:1313/web/>. Edits appear automatically. Stop the preview with `Ctrl+C`.

The setup script installs **Hugo Extended 0.135.0**, **Go 1.23.2** and a Python environment for BibTeX imports into the ignored `.tools/` folder. Python 3.9 or later must already be installed. If you previously installed the website tools, run `./scripts/setup-publications.sh` once to add BibTeX support. The versions match the verified build and GitHub workflow. No Node.js, database or paid hosting service is needed. First build requires internet access to download the theme modules. These are compatibility pins, not claims that these are the latest versions; test upgrades together with the old theme before changing them.

On Windows, install Hugo **Extended 0.135.0** from [Hugo releases](https://github.com/gohugoio/hugo/releases/tag/v0.135.0), Go **1.23.2** from [Go downloads](https://go.dev/dl/) and Python 3.9 or later. With Hugo and Go on your PATH, run:

```powershell
py -m venv .tools/bibtex-venv
.tools/bibtex-venv/Scripts/python -m pip install -r requirements-publications.txt
.tools/bibtex-venv/Scripts/python scripts/preview.py
```

The shell scripts are for macOS/Linux.

## Everyday editing

Content files use Markdown. The block between `---` lines contains settings; the text beneath it is the page body. Use spaces, not tabs, in these settings. Wrap titles containing colons in quotes.

| To change | Edit |
| --- | --- |
| Homepage wording and section order | `content/_index.md` |
| About the center | `content/about/index.md` |
| Research overview and theme descriptions | `content/research/` |
| People directory | `content/authors/<person>/_index.md` |
| Publications and featured selections | `publications.bib` |
| Publications page introduction | `content/publications/index.md` |
| Events | `content/event/<event>/index.md` |
| PhDs, postdocs, theses and internships | `content/opportunities/<opportunity>/index.md` |
| Contact information | `content/contact/index.md` |
| Navigation links | `config/_default/menus.yaml` |
| Site description and theme settings | `config/_default/params.yaml` |
| Colours, type and spacing | `assets/scss/custom.scss` |
| Page structure | `layouts/` |

### Add a person

Duplicate an existing person's folder under `content/authors/`, rename it, then change the name, surname, initials and profile URL. Keep the `_build` settings: these records populate the people directory and link to existing researcher profiles. The directory sorts by surname.

To show a photo, place an approved portrait in `assets/media/people/` and add `portrait: "media/people/<person>.jpg"` to their front matter. Record its source URL in `portrait_source`. Hugo crops the image to a square and displays it in a circular badge. If `portrait` is omitted or its file is missing, the person's initials appear instead. When duplicating a person, update or remove their portrait fields as well.

### Add an opportunity

Create a draft from the reusable template (replace `project-name` with a short lowercase slug):

```sh
PATH="$PWD/.tools:$PWD/.tools/go/bin:$PATH" .tools/hugo new content --kind opportunity opportunities/project-name/index.md
```

Edit the generated `content/opportunities/project-name/index.md`. Set the title, a short summary, and `opportunity_type` to `PhD`, `Postdoc`, `Thesis` or `Internship`. The `date` is the posting date; the directory shows newest posts first. Fill in the body sections with the project description, eligibility, practical details and application instructions.

Optional fields are `location`, `deadline` and `application_url`. Leave them empty to hide them. Write the deadline as readable text, including the time zone if there is a specific cutoff, for example `15 March 2027, 17:00 CET`, or `Until filled`. Use a full HTTPS URL for the application link.

Preview with `./scripts/preview.sh --buildDrafts`. When ready, set `draft: false`, then commit and push to publish. The entry automatically appears on the Opportunities page and gets its own detail page. Set `draft: true` again to withdraw a closed opportunity; deadlines are displayed as text and do not automatically remove listings.

The template lives in `archetypes/opportunity.md`; editing it affects future drafts only. The directory introduction is in `content/opportunities/_index.md`. With no published entries, the directory shows its empty message.

### Add an event

Duplicate an existing folder under `content/event/`, rename it, and change its fields:

```yaml
---
title: "Your event title"
date: "2027-03-15T17:00:00+01:00"
event_type: Seminar
summary: "Speaker name · Institution"
location: "Room and address"
time_label: "17:00 CET"
end_label: ""
source_url: "https://example.org/event"
draft: true
---
Optional longer description, written in Markdown.
```

Use `+01:00` / CET for Italian winter time or `+02:00` / CEST for summer time. Remove `draft: true` when ready. Preview drafts with `./scripts/preview.sh --buildDrafts`. For all-day events, omit `time_label`; `end_label` supplies an optional readable end date for multi-day events. Use the start date in `date` for sorting.

Upcoming events appear on the homepage automatically; otherwise it shows the three most recent archived events. Classification changes when the site is rebuilt. Rebuild manually from GitHub Actions if an event has passed without another content update. For multi-day events the archive currently classifies using the start time.

### Publications: edit one BibTeX file

The Publications page starts with 25 selected research items from 2023–2026 by researchers in the people directory. [Selection notes and verification sources](docs/publications-curation.md) explain the scope and publication-year choices.

1. Export a paper as **BibTeX** from Zotero, your reference manager or its publisher.
2. Paste the entry into `publications.bib`, using a unique citation key. Keep full author lists and check the publication year.
3. Save while `./scripts/preview.sh` is running: the page updates automatically. Items are grouped by year, newest first, then alphabetically by title.
4. Commit and push the bibliography change. GitHub automatically imports it before building the website.

Each entry requires `title`, `author`, a four-digit `year`, a venue (`journal`, `booktitle`, `publisher` or `howpublished`), and either `doi` or `url`. Use `and` between authors, as usual in BibTeX. UTF-8 names and standard LaTeX accents are supported. Use self-contained entries; expand inherited `crossref` fields before importing.

Optional fields:

| Field | Purpose |
| --- | --- |
| `featured = {true}` | Adds a Featured badge |
| `selected = {false}` | Hides an entry while keeping it in your source file; entries are shown by default |
| `pdf = {https://…}` | Adds a public PDF link |
| `code = {https://…}` | Adds a code link |
| `correction = {https://…}` | Links to a published correction |
| `volume`, `number`, `pages` | Adds standard citation details |

To remove a paper, delete its entry or set `selected = {false}`. The page count and year navigation adjust automatically; 25 is the initial selection, not a fixed limit. Visitors can view or download each citation and download the entire visible bibliography. Avoid private notes or local file paths in entries: their fields are included in the public BibTeX downloads.

Do not edit or commit `data/publications.json`: it is generated from the bibliography. Invalid entries stop a production build and produce an explanatory error. During a running preview, the last valid bibliography stays visible until the error is corrected.

The archived starter examples under `examples/original-starter/` are reference material only; their older publication-import workflow is not used.

## Publish with GitHub Pages

The repository remote is `https://github.com/C2S2-Trento/web.git`.

1. In that repository, go to **Settings → Pages → Build and deployment → Source → GitHub Actions**. This is a one-time setup and requires repository administration access.
2. Review the site locally, especially the content review notes below.
3. In GitHub Desktop, review the changed files, write a commit summary, commit to `main`, then choose **Push origin**. Alternatively, commit and push with Git.
4. Follow **Actions → Build and publish C2S2**. The workflow validates and imports BibTeX, builds the site, checks internal links, and deploys it.
5. With no custom domain configured, the intended address is **https://c2s2-trento.github.io/web/**. A successful workflow confirms publication.

Pull requests run the build and link checks without deploying. Do not commit `.tools/`, `public/` or generated caches. The workflow obtains the deployment address from GitHub so `/web/` URLs and a future custom domain both work.

No push, deployment or GitHub settings changes have been performed as part of the initial local build.

### Keep the current university domain later

First publish and review the GitHub Pages version. To use `c2s2.unitn.it`, coordinate DNS with the university IT team, configure the custom domain in GitHub Pages, and update `baseURL` in `config/_default/hugo.yaml`. Enable HTTPS once GitHub issues the certificate. Do not switch university DNS before the replacement site is approved. Follow [GitHub's custom-domain documentation](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site).

## Build and check

```sh
./scripts/build.sh
.tools/bibtex-venv/bin/python -m unittest discover -s tests -v
python3 scripts/check_site.py public
```

The build script imports the bibliography before running Hugo. On Windows, run `scripts/import_publications.py` with the Python environment above, then `hugo --minify`. The published website is entirely static; Python runs only during builds and local previews. The checker verifies generated internal links, local assets and fragment targets, including the GitHub project URL prefix. It does not check external researcher or event websites.

## Content review before launch

- Publications: 25 selected entries, curated on 14 October 2026; review the [selection notes](docs/publications-curation.md) and adjust the bibliography as desired.
- Names and external profile links: migrated from [C2S2 people](https://c2s2.unitn.it/chi-siamo.html), retrieved 13 October 2026. Confirm the roster is current; titles, biographies and individual affiliations have not been invented.
- Ten events (2022–2025): migrated from the [C2S2 homepage](https://c2s2.unitn.it/), with English titles and source links. Historical speaker affiliations describe the original event. Confirm whether newer events should be added.
- The English full name is documented on the [university's C2S2 event page](https://eventi.unitn.it/it/incontri-con-le-unita-di-ricerca-c2s2).
- About copy summarises the original site's institutional description. The four research areas are based on `content/research_areas.txt`; review their wording before launch.
- Contact uses the published department address and individual profile links. Add a shared email if the center has one.
- Seven member portraits come from their linked UniTrento profiles (checked 14 October 2026). Members with other profile links, no profile photo, or unavailable UniTrento pages retain initials. An original network illustration is used in place of institutional logo assets. Review official branding before launch.
- Site pages are English only; some source/profile links lead to Italian-language third-party pages.

## Maintenance alternatives

**Recommendation: keep Hugo for this template-based version.** Content updates require only Markdown/YAML or BibTeX changes and a push. The tradeoff is the older Hugo Blox dependency: avoid upgrading Hugo independently of the theme.

| Option | Best fit | Maintenance tradeoff |
| --- | --- | --- |
| Current Hugo Blox adaptation | Retaining the supplied academic template and its content formats | Familiar research-site structure; older theme and pinned tools need coordinated upgrades |
| Plain Hugo with a small local theme | Long-term simplicity with the same Markdown workflow | My preferred future simplification: fewer theme dependencies, but recreating specialised academic features takes work |
| Jekyll | A conventional, modest research website close to GitHub Pages defaults | GitHub Pages supports it directly; local editing adds a Ruby/Bundler toolchain |
| Eleventy | A custom site with a small set of layouts and comfortable JavaScript maintenance | Flexible Markdown and templates; Node.js dependencies replace Hugo/Go |

These are different site generators, not different hosting requirements. All can produce a static site for GitHub Pages. A browser-based CMS could be added later if several editors prefer forms, but it introduces authentication and configuration.

Official references: [Hugo on GitHub Pages](https://gohugo.io/host-and-deploy/host-on-github-pages/), [Jekyll and GitHub Pages](https://jekyllrb.com/docs/github-pages/), [Eleventy getting started](https://www.11ty.dev/docs/).

## Template attribution

The original research-group starter and Hugo Blox code retain their MIT licence in `LICENSE.md`. Selected template partials retain their upstream comments. This repository adapts the local CSS-SynoSys version without copying its researchers, publications, institutional logos or visualisation scripts into the published site. The original starter examples are reference material, not C2S2 content.

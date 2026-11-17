# gramps_devutil

Shared development tooling for Kevin White's Gramps feature work. The Gramps
fork is split into many feature repos (buttonswap, gwizard file merge, media
fix, citation fix, ...), and they all use the same helper scripts, templates
and test data. Those shared files live here, in one repo, so a fix is made
once and checked in once.

## How this repo is used

1. **The master copy lives here.** Every shared script, template and test
   file is edited and committed in `C:\gramps_dev\gramps_devutil`.
2. **Feature repos get copies.** The files are copied into each feature repo
   (for example `C:\gramps_dev\gramps_gwizard_mediafix_plugin`). There the
   copies are gitignored, so they never end up in a feature branch or a pull
   request to Gramps.
3. **Fixes flow back here.** If you change a copy inside a feature repo, the
   change is not under source control there. Move it back into
   gramps_devutil, commit it, and recopy it to the other feature repos.

Copy layout in a feature repo:

| From gramps_devutil       | To the feature repo         |
|---------------------------|-----------------------------|
| `package_addon.py`        | repo root                   |
| `check_banner.bash`       | repo root                   |
| `banner_template.txt`     | repo root                   |
| `environment_create.py`   | repo root (or run from here with `--target`) |
| `featuredocs/`            | `featuredocs/`              |
| `images/`                 | `images/` (gwizard repos)   |
| `gwizard_*.ged`, test-data README and image script | repo root (gwizard repos) |

## Contents

```
gramps_devutil/
├── README.md                        this file
├── package_addon.py                 builds an addon zip from a feature branch
├── addon_package.example.toml       annotated config for package_addon.py
├── check_banner.bash                checks GPL banners on changed .py files
├── banner_template.txt              the banner check_banner.bash expects
├── environment_create.py            sets up VS Code F5 debugging of Gramps
├── crib_notes.md                    git commands for the fork/branch workflow
├── final_checklist.txt              what to check before a feature is done
├── todo_list.txt                    running to-do list
├── gwizard_data_base.ged            gwizard test tree (import first)
├── gwizard_mergefrom.ged            gwizard test tree (merged into the base)
├── gwizard_testdata_README.txt      how to load and use the gwizard test data
├── make_gwizard_testdata_images.py  regenerates the test images (Pillow)
├── images/                          gwizard test media
│   ├── .gitignore
│   ├── FamilyTree/                  media base path for the test trees
│   └── Downloads/                   media outside the base path
└── featuredocs/                     wiki documentation pipeline
    ├── .gitignore
    ├── build_feature_docs.py        prepare AI prompt / build .mediawiki
    ├── create_example_wiki.bash     template per-feature driver script
    ├── scripts/
    │   ├── md_to_mediawiki.py       Markdown -> MediaWiki converter
    │   └── check_missing_images.py  audits screenshot references
    ├── templates/
    │   ├── header.mediawiki         addon infobox and intro
    │   └── footer.mediawiki         prerequisites, issues, categories
    └── devnotes/                    design notes and AI prompts
        ├── AdaptCodeForCorrectButtonSwap.md
        ├── GenerateFeatureWikiEntry.md
        ├── buttonswap/              button/dialog placement data and test plans
        └── funbase/                 AI prompts for branch syncing
```

## Requirements

- Windows with **MSYS2** (MINGW64 shell) for the bash scripts and the Gramps
  build. `environment_create.py` looks in `C:\Program Files\Msys64` first,
  then `C:\msys64`.
- **Python 3.11 or later** for `package_addon.py` (it uses `tomllib`).
- **git**, and a feature repo whose `origin` has the parent branch fetched.
- **xgettext** (GNU gettext) on `PATH` to build `po/template.pot`, or pass
  `--skip-pot`.
- **Pillow** (`pip install pillow`) only to regenerate the test images.

---

## package_addon.py: build a Gramps addon zip

Gramps features are developed inside the core Gramps tree, with modules spread
over `gramps/gen`, `gramps/gui` and `gramps/plugins`. An addon has to be one
flat folder. `package_addon.py` turns a feature branch into an installable
addon zip:

- Copies the addon's modules into one flat `<package>/` folder.
- Rewrites imports to suit the flat layout. For example,
  `from gramps.gui.gwizard.gwizardcompare import X` becomes
  `from gwizardcompare import X`. The rules come from each file's own path,
  so the config needs no regexes.
- Bundles unit tests, test helpers and optional test data into
  `<package>/tests/`, along with a `tests/__init__.py` that makes the flat
  modules importable.
- Generates `<package>/<package>.gpr.py` from the `[registration]` section.
- Generates `<package>/po/template.pot` with xgettext, the same way
  addons-source `make.py init` does.
- Normalizes newlines to LF, so the zip comes out identical whatever the
  checkout's line-ending setting.
- Warns about:
  - lines that still point into the core tree after rewriting;
  - files changed on the branch that no config bundles, provides, excludes
    or ignores.

### Setup

1. Copy `package_addon.py` into the feature repo root, unchanged. Nothing
   project-specific goes in it.
2. Copy `addon_package.example.toml` there as `addon_package.toml`, then fill
   it in. A repo with more than one addon gets one file per addon (for
   example `addon_package_mediafix.toml`), and you choose one with `--config`.

Key config sections (all are documented in the example file):

| Section             | Purpose |
|---------------------|---------|
| `package`, `zip_name` | Folder name in the zip and the output file name (`{package}_v{version}.zip` by default) |
| `[registration]`    | Fields for the generated `.gpr.py`: id, name, description, fname, toolclass, authors, Gramps version range, ... |
| `[files]`           | `modules`, `tests`, `test_helpers`, `exclude`, `keep_unrewritten`, and an optional `[files.test_data]` tree |
| `[[dependencies]]`  | Other addons this one needs at run time. Their modules are flattened but not bundled |
| `[check]`           | `base` branch to compare against (detected if unset) and `ignore` globs for the changed-files check |
| `[translations]`    | xgettext keywords |

Globs: `*` and `?` match within one folder, and `**` spans folders.
`__init__.py` files are never bundled.

### Usage

```bash
python package_addon.py 0.1.0                       # build with version 0.1.0
python package_addon.py --version 0.1.0             # same
python package_addon.py --config addon_package_mediafix.toml 0.1.0
python package_addon.py --check                     # report only, write no zip
python package_addon.py 0.1.0 --skip-pot            # no po/template.pot
python package_addon.py 0.1.0 -o dist/MyAddon.zip   # custom output path
python package_addon.py 0.1.0 --log package_output.txt -v
```

The default version is `0.0.1`. By default the zip is written to the repo
root.

---

## featuredocs/: Gramps wiki pages for a feature

A two-stage pipeline that produces a Gramps Wiki addon page for a feature
branch. It documents only what the branch itself adds. See
`featuredocs/devnotes/GenerateFeatureWikiEntry.md` for the reasoning.

### Stage 1: prepare (`--prepare`)

Reads `changed_files.txt` and the isolated `git diff <parent>...HEAD` for
those files, plus any `.gpr.py` registration file, and writes:

- `featuredocs/<feature>_prompt.txt`: a ready-to-paste prompt for an AI
  assistant (Cline, ChatGPT, Claude). It includes the documentation rules,
  the screenshot naming convention and the screenshots already in
  `featuredocs/images/`.
- `featuredocs/README_<feature>.md`: a starter README, created only if one
  doesn't exist yet.

Paste the prompt into the AI assistant and have it fill in
`README_<feature>.md`. If the output is wrong, fix the automation (the
prompt builder or the templates), not just the generated README.

### Stage 2: build (`--build`)

- Converts `README_<feature>.md` to MediaWiki markup with
  `scripts/md_to_mediawiki.py`.
- Wraps it with `templates/header.mediawiki` and
  `templates/footer.mediawiki`, replacing `<PluginName>` with the feature
  name and `<Plugin Display Name>` with the display name.
- Writes `featuredocs/<feature>.mediawiki`.
- Runs `scripts/check_missing_images.py` against `featuredocs/images/`,
  prints the audit and saves it to `featuredocs/<feature>_image_audit.txt`.
  The exit code is 0 only when every referenced screenshot exists.

### Usage

The simplest way is a per-feature driver script.
`featuredocs/create_example_wiki.bash` is a template for one: it generates
`changed_files.txt` from `origin/<parent>...HEAD`, runs both stages, and
deletes `changed_files.txt` afterwards if it created it.

To set one up for a feature, in the feature repo:

1. Copy the template, replacing `example` with the feature's slug:

   ```bash
   cp featuredocs/create_example_wiki.bash featuredocs/create_my_feature_wiki.bash
   ```

2. Edit the three values at the top of the copy:

   ```bash
   FEATURE="my_feature"                 # slug used in every generated file name
   PLUGIN_DISPLAY_NAME="My Feature"     # name shown on the wiki page
   PARENT_BRANCH="functionality_base"   # branch the feature started from
   ```

3. Commit the copy in the feature repo. Only the template is gitignored
   there, so each feature keeps its own script.
4. Run it from the repo root:

   ```bash
   ./featuredocs/create_my_feature_wiki.bash
   ```

5. Paste `featuredocs/my_feature_prompt.txt` into your AI assistant, save
   its answer as `featuredocs/README_my_feature.md`, take the screenshots it
   asks for, and run the script again to rebuild the `.mediawiki` page.

To run the stages directly instead:

```bash
git diff --name-only origin/functionality_base...HEAD > changed_files.txt
python featuredocs/build_feature_docs.py my_feature \
    --parent functionality_base --filelist changed_files.txt --prepare
python featuredocs/build_feature_docs.py my_feature \
    --plugin-display-name "My Feature" --build
```

`--parent` defaults to `functionality_base`, and `--filelist` defaults to
`./changed_files.txt`.

The helper scripts also work on their own:

```bash
python featuredocs/scripts/md_to_mediawiki.py featuredocs/README_X.md \
    --header featuredocs/templates/header.mediawiki \
    --footer featuredocs/templates/footer.mediawiki
python featuredocs/scripts/md_to_mediawiki.py featuredocs/X.mediawiki --check-only
python featuredocs/scripts/check_missing_images.py featuredocs/X.mediawiki \
    --images-dir featuredocs/images
```

### Screenshots

Screenshots go in `featuredocs/images/` in the feature repo and are named
`<feature>-<short-name>.png`. The header template always shows
`<feature>-main.png`, the main window as it first opens. Reference each
image once in the README as
`![Caption](images/<feature>-<short-name>.png)`.

### featuredocs/devnotes/

- `AdaptCodeForCorrectButtonSwap.md`: an AI prompt for platform-native
  dialog button order (Windows `OK / Cancel` vs. GTK `Cancel / OK`).
- `GenerateFeatureWikiEntry.md`: the design behind the wiki pipeline.
- `buttonswap/`: button and dialog placement CSVs for each buttonswap commit
  (Linux and Windows), the scripts that generate them, the test plan and
  verification instructions.
- `funbase/`: AI prompts for syncing the fork with upstream, bringing in a
  lesser branch, and updating a branch from its parent.

---

## check_banner.bash: GPL banner check

Checks that every `.py` file changed on the branch starts with the exact
banner in `banner_template.txt` (the Gramps GPL v2+ header). Line endings are
normalized first, so CRLF and LF files both pass.

```bash
./check_banner.bash
CHANGED_FILE=my_list.txt ./check_banner.bash   # use a different list file
```

- It always regenerates the list from
  `git diff --name-only origin/functionality_base...HEAD`, keeping only
  `.py` files.
- It names untracked `.py` files but doesn't check them.
- It deletes the list file afterwards if it created it.
- Exit code: 0 if every banner matches, 1 if any is missing or different.

Run it from the repo root, with `banner_template.txt` beside it.

---

## environment_create.py: VS Code debugging of Gramps from source

Sets up a Gramps checkout so you can press F5 in VS Code:

- Writes `.vscode/launch.json`, a "Debug Gramps outside MSYS2"
  configuration using the MSYS2 MINGW64 Python, with `GRAMPS_RESOURCES`
  pointing at `build/share` and the MSYS2 `bin` folders on `PATH`.
- Writes `.vscode/settings.json`, enabling unittest discovery for
  `*test*.py`.
- If `build/share/gramps/authors.xml` is missing, it builds the resources
  with `python -m build --wheel --no-isolation`, installing the `build`
  module first if needed.

```bash
python environment_create.py                     # current folder, home MSYS2 root
python environment_create.py work                # use C:\msys64 (work machine)
python environment_create.py --target C:\gramps_dev\gramps_buttonswap
python environment_create.py --no-build          # only write .vscode
```

---

## GWizard test data

A pair of GEDCOM trees and matching media, made to exercise the GWizard
tools (File Merge, Media Fix, Citation Fix). They cover name variants
(Mac/Mc, von prefixes, Schmid/Schmidt), date quality, duplicate GEDCOM IDs,
missing files, an unused file and a deliberately corrupt image.

- `gwizard_data_base.ged`: the tree you import first.
- `gwizard_mergefrom.ged`: the tree you merge into it.
- `images/FamilyTree/`: the media base path. Set it in Gramps before
  importing.
- `images/Downloads/`: media referenced by absolute path, outside the base
  path.
- `make_gwizard_testdata_images.py [IMAGES_DIR]`: regenerates both image
  folders. It defaults to
  `C:\gramps_dev\gramps_gwizard_mediafix_plugin\images`.

`gwizard_testdata_README.txt` has the full loading steps and the expected
match results, person by person.

---

## .gitignore files

The `.gitignore` files in `featuredocs/` and `images/` are written for the
**feature repos**. Each one lists the shared files by name, including itself,
so the copies stay out of feature-branch history. In gramps_devutil those
files are already tracked, so the lists have no effect here. A new file added
here can be committed with a plain `git add`.

`featuredocs/.gitignore` also ignores the pipeline's generated output
(`*_prompt.txt`, `*.mediawiki`, `*_image_audit.txt`, `changed_files.txt`)
and Python bytecode. It does **not** ignore `README_<feature>.md` or
`featuredocs/images/`, because those belong to the feature and are committed
in its repo.

**When you add a shared file to `featuredocs/` or `images/`, add its name to
that folder's `.gitignore` too.** Otherwise it will show up as untracked in
every feature repo it's copied into.

---

## Workflow notes

- **Branches:** feature branches start from `functionality_base` in the fork.
  Finished features are squashed and merged into the GoatGramps integration
  branch, `goatgramps/core`. `crib_notes.md` has the git commands: syncing
  with upstream, rebasing a feature onto `functionality_base`, squashing,
  checking for conflicts, renaming branches and fixing line endings.
- **Before calling a feature done:** work through `final_checklist.txt`:
  - `black .`
  - file banners (`check_banner.bash`)
  - `gw_` naming for gwizard functions
  - tests
  - buttonswap compliance
  - `.gitattributes` conformance
  - up to date with upstream
  - each feature has its own notes, package config and
    `featuredocs/README_<feature>.md` with screenshots
- **Diff base:** `check_banner.bash`, the driver script and
  `build_feature_docs.py` all compare against `functionality_base`. For a
  feature started from another branch, pass `--parent` (or set
  `PARENT_BRANCH`) to match it.

## License

The scripts carry the Gramps GPL banner: GNU General Public License,
version 2 or later. Copyright (C) 2026 Kevin White.

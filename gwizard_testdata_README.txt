GWizard test data: gwizard_data_base.ged and gwizard_mergefrom.ged
==============================================================

Files
-----
The master copies live in gramps_devutil. Copy them into the root of each
feature repo that uses them (for example gramps_gwizard_filemerge_plugin or
gramps_gwizard_mediafix_plugin), keeping the images\ folder layout.

C:\gramps_dev\gramps_devutil\
    gwizard_data_base.ged             the tree you import first
    gwizard_mergefrom.ged             the file you merge into it with GWizard File Merge
    make_gwizard_testdata_images.py   regenerates the images (needs Pillow)
    gwizard_testdata_README.txt       this file
C:\gramps_dev\gramps_devutil\images\
    FamilyTree\   the media base path. Holds the files the GEDCOMs reference
                  by relative path, plus one file no record uses and one
                  deliberately corrupt file.
    Downloads\    files referenced by absolute path, outside the base path.

How to load them
----------------
1. Create a new, empty family tree and open it.
2. BEFORE importing, set the media base path to the FamilyTree folder in the
   feature repo you are testing, for example
       C:\gramps_dev\gramps_gwizard_mediafix_plugin\images\FamilyTree
   Don't point it at the gramps_devutil copy: Media Fix renames and moves
   these files, and the gramps_devutil copies are the tracked originals.
   (Edit > Preferences > General > "Base path for relative media paths").
   Gramps' GEDCOM import looks for each media file there. If the base path is
   not set first, every media record gets a "Could not import ..." note.
   Keep the images in C:\gramps_dev\gramps_gwizard_mediafix_plugin\images,
   not elsewhere (for example inside the Gramps source tree): the absolute
   paths in the GEDCOMs (Clara von Holt's portrait, Downloads\scan0042.jpg,
   and "Downloads\Ohio death cert Johann Schmid.jpg" in merge_from) point
   there. When Gramps can't find an absolute path on import, it drops the
   drive letter, so the record ends up missing with a path such as
   \gramps_dev\gramps_gwizard_mediafix_plugin\images\Downloads\scan0042.jpg.
   Media Fix moves files out of images\ when it consolidates, so run
   make_gwizard_testdata_images.py (it writes to that folder by default)
   before each test run to put them back.
3. Import gwizard_data_base.ged.
4. Run Media Fix and Citation Fix on it if you are testing those (see below),
   or go straight to Tools > Family Tree Processing > GWizard File Merge and
   pick gwizard_mergefrom.ged.

Gramps 6.1 gives imported people IDs like I00001 (the "I%05d" default). The
"good" media files are named for those IDs. With other ID formats in
Preferences, those files will show as non-standard names too.

Both files reuse the same GEDCOM IDs (@I1@, @S1@, @M1@...) for different
records, to exercise the handle/ID collision handling.


People to merge (merge_from -> base)
------------------------------------
"Matches today" is what the compare window's matcher does with the current
gwizard_filemerge code.

  Merge-from person          Base person                   Tests                                   Matches today
  -------------------------  ----------------------------  --------------------------------------  -------------
  Angus McDonald  1890       Angus MacDonald  1890         Mac vs Mc; adds a 1930 residence;       yes
                                                           empty Burial on both sides
  Mary Mac Lean   abt 1892   Mary MacLean  1892            Mac with a space; "abt" vs exact date;  yes
                                                           death place full of extra spaces
  Duncan Mc Donald abt 1914  Duncan MacDonald 2 Feb 1914   Mc with a space; date quality           yes
  Margaret McDonald 1916     (none)                        Add as New, linked into the             no (correct)
                                                           MacDonald family by birth order
  (none)                     Ewan MacDonald 1918           base-only child                         -
  Friedrich Vonsteuben 1855  Friedrich von Steuben 1855    von as a prefix vs run together         NO (gap)
  Clara vonHolt 1860         Clara von Holt 1860           von with no space, lower case           NO (gap)
  Johann Schmid 1850         Johann Schmidt 1850           Schmid vs Schmidt; adds a death day     yes
  John Schmidt 1878          John Smith 1878               Smith vs Schmidt; must NOT pick the     yes
                                                           other John Smith (born 1925)
  Heinrich Schmidt 1880      (none)                        Add as New, sibling placed by birth     no (correct)
  Anna Bauer 1853            Anna Bauer 1853               exact match                             yes
  Patrick OBrien 1870        Patrick O'Brien 1870          apostrophe vs none                      yes
  Bill Turner 1900           William "Bill" Turner 1900    nickname vs given name                  NO (gap)
  Elizabeth Turner 1902      Elizabeth Harris 1902         married name primary vs maiden          NO (gap)
                             (alt name Elizabeth Turner)   name primary
  Thomas Devault 1868        Thomas Devault Jr. 1868       must pick Jr., not Sr. (1840)           yes
  Zoe Mueller 1885           Zoë Müller 1885               accents and ue vs ü                     yes (weakly)
  (none)                     Hans Schmid 1802              decoy that must not match               -

The four NO (gap) rows are good cases for matching by hand.

Family data:
  * MacDonald family: base has an empty Engagement; merge_from has an extra
    empty Marriage. Children are listed in a different order.
  * Schmidt family: merge_from lists Heinrich before John.
  * Turner family: the marriage citation is only in merge_from.

Notes: base Angus has a whitespace-only note, merge_from Mary has a blank
two-line note. Neither should be listed in the merge dialog.


Citation Fix conditions
-----------------------
Base (gwizard_data_base.ged):
  Unpack Conflated Source
    S3  "Ancestry.com - 1920 United States Federal Census, page 7 line 22"
    S4  "<i>Newspapers.com</i> Obituary Index"               (markup)
    S5  "familysearch.org"                                     (bare website)
    S6  "“Pennsylvania, Church Records, 1680-1950,” database, FamilySearch"
    S7  "Find a Grave Memorial ID 45678 (Repository: Find a Grave, Source: Find a Grave Index)"
        (labelled group; currently NOT offered, see Findings)
  Repository Consolidate   R1 "Ancestry.com" and R3 "ancestry" are duplicates;
                           R4 has an address and an import-debris note
  Fix Repositories         sources with no repository (S3-S8)
  Fix Sources              S1 "1900 United States Federal Census" vs
                           S9 "1900 U.S. Federal Census" (duplicates)
  Unpack Conflated Citation
    Angus death:      page is a URL plus "accessed 3 January 2020"
    Friedrich census: page has an ark URL and "accessed 14 February 2018"
    Ewan birth:       no page; FamilySearch-style citation is in the note
  Citation Attributes      citations with and without QUAY or keywords
  Link Citation Media
    S10 has its media at source level (unpack to the citation)
    Johann's 1900 census image is in the event gallery (promote to citation)
    the marriage record is in the marriage event gallery (currently NOT
        offered, see Findings)
    Mary's obituary citation links a non-standard file (obit_maclean_1970.jpg)
  Fix Notes
    "Records not imported into REPO..." debris note on R4
    "Birth type: natural" review note on Mary
    bare Find a Grave URL note on Patrick's burial citation

Merge from (gwizard_mergefrom.ged):
  Unpack Conflated Source  "FamilySearch.org - Ohio Death Certificates, 1908-1953; cert 4521"
  Unpack Conflated Citation  Angus residence and Friedrich emigration pages
                             with URLs and access dates
  Fix Sources              S2 "1900 United States Federal Census" and
                           S7 "1930 United States Federal Census", both at
                           Ancestry.com (currently wrongly merged, see Findings)
  Fix Notes                "Tag recognized but not supported" debris,
                           "passed away exactly on his ..." review note,
                           bare URL note
  Source matching on merge  S1 Scotland Births and S2 1900 Census match base
                            sources (same title, author and publication).
                            The other five come in as new, including "Find a
                            Grave Index": base S7 still has its conflated
                            title, so unpack it first if you want those two
                            to line up.


Media Fix conditions (with the base path set as above)
------------------------------------------------------
Base:
  good (standard name, relative, file exists)
      Angus birth certificate and 1920 census (on citations)
      Patrick grave marker (on a citation)
      marriage record (on the marriage event)
      Johann 1900 census (on the census event)
      Johann death certificate (on source S10)
  missing file          Duncan_MacDonald_school_photo_1925.jpg
  absolute, inside base Clara von Holt portrait
  absolute, outside     Downloads\scan0042.jpg (also a non-standard name)
  non-standard names    "Johann Schmidt grave.JPG", mary_maclean_portrait.jpg,
                        obit_maclean_1970.jpg (on a citation), and others
  duplicate file        family_reunion_1950.jpg used by two media records
  unreferenced record   unknown_woman_1900.jpg (no links)
  unreferenced file     orphan_scan_0007.png (on disk, no record)
  name mismatch         "O'Brien, Patrick - Obituary, 1931" attached to Angus
                        (different person)
                        "Duvault, Thomas - Baptism record, 1868" attached to
                        Thomas Devault Jr. (spelling variant)
  stale import note     mary_maclean_portrait.jpg (an unsupported _CUTOUT tag)
  corrupt file          broken_scan.jpg (JPEG header followed by junk)

Merge from:
  good                  Angus McDonald birth certificate (on a citation),
                        Bill Turner portrait
  missing, absolute     C:\Users\GWizardTester\Pictures\obrien_grave_1931.jpg
                        (on a citation)
  absolute, outside     "Downloads\Ohio death cert Johann Schmid.jpg"
                        (on a citation, non-standard name)


What the tools report today (checked against the current code)
--------------------------------------------------------------
Base, Media Fix report: 18 media, 1 missing, 2 absolute, 1 outside the base
path, 11 non-standard names, 3 unreferenced files (two belong to merge_from),
1 unreferenced record, 2 name mismatches, 1 duplicate file, 1 stale import
note.

Base, Citation Fix "Accept all hints": unpacks 4 sources and 3 citations,
merges 1 repository, links 2 media to citations, fixes 5 notes.
Merge from: unpacks 1 source and 2 citations, merges 1 source (the wrong
one, see below), fixes 3 notes.


Findings in Citation Fix that this data exposes
-----------------------------------------------
1. A title that is only repository plus citation, with the source in a
   labelled group, is never offered for unpacking (base S7).
   split_conflated_title() returns None because nothing is left for the
   title. It could use the labelled Source value ("Find a Grave Index").
2. Cutting repository mentions can eat the source title: "Find a Grave
   Index; Memorial ID 45678 (Repository: Find a Grave)" becomes "Index".
3. Citation text separated by commas stays in the title: base S3 unpacks to
   "1920 United States Federal Census, page 7 line 22". A comma-separated
   "..., cert 4521" makes the whole title count as citation text, so it is
   not offered at all.
4. Link Citation Media takes a citation's year from the source title's date
   range ("Scotland, Marriages, 1561-1910" gives 1561) rather than the page
   ("Inverness, 1912, entry 33"). The 1912 marriage record then counts as a
   year conflict and is not offered.
5. After a split, citation-style quotes stay in the new title:
   "“Pennsylvania, Church Records, 1680-1950,” database".
6. Fix Sources merges different collections that share a repository:
   suggest_source_merge_target() skips same_collection_titles() when the
   repositories match and title similarity is 70% or more. In merge_from,
   "1900 United States Federal Census" was merged into "1930 United States
   Federal Census" (both Ancestry.com).

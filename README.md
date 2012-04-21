journal.py
==========

NAME
----

`journal.py` - a command line tool for viewing and maintaining a journal

DESCRIPTION
-----------

`journal.py` is a tool to archive, search through, calculate statistics
on, verify, and create tags for a plain text journal. It expects journal
files to have the extension `.journal` and the contents to conform to a
(loose) syntax. Entries start with unindented dates in the form `YYYY-MM-DD`,
optionally followed by "`, WEEKDAY`" (without quotes).  Entry contents
starts on the next line, indented by at least one tab.  Each line is a
paragraph; consequtive lines must either be indented by the same level,
by one more level, or by arbritrarily fewer levels (down to one) than
the previous line. An empty line is required between entries.  For
example:

    2012-03-29, Thursday
        This is the first paragraph.
        This is the second paragraph.
            Lines can be indented one level further
                for each line,
        but can drop back arbitrarily far
    
    2012-03-30, Friday
        The next entry.

OPTIONS
-------

    usage: journal.py <operation> [options] [TERM ...]

    positional arguments:
      TERM                  pattern which must exist in entries

    optional arguments:
      -h, --help            show this help message and exit

    OPERATIONS:
      -A                    archive to datetimed tarball
      -C                    count words and entries
      -G                    graph entry references in DOT
      -L                    list entry dates
      -S                    show entries
      -T                    create tags file
      -V                    verify journal sanity

    INPUT OPTIONS:
      --directory DIRECTORY
                            use journal files in directory
      --ignore IGNORES      ignore specified files

    OUTPUT OPTIONS:
      -d DATE_RANGE         only use entries in range
      -i                    ignore ignore case
      -n NUM_RESULTS        max number of results
      -r                    reverse chronological order

BUGS
----

Report bugs or submit pull requests at <https://github.com/justinnhli/journal>.

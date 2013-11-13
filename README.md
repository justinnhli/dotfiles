journal.py
==========

NAME
----

`journal.py` - a command line tool for viewing and maintaining a journal

DESCRIPTION
-----------

`journal.py` is a tool to archive, search through, calculate statistics on,
verify, and create tags for a plain text journal. It expects journal files to
have the extension `.journal` and the contents to conform to a (loose) syntax.
Entries start with unindented dates in the form `YYYY-MM-DD`, optionally
followed by `, WEEKDAY`. Entry contents begins on the next line, one paragraph
per line, each indented by at least one tab. Consecutive lines must either be
indented by the same level, by one more level, or by arbitrarily fewer levels
(down to one) than the previous line. An empty line is required between entries.

For example:

    1970-01-01, Thursday
        This is the first paragraph.
        This is the second paragraph.
			An indented third paragraph.
				A further-intended fourth paragraph.
		An unindented fifth paragraph.
    
    1970-01-02, Friday
        The next entry.

OPTIONS
-------

	usage: journal.py <operation> [options] [TERM ...]

	a command line tool for viewing and maintaining a journal

	positional arguments:
	  TERM                  pattern which must exist in entries

	optional arguments:
	  -h, --help            show this help message and exit

	OPERATIONS:
	  -A                    archive to datetimed tarball
	  -C                    count words and entries
	  -G                    graph entry references in DOT
	  -L                    list entry dates
	  -S                    show entry contents
	  -U                    update tags and cache file
	  -V                    verify journal sanity

	INPUT OPTIONS:
	  --directory DIRECTORY
							use journal files in directory
	  --ignore IGNORES      ignore specified file

	FILTER OPTIONS (APPLIES TO -[CGLS]):
	  -d DATE_RANGE         only use entries in range
	  -i                    ignore case-insensitivity
	  -n NUM_RESULTS        max number of results

	OUTPUT OPTIONS:
	  -r                    reverse chronological order

	OPERATION-SPECIFIC OPTIONS:
	  --no-log              [S] do not log search
	  --unit {year,month,date}
							[C] tabulation unit

BUGS
----

Report bugs or submit pull requests at <https://github.com/justinnhli/journal>.

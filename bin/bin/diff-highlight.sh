#!/bin/bash

# find the path to git
git_path="$(which git)"
# if git is a symbolic link, find the real path
# this should only happen on MacOS
if [ -L "$git_path" ]; then
	# if the path is not an absolute path
	if ! [[ "$git_path" =~ ^/ ]]; then
		# create an absolute path by prepending with its parent
		git_path="$(dirname "$git_path")/$(readlink "$git_path")"
	fi
	# normalize the absolute path
	git_path="$(readlink -f "$git_path")"
fi
# go up two directories
git_path="$(dirname "$(dirname "$git_path")")"
# find the first share/git* path, usually git on Linux and git-core on MacOS
git_path="$(find "$git_path/share" -maxdepth 1 -type d -name 'git*' | sort | head -n 1)"
# find the diff-highlight program
diff_highlight_path="$(find "$git_path" -type f -name 'diff-highlight')"
# if the file exists and is executable
if [ -x "$diff_highlight_path" ]; then
	"$diff_highlight_path" | less
else
	less
fi

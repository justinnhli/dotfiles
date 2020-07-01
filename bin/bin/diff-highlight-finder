#!/bin/bash

git_path="$(which git)"
if [ -L "$git_path" ]; then
    git_path="$(dirname "$git_path")/$(readlink "$git_path")"
fi
git_dir_path="$(echo "$git_path" | sed 's#bin#share#; s#git/.*#git#;')"
diff_highlight_path="$(find "$git_dir_path" -type f -name 'diff-highlight')"
if [ -z "$diff_highlight_path" ]; then
    cat
else
    "$diff_highlight_path"
fi

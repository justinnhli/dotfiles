#!/bin/bash

update_dot_files() {
	if [ ! -d "$HOME/bin" ]; then
		mkdir "$HOME/bin"
	fi
	curl -L 'https://raw.githubusercontent.com/justinnhli/dotfiles/master/.bashrc' > "$HOME/.bashrc"
	curl -L 'https://www.dropbox.com/s/9ulktr6czt5tsfh/sshh' > "$HOME/bin/sshh"
	curl -L 'https://raw.githubusercontent.com/justinnhli/dotfiles/master/.nvim/nvimrc' > "$HOME/.vimrc"
	chmod 744 "$HOME/bin/sshh"
}

# convenience variable
uname="$(uname)"

# prompt
prompt_command_fn() {
	# right before prompting for the next command, save the previous command in a file.
	if [ -e ~/Dropbox/documents/shell_history ]; then
		echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)	$(hostname)	$PWD	$(history 1 | sed 's/^ *[0-9 :-]* //; s/ *$//;')" >> ~/Dropbox/documents/shell_history
	fi
	echo -ne "\033]0;${PWD/$HOME/~}\007"
}
PS1='[\u@\h \W]\$ '
PROMPT_COMMAND=prompt_command_fn

# paths
export PATH="$HOME/bin:$HOME/.cabal/bin:/usr/texbin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"
export PYTHONPATH="$HOME/bin"
if [ -d "$HOME/projects/" ]; then
	for dir in $(find "$HOME/projects/" -maxdepth 2 -type f -perm -100 -exec dirname {} ';' | sort | uniq); do
		export PATH="$dir:$PATH"
	done
	for dir in $(find "$HOME/projects/" -maxdepth 2 -type f -name '*.py' -exec dirname {} ';' | sort | uniq); do
		export PYTHONPATH="$dir:$PYTHONPATH"
	done
fi
if [ -d "$HOME/git/" ]; then
	for dir in $(find "$HOME/git/" -maxdepth 2 -type f -perm -100 -exec dirname {} ';' | sort | uniq); do
		export PATH="$dir:$PATH"
	done
	for dir in $(find "$HOME/git/" -maxdepth 2 -type f -name '*.py' -exec dirname {} ';' | sort | uniq); do
		export PYTHONPATH="$dir:$PYTHONPATH"
	done
fi

# environment
if which nvim &>/dev/null; then
	export EDITOR=nvim
	export VISUAL=nvim
	export MANPAGER="/bin/sh -c \"col -b | nvim -c 'set ft=man ts=8 nomod nolist nonu noma' -\""
fi
export HISTSIZE=10000
export HISTCONTROL=ignoredups
export PYTHONIOENCODING="utf-8"

# soar variables
case "$uname" in
"Linux")
	if uname -v | grep Ubuntu &>/dev/null; then
		if [ -d "/usr/lib/jvm/default-java" ]; then
			export JAVA_HOME="/usr/lib/jvm/default-java"
		fi
	elif [ -d "/usr/lib/jvm/java-7-openjdk" ]; then
		export JAVA_HOME="/usr/lib/jvm/java-7-openjdk"
	fi
	export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:$HOME/Soar/out";;
"Darwin")
	export DYLD_LIBRARY_PATH="$DYLD_LIBRARY_PATH:$HOME/Soar/out"
esac
export PYTHONPATH="$HOME/Soar/out:$PYTHONPATH"

export PATH="$(echo "$PATH" | sed 's#//#/#g')"
export PYTHONPATH="$(echo "$PYTHONPATH" | sed 's#//#/#g')"

# aliases
alias rm='rm -i'
alias cp='cp -i'
alias mv='mv -i'
alias grep='grep --color=auto'
alias jrnl='journal.py --ignore ~/journal/notes.journal --ignore ~/journal/ponderings.journal'
alias flake8='flake8 --ignore=E501'
alias pylint='pylint --indent-string="    " --disable=invalid-name,missing-docstring,old-style-class,star-args,line-too-long,bad-builtin,bad-continuation --reports=n'
alias soar='~/Soar/out/testcli'
alias valgrind='valgrind --dsymutil=yes --leak-check=yes --track-origins=yes'
if which python3 &>/dev/null; then
	alias scons="scons --python=$(which python3)"
fi
if which nvim &>/dev/null; then
	alias vino="nvim ~/journal/notes.journal"
	alias vi='nvim'
	alias vim='nvim'
fi
case "$uname" in
	"Linux")
		alias ls='ls --color=auto'
		alias open='xdg-open'
		alias vncserver='vncserver -depth 8'
		alias x11vnc='x11vnc -display :0 -xkb -usepw -noxdamage';;
	"Darwin")
		alias ls='ls -G';;
esac

# redraw on window size change
shopt -s checkwinsize

# disable output stop keyboard shortcut (so <C-s> can be mapped in vim)
stty stop '' -ixoff

# make C-w stop at slashes
stty werase undef
bind '"\C-w": unix-filename-rubout'

#!/bin/sh

update_dot_files() {
	if [ ! -d "$HOME/bin" ]; then
		mkdir "$HOME/bin"
	fi
	curl -L 'https://raw.githubusercontent.com/justinnhli/dotfiles/master/bash/.bashrc' > "$HOME/.bashrc"
	curl -L 'https://www.dropbox.com/s/9ulktr6czt5tsfh/sshh' > "$HOME/bin/sshh"
	curl -L 'https://raw.githubusercontent.com/justinnhli/dotfiles/master/neovim/.nvim/nvimrc' > "$HOME/.vimrc"
	chmod 744 "$HOME/bin/sshh"
}

# bashrc convenience variables
SHELL_HISTORY_FILE="~/Dropbox/personal/logs/shell_history"
SHELLSCRAPE="~/.bash_completion.d/shellscrape.py"

# prompt
prompt_command_fn() {
	# right before prompting for the next command, save the previous command in a file.
	echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)	$(hostname)	$PWD	$(history 1 | sed 's/^ *[0-9 -]* //; s/ *$//;')" >> "$SHELL_HISTORY_FILE"
}
PS1='[\u@\h \W]\$ '
if [ -e "$SHELL_HISTORY_FILE" ]; then
	PROMPT_COMMAND=prompt_command_fn
fi

# paths
export PATH="$HOME/bin:$HOME/neovim/build/bin:/usr/local/heroku/bin:/opt/pdflabs/pdftk/bin:$HOME/.cabal/bin:$PATH"
export PYTHONPATH="$HOME/bin"
for master_dir in "$HOME/projects/" "$HOME/git/"; do
	if [ -d "$master_dir" ]; then
		for dir in $(find "$master_dir" -maxdepth 2 -type f -perm -100 -exec dirname {} ';' | sort -r | uniq); do
			export PATH="$dir:$PATH"
		done
		for dir in $(find "$master_dir" -maxdepth 2 -type f -name '*.py' -exec dirname {} ';' | sort -r | uniq); do
			if [ ! -e "$dir/__init__.py" ]; then
				export PYTHONPATH="$dir:$PYTHONPATH"
			fi
		done
	fi
done
export PYTHONPATH="$HOME/git:$PYTHONPATH"

# environment
if which nvim >/dev/null 2>&1; then
	if [ -d "$HOME/neovim/runtime" ]; then
		export VIM="$HOME/neovim/runtime"
	fi
	export EDITOR='nvim'
else
	export EDITOR=vim
fi
export VISUAL=$EDITOR
export MANPAGER="/bin/sh -c \"col -b | $EDITOR -c 'set ft=man ts=8 nomod nolist nonu noma' -\""
export HISTSIZE=10000
export HISTCONTROL=ignoredups
export PYTHONIOENCODING="utf-8"

# soar variables
case "$(uname)" in
"Linux")
	if uname -v | grep Ubuntu 2>&1 >/dev/null; then
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

# clean up the paths
export PATH="$(echo "$PATH" | sed 's#//#/#g')"
export PYTHONPATH="$(echo "$PYTHONPATH" | sed 's#//#/#g')"

# aliases
alias rm='rm -i'
alias cp='cp -i'
alias mv='mv -i'
alias bc='bc -l'
alias flake8='flake8 --ignore=E501'
alias grep='grep --color=auto'
alias jrnl="journal.py --ignore '$(ls -m ~/journal/*.journal 2>/dev/null | sed 's/ //g')'"
alias pacaur='pacaur --domain aur4.archlinux.org'
alias pylint='pylint --indent-string="    " --disable=invalid-name,missing-docstring,old-style-class,star-args,line-too-long,bad-builtin,bad-continuation --reports=n'
alias soar='~/Soar/out/testcli'
alias valgrind='valgrind --dsymutil=yes --leak-check=yes --track-origins=yes'
if which python3 >/dev/null 2>&1; then
	alias scons="scons --python=$(which python3)"
fi
alias vi="$VISUAL"
alias vim="$VISUAL"
alias vino="$VISUAL ~/journal/notes.journal"
case "$(uname)" in
	"Linux")
		alias ls='ls --color=auto --time-style=long-iso'
		alias open='xdg-open'
		alias vncserver='vncserver -depth 8'
		alias x11vnc='x11vnc -display :0 -xkb -usepw -noxdamage';;
	"Darwin")
		alias ls='ls -G';;
esac
if [ "$NVIM_LISTEN_ADDRESS" != "" ]; then
	alias :="$(which nvimcmd)"
fi

# completion
_generic_completion()
{
	# FIXME only do this if we're looking for options
	if [ "${COMP_WORDS[COMP_CWORD]:0:1}" == "-" ]; then
		# build up the context
		local context="${COMP_WORDS[0]}"
		if [ $COMP_CWORD -gt 0 ]; then
			for i in $(seq $COMP_CWORD); do
			context="$context ${COMP_WORDS[i]}"
			done
		fi
		# call script
		COMPREPLY=( $(~/.bash_completion.d/shellscrape.py "$context") )
	fi
}

if [ -f ~/.bash_completion.d/shellscrape.py ]; then
	for program in $(~/.bash_completion.d/shellscrape.py); do
		if type "$program" >/dev/null 2>&1; then
			complete -o default -F _generic_completion "$program"
		fi
	done
fi

# automatically correct minor spelling errors with `cd`
shopt -s cdspell
# redraw on window size change
shopt -s checkwinsize
# save multi-line commands in the same history entry
shopt -s cmdhist
# allow '**' to match subdirectories
if [ "$(( echo $BASH_VERSION && echo 4 ) | sort -n | tail -n 1 )" != "4" ]; then
	shopt -s globstar
fi

# disable output stop keyboard shortcut (so <C-s> can be mapped in vim)
stty stop '' -ixoff

# make C-w stop at slashes
stty werase undef
bind '"\C-w": unix-filename-rubout'

# fix terminfo
export TERM=xterm-256color
terminfo="$(mktemp /tmp/$TERM-terminfo.XXXXXX)"
infocmp $TERM | sed 's/kbs=^[hH]/kbs=\\177/' > "$terminfo"
tic "$terminfo"
rm -f "$terminfo"

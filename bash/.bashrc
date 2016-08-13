#!/bin/sh

update_dot_files() {
	curl -L 'https://raw.githubusercontent.com/justinnhli/dotfiles/master/bash/.bash_profile' > "$HOME/.bash_profile"
	curl -L 'https://raw.githubusercontent.com/justinnhli/dotfiles/master/bash/.bashrc' > "$HOME/.bashrc"
	curl -L 'https://raw.githubusercontent.com/justinnhli/dotfiles/master/neovim/.config/nvim/init.vim' > "$HOME/.vimrc"
}

# paths
if [ -d "/usr/local/Cellar" ]; then
	export PATH="$(find /usr/local/Cellar -name bin | sort -f | tr '\n' ':')$PATH"
fi
if [ -d "$HOME/git" ]; then
	export PATH="$(find "$HOME/git" -maxdepth 2 -type f -perm -100 -exec dirname {} ';' | sort -f | uniq | tr '\n' ':' | sed 's/:$//'):$PATH"
fi
export PATH="$HOME/Dropbox/bin:$HOME/bin:$PATH"
export PYTHONPATH="$HOME/git"

# environment
if which nvim >/dev/null 2>&1; then
	export EDITOR='nvim'
elif which vim >/dev/null 2>&1; then
	export EDITOR=vim
else
	export EDITOR=vi
fi
export VISUAL=$EDITOR
export MANPAGER="/bin/sh -c \"col -b | $EDITOR -c 'set ft=man ts=8 nomod nolist nonu noma' -\""
export HISTSIZE=10000
export HISTCONTROL=ignoredups
export PYTHONIOENCODING="utf-8"

# soar variables
if [ -d "$HOME/git/Soar" ]; then
	case "$(uname)" in
	"Linux")
		if uname -v | grep Ubuntu 2>&1 >/dev/null; then
			if [ -d "/usr/lib/jvm/default-java" ]; then
				export JAVA_HOME="/usr/lib/jvm/default-java"
			fi
		elif [ -d "/usr/lib/jvm/java-7-openjdk" ]; then
			export JAVA_HOME="/usr/lib/jvm/java-7-openjdk"
		fi
		export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:$HOME/git/Soar/out";;
	"Darwin")
		export DYLD_LIBRARY_PATH="$DYLD_LIBRARY_PATH:$HOME/git/Soar/out";;
	esac
	export PYTHONPATH="$HOME/git/Soar/out:$PYTHONPATH"
fi

# clean up the paths
export PATH="$(echo "$PATH" | sed 's#//#/#g')"
export PYTHONPATH="$(echo "$PYTHONPATH" | sed 's#//#/#g')"

# prompt
prompt_command_fn() {
	# right before prompting for the next command, save the previous command in a file.
	echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)	$(hostname)	$PWD	$(history 1 | sed 's/^ *[0-9 -]* //; s/ *$//;')" >> ~/Dropbox/personal/logs/shell_history
}
PS1='[\u@\h \W]\$ '
if [ -e ~/Dropbox/personal/logs/shell_history ]; then
	PROMPT_COMMAND=prompt_command_fn
fi

# aliases
alias rm='rm -i'
alias cp='cp -i'
alias mv='mv -i'
alias grep='grep --color=auto'

if which bc >/dev/null 2>&1; then
	alias bc='bc -l'
fi
if which flake8 >/dev/null 2>&1; then
	alias flake8='flake8 --ignore=E501'
fi
if which journal.py >/dev/null 2>&1; then
	alias jrnl="journal.py --ignore '$(ls ~/journal/[a-z-]*.journal 2>/dev/null | grep -v '[ ()]' | tr '\n' ',')'"
fi
if which scons >/dev/null 2>&1 && which python3 >/dev/null 2>&1; then
	alias scons="scons --python=$(which python3)"
fi
if [ -d "$HOME/git/Soar" ]; then
	alias soar="$HOME/git/Soar/out/testcli"
fi
if which valgrind >/dev/null 2>&1; then
	alias valgrind='valgrind --dsymutil=yes --leak-check=yes --track-origins=yes'
fi

alias vi="$VISUAL"
alias vim="$VISUAL"
if [ -d "$HOME/journal" ]; then
	alias vino="$VISUAL $HOME/journal/notes.journal"
fi
if [ "$NVIM_LISTEN_ADDRESS" != "" ]; then
	unset MANPAGER
	alias :="$(which nvimcmd)"
	alias vi="$(which nvimcmd) tabnew"
	alias vim="$(which nvimcmd) tabnew"
	alias nvim="$(which nvimcmd) tabnew"
	if [ -d "$HOME/journal" ]; then
		alias vino="$(which nvimcmd) tabnew $HOME/journal/notes.journal"
	fi
fi

case "$(uname)" in
	"Linux")
		alias ls='ls --color=auto --time-style=long-iso'
		if which xdg-open >/dev/null 2>&1; then
			alias open='xdg-open'
		fi
		if which vncserver >/dev/null 2>&1; then
			alias vncserver='vncserver -depth 8'
		fi
		if which x11vnc >/dev/null 2>&1; then
			alias x11vnc='x11vnc -display :0 -xkb -usepw -noxdamage'
		fi;;
	"Darwin")
		alias ls='ls -G';;
esac

# python venv
if which python3 >/dev/null 2>&1; then
	export PYTHON_VENV_HOME=~/.venv
	if [ ! -d $PYTHON_VENV_HOME ]; then
		mkdir $PYTHON_VENV_HOME
	fi
	function mkvenv() {
		if [ ! -d $PYTHON_VENV_HOME ]; then
			echo "venv $1 already exists"
		else
			python3 -m venv $PYTHON_VENV_HOME/$1
			workon $1
		fi
	}
	function workon() {
		source $PYTHON_VENV_HOME/$1/bin/activate
	}
	function rmvenv() {
		rm -rf $PYTHON_VENV_HOME/$1
	}
	function lsvenv() {
		ls $PYTHON_VENV_HOME
	}
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

if which python3 >/dev/null 2>&1 && [ -f ~/.bash_completion.d/shellscrape.py ]; then
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
# append to history instead of overwriting it
shopt -s histappend
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

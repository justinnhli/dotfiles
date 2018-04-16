#!/bin/bash

# If not running interactively, don't do anything
[ -z "$PS1" ] && return

update_dot_files() {
	curl -L 'https://raw.githubusercontent.com/justinnhli/dotfiles/master/bash/.bash_profile' > "$HOME/.bash_profile"
	curl -L 'https://raw.githubusercontent.com/justinnhli/dotfiles/master/bash/.bashrc' > "$HOME/.bashrc"
	curl -L 'https://raw.githubusercontent.com/justinnhli/dotfiles/master/neovim/.config/nvim/init.vim' > "$HOME/.vimrc"
}

# paths
export PATH="/usr/local/bin:/usr/local/opt/sqlite/bin:$PATH"
export PATH="$HOME/Dropbox/bin:$HOME/bin:$PATH"
export PATH="$(find "$HOME/git" -maxdepth 2 -type f -perm -100 -exec dirname {} ';' 2>/dev/null | sort -f | uniq | tr '\n' ':' | sed 's/:$//'):$PATH"
export PATH="$(find "$HOME/Dropbox/projects" -maxdepth 2 -type f -perm -100 -exec dirname {} ';' 2>/dev/null | sort -f | uniq | tr '\n' ':' | sed 's/:$//'):$PATH"
export PYTHONPATH="$HOME/Dropbox/projects:$HOME/git"

# environment
case "$(uname)" in
'Linux')
	WHICH='which --skip-alias';;
'Darwin')
	WHICH='which';;
esac
if $WHICH nvim >/dev/null 2>&1; then
	export EDITOR=nvim
	export MANPAGER="nvim -c 'set ft=man' -"
elif $WHICH vim >/dev/null 2>&1; then
	export EDITOR=vim
else
	export EDITOR=vi
fi
export VISUAL="$EDITOR"
export HISTSIZE=10000
export HISTCONTROL=ignoredups
export PYTHONIOENCODING='utf-8'
if [ -f "$HOME/.dot_secrets/bashrc" ]; then
	source "$HOME/.dot_secrets/bashrc"
fi

# soar variables
if [ -d "$HOME/git/Soar" ]; then
	case "$(uname)" in
	'Linux')
		if [ -d '/usr/lib/jvm/default-java' ]; then
			export JAVA_HOME='/usr/lib/jvm/default-java'
		elif [ -d '/usr/lib/jvm/default' ]; then
			export JAVA_HOME='/usr/lib/jvm/default'
		fi
		export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:$HOME/git/Soar/out";;
	'Darwin')
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
	echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)	$(hostname)	$PWD	$(history 1 | sed 's/^ *[0-9 -]* //; s/ *$//;')" >> "$HOME/Dropbox/personal/logs/$(date -u +%Y).shistory"
}
PS1='[\u@\h \W]\$ '
if [ -e "$HOME/Dropbox/personal/logs" ]; then
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
if which pydocstyle >/dev/null 2>&1; then
	alias pydocstyle='pydocstyle --convention=pep257 --add-ignore=D105,D413'
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
if which yapf >/dev/null 2>&1; then
	alias yapf="yapf --style=$HOME/.config/yapf/style"
fi

alias vi="$VISUAL"
alias vim="$VISUAL"
if [ "$NVIM_LISTEN_ADDRESS" != '' ]; then
	unset MANPAGER
	export PATH="$PYTHON_VENV_HOME/neovim/bin:$PATH"
	alias :="$(which nvimcmd)"
	alias vi="$(which nvimcmd) tabnew"
	alias vim="$(which nvimcmd) tabnew"
	alias nvim="$(which nvimcmd) tabnew"
	if [ -d "$HOME/journal" ]; then
		alias vino="$(which nvimcmd) tabnew $HOME/journal/notes.journal"
	fi
fi

case "$(uname)" in
	'Linux')
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
	'Darwin')
		alias ls='ls -G';;
esac

# python modules
if which python3 >/dev/null 2>&1; then
	alias doctest='python3 -m doctest'
	alias pydoc='python3 -m pydoc -b'
fi

# python venv
if which python3 >/dev/null 2>&1; then
	alias pip='python3 -m pip'
	VENV_LIST="$HOME/.config/packages-meta/venv"
	export PYTHON_VENV_HOME="$HOME/.venv"
	if [ ! -d "$PYTHON_VENV_HOME" ]; then
		mkdir "$PYTHON_VENV_HOME"
	fi
	mkvenv() {
		if [ $# -ne 1 ]; then
			echo 'usage: mkvenv VENV_NAME'
			return 1
		elif [ -d "$PYTHON_VENV_HOME/$1" ]; then
			echo "venv $1 already exists"
			return 1
		else
			python3 -m venv "$PYTHON_VENV_HOME/$1"
			workon "$1"
			pip install --upgrade pip
		fi
	}
	workon() {
		if [ $# -eq 0 ]; then
			lsvenv
		elif [ $# -eq 1 ]; then
			if [ -f "$PYTHON_VENV_HOME/$1/bin/activate" ]; then
				source "$PYTHON_VENV_HOME/$1/bin/activate"
			else
				read -p "venv '$1' not found; do you want to create it (Y/n)? " response
				if [[ ! $response =~ ^[Nn]$ ]]; then
					mkvenv "$1"
				fi
			fi
		else
			echo 'usage: workon [environment]'
			return 1
		fi
	}
	rmvenv() {
		for venv in "$@"; do
			rm -rf "$PYTHON_VENV_HOME/$venv"
		done
	}
	lsvenv() {
		find "$PYTHON_VENV_HOME/" -mindepth 1 -maxdepth 1 -type d -exec basename {} ';' | sort
	}
	venv-source() {
		results="$( (
			(
				find ~/git -maxdepth 2 -name requirements.txt
				find ~/Dropbox/projects -maxdepth 2 -name requirements.txt
			) | while read requirements; do
				path="$(dirname "$requirements")"
				name="$(basename "$path")"
				modules="$(cat $requirements | tr '\n' ' ')"
				echo "$name" "$path" "$modules"
			done
			cat ~/.config/packages-meta/venv | while read line; do
				path="$HOME/.config/packages-meta/venv"
				name="$(echo "$line" | cut -d ' ' -f 1)"
				modules="$(echo "$line" | cut -d ' ' -f 2-)"
				echo "$name" "$path" "$modules"
			done
			) | sort | uniq
		)"
		if [ $# -eq 0 ]; then
			echo "$results"
		else
			echo $@ | sort | while read line; do
				echo "$results" | grep "^$line "
			done
		fi
	}
	venv-comm() {
		comm <(workon) <(venv-source | cut -d ' ' -f 1)
	}
	venv-all() {
		lsvenv | sort | while read venv; do
			venv="$(basename "$venv")"
			echo "$venv" && workon "$venv" && $@ && deactivate
		done
	}
	venv-freeze() {
		lsvenv | sort | while read venv; do
			venv="$(basename "$venv")"
			workon "$venv" && echo "$venv $(pip list --not-required --format freeze | sed 's/=.*//;' | tr '\n' ' ')" && deactivate
		done
	}
	venv-setup() {
		venv-source | sort --ignore-case | while read line; do
			venv="$(echo "$line" | cut -d ' ' -f 1)"
			packages="$(echo "$line" | cut -d ' ' -f 3-)"
			echo
			echo "VENV $venv" | tr '[:lower:]' '[:upper:]'
			echo
			if [ ! -f "$PYTHON_VENV_HOME/$venv/bin/activate" ]; then
				rm -rf "$PYTHON_VENV_HOME/$venv"
			elif [ ! -e "$PYTHON_VENV_HOME/$venv/bin/python3" ]; then
				rm -rf "$PYTHON_VENV_HOME/$venv"
			fi
			if [ ! -d "$PYTHON_VENV_HOME/$venv" ]; then
				mkvenv "$venv" && pip install $packages && deactivate
			elif ! echo "$packages" | grep '[>=]' >/dev/null 2>&1; then
				workon "$venv"
				packages="$(python3 -m pip list --outdated --format freeze | sed 's/=.*//;' | tr '\n' ' ')"
				if [ "$packages" != "" ]; then
					pip install --upgrade $packages
				fi
				deactivate
			fi
		done
	}
fi

# journal related settings
if [ -d "$HOME/journal" ]; then
	note() {
		date '+%Y-%m-%d %H:%M' >> "$HOME/journal/scratch.journal"
		printf '\t%s\n' "$*" >> "$HOME/journal/scratch.journal"
	}
	alias vino="$VISUAL $HOME/journal/notes.journal"
	if which journal.py >/dev/null 2>&1; then
		alias jrnl="journal.py --ignore '$(ls $HOME/journal/[a-z-]*.journal 2>/dev/null | grep -v '[ ()]' | tr '\n' ',')'"
	fi
fi

# completion
_generic_completion() {
	# build up the context
	local context="${COMP_WORDS[0]}"
	if [ $COMP_CWORD -gt 0 ]; then
		for i in $(seq "$COMP_CWORD"); do
			context="$context ${COMP_WORDS[i]}"
		done
	fi
	# call script
	COMPREPLY=( $($HOME/.bash_completion.d/shellscrape.py "$(pwd)" "$context") )
}

if which python3 >/dev/null 2>&1 && [ -f "$HOME/.bash_completion.d/shellscrape.py" ]; then
	for program in $($HOME/.bash_completion.d/shellscrape.py); do
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
# allow '**' to match subdirectories (if bash version >= 4)
if [ "$( ( echo "$BASH_VERSION" && echo 4 ) | sort -n | tail -n 1 )" != "4" ]; then
	shopt -s globstar
fi

# disable output stop keyboard shortcut (so <C-s> can be mapped in vim)
stty stop '' -ixoff

# make C-w stop at slashes
stty werase undef
bind '"\C-w": unix-filename-rubout'

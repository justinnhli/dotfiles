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
export PYTHONPATH="$(find "$HOME/git" -maxdepth 2 -type f -name 'setup.py' -exec dirname {} ';' 2>/dev/null | sort -f | uniq | tr '\n' ':' | sed 's/:$//'):$PYTHONPATH"

# basic environment
export XDG_CONFIG_HOME=$HOME/.config
export XDG_CACHE_HOME=$HOME/.cache
export XDG_DATA_HOME=$HOME/.local/share
if command -v nvim >/dev/null 2>&1; then
	export EDITOR=nvim
	export MANPAGER="nvim -c 'set ft=man' -"
elif command -v vim >/dev/null 2>&1; then
	export EDITOR=vim
else
	export EDITOR=vi
fi
export VISUAL="$EDITOR"
export HISTSIZE=10000
export HISTCONTROL=ignoredups

# environment variables
# nltk
export NLTK_DATA="$HOME/.local/share/nltk"
# npm
export NPM_CONFIG_USERCONFIG="$XDG_CONFIG_HOME/npm/npmrc"
# python
export PYTHONIOENCODING='utf-8'
if command -v python3 >/dev/null 2>&1 && python3 -c 'import readline' >/dev/null 2>&1; then
	# Python on macOS does not include readline by default
	# https://pypi.org/project/gnureadline/
	export PYTHONSTARTUP="$XDG_CACHE_HOME/python/pythonstartup.py"
fi
# soar
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
# sqlite
export SQLITE_HISTORY="$XDG_DATA_HOME/sqlite_history"

if [ -f "$HOME/.dot_secrets/bashrc" ]; then
	source "$HOME/.dot_secrets/bashrc"
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

if command -v bc >/dev/null 2>&1; then
	alias bc='bc -l'
fi
if command -v flake8 >/dev/null 2>&1; then
	alias flake8='flake8 --ignore=E501'
fi
if command -v pyan.py >/dev/null 2>&1; then
	alias pyan='pyan.py --grouped --colored --no-defines --dot'
fi
if command -v pydocstyle >/dev/null 2>&1; then
	alias pydocstyle='pydocstyle --convention=pep257 --add-ignore=D105,D413'
fi
if command -v scons >/dev/null 2>&1 && command -v python3 >/dev/null 2>&1; then
	alias scons="scons --python=\$(command -v python3)"
fi
if [ -d "$HOME/git/Soar" ]; then
	alias soar="$HOME/git/Soar/out/testcli"
fi
if command -v tmux >/dev/null 2>&1; then
	alias tmux='tmux -f $XDG_CONFIG_HOME/.tmux/tmux.conf'
fi
if command -v valgrind >/dev/null 2>&1; then
	alias valgrind='valgrind --dsymutil=yes --leak-check=yes --track-origins=yes'
fi
if command -v wget >/dev/null 2>&1; then
	alias wget="wget --hsts-file='$XDG_CACHE_HOME/wget-hsts'"
fi
if command -v yapf >/dev/null 2>&1; then
	alias yapf="yapf --style=$HOME/.config/yapf/style"
fi

alias vi="$VISUAL"
alias vim="$VISUAL"
if [ "$NVIM_LISTEN_ADDRESS" != '' ]; then
	unset MANPAGER
	export PATH="$PYTHON_VENV_HOME/neovim/bin:$PATH"
	alias :="\$(command -v nvimcmd)"
	alias vi="\$(command -v nvimcmd) tabnew"
	alias vim="\$(command -v nvimcmd) tabnew"
	alias nvim="\$(command -v nvimcmd) tabnew"
	if [ -d "$HOME/journal" ]; then
		alias vino="\$(command -v nvimcmd) tabnew \"\$HOME/journal/notes.journal\""
	fi
fi

case "$(uname)" in
	'Linux')
		alias ls='ls --color=auto --time-style=long-iso'
		if command -v xdg-open >/dev/null 2>&1; then
			alias open='xdg-open'
		fi
		if command -v vncserver >/dev/null 2>&1; then
			alias vncserver='vncserver -depth 8'
		fi
		if command -v x11vnc >/dev/null 2>&1; then
			alias x11vnc='x11vnc -display :0 -xkb -usepw -noxdamage'
		fi;;
	'Darwin')
		alias ls='ls -G';;
esac

# python modules
if command -v python3 >/dev/null 2>&1; then
	alias doctest='python3 -m doctest'
	alias pydoc='python3 -m pydoc -b'
fi

# python venv
if command -v python3 >/dev/null 2>&1; then
	alias pip='python3 -m pip'
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
			# should ensure that system python3 is used
			# (as opposed to python3 in a venv)
			py="$(command -v python3)"
			if readlink "$py" >/dev/null; then
				newpy="$(readlink "$py")"
				# if the link is relative, prepend the original
				if [[ "$newpy" == .* ]]; then
					py="$(dirname "$py")/$newpy"
				else
					py="$py"
				fi
			fi
			$py -m venv "$PYTHON_VENV_HOME/$1"
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
			) | while read -r requirements; do
				path="$(dirname "$requirements")"
				name="$(basename "$path")"
				modules="$(tr '\n' ' ' < "$requirements")"
				echo "$name" "$path" "$modules"
			done
			cat ~/.config/packages-meta/venv | while read -r line; do
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
			echo $@ | sort | while read -r line; do
				echo "$results" | grep "^$line "
			done
		fi
	}
	venv-comm() {
		comm <(workon) <(venv-source | cut -d ' ' -f 1)
	}
	venv-all() {
		lsvenv | sort | while read -r venv; do
			venv="$(basename "$venv")"
			echo "$venv" && workon "$venv" && $@ && deactivate
		done
	}
	venv-freeze() {
		lsvenv | sort | while read -r venv; do
			venv="$(basename "$venv")"
			workon "$venv" && echo "$venv $(pip list --not-required --format freeze | sed 's/=.*//;' | tr '\n' ' ')" && deactivate
		done
	}
	venv-setup() {
		venv-source | sort --ignore-case | while read -r line; do
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
	alias vino="$VISUAL $HOME/journal/notes.journal"
	if command -v journal.py >/dev/null 2>&1; then
		alias jrnl="journal.py $(ls $HOME/journal/[a-z-]*.journal 2>/dev/null | grep -v '[ ()]' | sed 's/^/--ignore /' | tr '\n' ' ')"
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

if command -v python3 >/dev/null 2>&1 && [ -f "$HOME/.bash_completion.d/shellscrape.py" ]; then
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

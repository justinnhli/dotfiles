#!/bin/bash

update_dot_files() {
	curl -L 'https://raw.githubusercontent.com/justinnhli/dotfiles/master/bash/.bash_profile' > "$HOME/.bash_profile"
	curl -L 'https://raw.githubusercontent.com/justinnhli/dotfiles/master/bash/.bashrc' > "$HOME/.bashrc"
	curl -L 'https://raw.githubusercontent.com/justinnhli/dotfiles/master/neovim/.config/nvim/init.vim' | sed 's/ \.\. / . /g' > "$HOME/.vimrc"
}

# paths
PATH="/usr/local/bin:/usr/local/opt/sqlite/bin:$PATH"
PATH="$HOME/Dropbox/bin:$HOME/bin:$PATH"
PATH="$(find "$HOME/git" -maxdepth 2 -type f -perm -100 -exec dirname {} ';' 2>/dev/null | sort -f | uniq | tr '\n' ':' | sed 's/:$//'):$PATH"
PATH="$(find "$HOME/Dropbox/projects" -maxdepth 2 -type f -perm -100 -exec dirname {} ';' 2>/dev/null | sort -f | uniq | tr '\n' ':' | sed 's/:$//'):$PATH"
export PYTHONPATH="$HOME/Dropbox/projects:$HOME/git"

# basic environment
export XDG_CONFIG_HOME=$HOME/.config
export XDG_CACHE_HOME=$HOME/.cache
export XDG_DATA_HOME=$HOME/.local/share
export SECRETS_HOME=$HOME/.secrets
if command -v nvim >/dev/null 2>&1; then
	export EDITOR=nvim
	export MANPAGER='nvim +Man!'
	export MANWIDTH=999
elif command -v vim >/dev/null 2>&1; then
	export EDITOR=vim
else
	export EDITOR=vi
fi
export VISUAL="$EDITOR"
case "$(uname)" in
'Linux')
	export BROWSER='firefox';;
'Darwin')
	# don't set BROWSER on Mac, since it breaks jupyter
	# see https://bugs.python.org/issue24955
	unset BROWSER;;
esac
export HISTSIZE=10000
export HISTCONTROL=ignoredups

# environment variables
# gpg
export GNUPGHOME="$SECRETS_HOME/.gnupg"
# ipython
export IPYTHONDIR="$XDG_CONFIG_HOME/ipython"
# jupyter
export JUPYTER_CONFIG_DIR="$XDG_CONFIG_HOME/jupyter"
# nltk
export NLTK_DATA="$HOME/.local/share/nltk"
# npm
export NPM_CONFIG_USERCONFIG="$XDG_CONFIG_HOME/npm/npmrc"
# pass
export PASSWORD_STORE_DIR="$SECRETS_HOME/.password-store"
export PASSWORD_STORE_CLIP_TIME=20
# python
export PYTHONIOENCODING='utf-8'
if command -v python3 >/dev/null 2>&1 && python3 -c 'import readline' >/dev/null 2>&1; then
	# Python on macOS does not include readline by default
	# https://pypi.org/project/gnureadline/
	export PYTHONSTARTUP="$XDG_CONFIG_HOME/python/pythonstartup.py"
fi
# scikit-learn
export SCIKIT_LEARN_DATA="$XDG_DATA_HOME/scikit-learn"
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

if [ -f "$SECRETS_HOME/.bashrc" ]; then
	source "$SECRETS_HOME/.bashrc"
fi

# clean up the paths
PATH="${PATH//\/\//\/}"
export PYTHONPATH="${PYTHONPATH//\/\//\/}"

# prompt
prompt_command_fn() {
	# right before prompting for the next command, save the previous command in a file.
	echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)	$(hostname)	$PWD	$(history 1 | sed 's/^ *[0-9 -]* //; s/ *$//;')" >> "$HOME/Dropbox/personal/logs/$(date -u +%Y).shistory"
}
PS1='[\u@\h \W]\$ '
if [ -d "$HOME/Dropbox/personal/logs" ]; then
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
if command -v scons >/dev/null 2>&1 && command -v python3 >/dev/null 2>&1; then
	alias scons="scons --python=\$(command -v python3)"
fi
if [ -d "$HOME/git/Soar" ]; then
	alias soar='$HOME/git/Soar/out/testcli'
fi
if command -v tmux >/dev/null 2>&1; then
	alias tmux='tmux -f $XDG_CONFIG_HOME/tmux/tmux.conf'
fi
if command -v update-everything.py >/dev/null 2>&1; then
	alias delete-orphans='update-everything.py delete-orphans'
fi
if command -v valgrind >/dev/null 2>&1; then
	alias valgrind='valgrind --dsymutil=yes --leak-check=yes --track-origins=yes'
fi
if command -v wget >/dev/null 2>&1; then
	alias wget='wget --hsts-file="$XDG_CACHE_HOME/wget-hsts"'
fi
if command -v yapf >/dev/null 2>&1; then
	alias yapf='yapf --style="$HOME/.config/yapf/style"'
fi

alias vi='$VISUAL'
alias vim='$VISUAL'

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
export PIP_REQUIRE_VIRTUALENV=true
if command -v python3 >/dev/null 2>&1; then
	alias pip='python3 -m pip'
	alias gpip='PIP_REQUIRE_VIRTUALENV=false python3 -m pip'
	export PYTHON_VENV_HOME="$XDG_DATA_HOME/venv"
	if [ ! -d "$PYTHON_VENV_HOME" ]; then
		mkdir -p "$PYTHON_VENV_HOME"
	fi
	mkvenv() {
		if [ $# -lt 1 ]; then
			echo "usage: ${FUNCNAME[0]} VENV_NAME [PIP_ARGS ...]"
			return 1
		elif [ -d "$PYTHON_VENV_HOME/$1" ]; then
			echo "venv $1 already exists"
			return 1
		fi
		# ensure that system python3 is used
		# (as opposed to python3 in a venv)
		py="$(command -v python3)"
		if readlink "$py" >/dev/null; then
			newpy="$(readlink "$py")"
			# if the link is relative, prepend the original
			if [[ "$newpy" == .* ]]; then
				py="$(dirname "$py")/$newpy"
			fi
		fi
		$py -m venv "$PYTHON_VENV_HOME/$1"
		workon "$1"
		pip install --upgrade pip wheel
		if [ $# -gt 1 ]; then
			shift 1
			pip install "$@"
		fi
	}
	workon() {
		if [ $# -eq 0 ]; then
			lsvenv
			return 0
		fi
		if [ -f "$PYTHON_VENV_HOME/$1/bin/activate" ]; then
			source "$PYTHON_VENV_HOME/$1/bin/activate"
		else
			read -rp "venv '$1' not found; do you want to create it (Y/n)? " response
			if [[ ! $response =~ ^[Nn]$ ]]; then
				mkvenv "$@"
			fi
		fi
	}
	venvrun() {
		if [ $# -lt 2 ]; then
			echo "usage: ${FUNCNAME[0]} VENV_NAME SCRIPT [ARGS ...]"
			return 1
		fi
		# try both a python file and an installed script
		if [ -f "$2" ]; then
			( workon "$1" && shift 1 && python3 "$@" )
		else
			( workon "$1" && shift 1 && "$@" )
		fi
	}
	rmvenv() {
		for venv in "$@"; do
			rm -rf "${PYTHON_VENV_HOME:?}/$venv"
		done
	}
	lsvenv() {
		find "$PYTHON_VENV_HOME/" -mindepth 1 -maxdepth 1 -type d -exec basename {} ';' | sort
	}
fi

# nvim terminal
if [ "$NVIM_LISTEN_ADDRESS" != '' ]; then
	unset MANPAGER
	alias :='$(command -v nvimcmd)'
	alias vi='$(command -v nvimcmd) tabnew'
	alias vim='$(command -v nvimcmd) tabnew'
	alias nvim='$(command -v nvimcmd) tabnew'
	workon neovim
fi

# PIM related settings
if [ -d "$HOME/pim" ]; then
	pim_dir="$HOME/pim"
	alias vijj='$VISUAL -c "normal 1 JJ" -c tabonly'
	alias vijl='$VISUAL -c "normal 1 JL" -c tabonly'
	alias vijr='$VISUAL -c "normal 1 JR" -c tabonly'
	alias vijn='$VISUAL -c "normal 1 JN" -c tabonly'
	alias vijd='$VISUAL -c "normal 1 JD" -c tabonly'
	alias vijc='$VISUAL -c "normal 1 JC" -c tabonly'
	alias vijp='$VISUAL -c "normal 1 JP" -c tabonly'
	if command -v journal.py >/dev/null 2>&1; then
		alias jrnl="journal.py \$(find $pim_dir/journal/ -maxdepth 1 -name '[a-z]*.journal' | sed 's/^/--ignore /' | tr '\n' ' ')"
	fi
fi

# completion
_generic_completion() {
	# build up the context
	local context="${COMP_WORDS[0]}"
	if [ "$COMP_CWORD" -gt 0 ]; then
		for i in $(seq "$COMP_CWORD"); do
			context="$context ${COMP_WORDS[i]}"
		done
	fi
	# call script
	COMPREPLY=( $("$HOME"/.bash_completion.d/shellscrape.py "$(pwd)" "$context") )
}

if command -v python3 >/dev/null 2>&1 && [ -f "$HOME/.bash_completion.d/shellscrape.py" ]; then
	for program in $("$HOME"/.bash_completion.d/shellscrape.py); do
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

# if the shell is interactive
if echo "$-" | grep i >/dev/null 2>&1; then
	# disable output stop keyboard shortcut (so <C-s> can be mapped in vim)
	stty stop '' -ixoff
	# make C-w stop at slashes
	stty werase undef
	bind '"\C-w": unix-filename-rubout'
fi

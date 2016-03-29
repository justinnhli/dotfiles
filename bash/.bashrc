#!/bin/sh

update_dot_files() {
	curl -L 'https://raw.githubusercontent.com/justinnhli/dotfiles/master/bash/.bash_profile' > "$HOME/.bash_profile"
	curl -L 'https://raw.githubusercontent.com/justinnhli/dotfiles/master/bash/.bashrc' > "$HOME/.bashrc"
	curl -L 'https://raw.githubusercontent.com/justinnhli/dotfiles/master/neovim/.config/nvim/init.vim' > "$HOME/.vimrc"
}

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

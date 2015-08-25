#!/bin/sh

update_dot_files() {
	curl -L 'https://raw.githubusercontent.com/justinnhli/dotfiles/master/bash/.bash_profile' > "$HOME/.bash_profile"
	curl -L 'https://raw.githubusercontent.com/justinnhli/dotfiles/master/bash/.bashrc' > "$HOME/.bashrc"
	curl -L 'https://raw.githubusercontent.com/justinnhli/dotfiles/master/neovim/.nvim/nvimrc' > "$HOME/.vimrc"
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
alias bc='bc -l'
alias flake8='flake8 --ignore=E501'
alias grep='grep --color=auto'
alias jrnl="journal.py --ignore '$(ls ~/journal/*.journal 2>/dev/null | tr '\n' ',')'"
alias pacaur='pacaur --domain aur4.archlinux.org'
alias pylint='pylint --indent-string="    " --disable=invalid-name,missing-docstring,old-style-class,star-args,line-too-long,bad-builtin,bad-continuation --reports=n'
alias soar='~/git/Soar/out/testcli'
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

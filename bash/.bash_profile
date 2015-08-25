# paths
export PATH="$HOME/bin:$(find "$HOME/git" -maxdepth 2 -type f -perm -100 -exec dirname {} ';' | sort | uniq | tr '\n' ':' | sed 's/:$//'):$PATH"
export PYTHONPATH="$HOME/git:$(find "$HOME/git" -maxdepth 2 -type f -name '*.py' -exec dirname {} ';' | sort | uniq | tr '\n' ':' | sed 's/:$//')"

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

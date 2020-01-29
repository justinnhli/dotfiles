# silence OS X default interactive shell message
export BASH_SILENCE_DEPRECATION_WARNING=1

# source .bashrc if interactive
case "$-" in
	*i*)
		if [ -r ~/.bashrc ]; then
			. ~/.bashrc
		fi;;
esac

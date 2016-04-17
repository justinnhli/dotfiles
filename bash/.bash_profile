# source .bashrc if interactive
case "$-" in
	*i*)
		if [ -r ~/.bashrc ]; then
			. ~/.bashrc
		fi;;
esac

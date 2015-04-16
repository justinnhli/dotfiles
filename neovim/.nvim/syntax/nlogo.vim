set tabstop=2
set shiftwidth=2

set iskeyword+=+
set iskeyword+=-
set iskeyword+=*
set iskeyword+=/
set iskeyword+=<
set iskeyword+=>
set iskeyword+==
set iskeyword+=?
set iskeyword+=!

syn match comment ";.*$"

syn region foldable matchgroup=definition start="^to " end="^end$" fold contains=reserved,maths,comment,flow
syn region foldable matchgroup=definition start="^[a-z-]\+ \[$" end="^\]$" fold contains=reserved,maths,comment,flow

syn keyword reserved + * - / ^ < > = != <= >=

syn keyword reserved clear-patches cp diffuse diffuse4 distance distancexy import-pcolors import-pcolors-rgb inspect is-patch? myself neighbors neighbors4 nobody no-patches of other patch patch-at patch-ahead patch-at-heading-and-distance patch-here patch-left-and-ahead patch-right-and-ahead patch-set patches patches-own random-pxcor random-pycor self sprout subject turtles-here
syn keyword reserved all? any? ask ask-concurrent at-points count in-cone in-radius is-agent? is-agentset? is-patch-set? is-turtle-set? link-heading link-length link-set link-shapes max-n-of max-one-of min-n-of min-one-of n-of neighbors neighbors4 no-patches no-turtles of one-of other patch-set patches sort sort-by turtle-set turtles with with-max with-min turtles-at turtles-here turtles-on
syn keyword reserved approximate-hsb approximate-rgb base-colors color extract-hsb extract-rgb hsb import-pcolors import-pcolors-rgb pcolor rgb scale-color shade-of? wrap-color
syn keyword reserved clear-all ca clear-drawing cd clear-patches cp clear-turtles ct display import-drawing import-pcolors import-pcolors-rgb no-display max-pxcor max-pycor min-pxcor min-pycor patch-size reset-ticks resize-world set-patch-size tick tick-advance ticks world-width world-height
syn keyword reserved follow follow-me reset-perspective rp ride ride-me subject watch watch-me
syn keyword reserved hubnet-broadcast hubnet-broadcast-clear-output hubnet-broadcast-message hubnet-broadcast-view hubnet-clear-override hubnet-clear-overrides hubnet-enter-message? hubnet-exit-message? hubnet-fetch-message hubnet-message hubnet-message-source hubnet-message-tag hubnet-message-waiting? hubnet-reset hubnet-reset-perspective hubnet-send hubnet-send-clear-output hubnet-send-follow hubnet-send-message hubnet-send-override hubnet-send-watch hubnet-set-client-interface
syn keyword reserved beep clear-output date-and-time export-view export-interface export-output export-plot export-all-plots export-world import-drawing import-pcolors import-pcolors-rgb import-world mouse-down? mouse-inside? mouse-xcor mouse-ycor output-print output-show output-type output-write print read-from-string reset-timer set-current-directory show timer type user-directory user-file user-new-file user-input user-message user-one-of user-yes-or-no? write
syn keyword reserved file-at-end? file-close file-close-all file-delete file-exists? file-flush file-open file-print file-read file-read-characters file-read-line file-show file-type file-write user-directory user-file user-new-file
syn keyword reserved but-first but-last empty? filter first foreach fput histogram is-list? item last length list lput map member? modes n-of n-values of position one-of reduce remove remove-duplicates remove-item replace-item reverse sentence shuffle sort sort-by sublist
syn keyword reserved but-first but-last empty? first is-string? item last length member? position remove remove-item read-from-string replace-item reverse substring word
syn keyword reserved abs acos asin atan ceiling cos e exp floor int is-number? ln log max mean median min mod modes new-seed pi precision random random-exponential random-float random-gamma random-normal random-poisson random-seed remainder round sin sqrt standard-deviation subtract-headings sum tan variance
syn keyword reserved autoplot? auto-plot-off auto-plot-on clear-all-plots clear-plot create-temporary-plot-pen export-plot export-all-plots histogram plot plot-name plot-pen-exists? plot-pen-down plot-pen-reset plot-pen-up plot-x-max plot-x-min plot-y-max plot-y-min plotxy set-current-plot set-current-plot-pen set-histogram-num-bars set-plot-pen-color set-plot-pen-interval set-plot-pen-mode set-plot-x-range set-plot-y-range
syn keyword reserved both-ends clear-links create-link-from create-links-from create-link-to create-links-to create-link-with create-links-with die hide-link in-link-neighbor? in-link-neighbors in-link-from is-directed-link? is-link? is-link-set? is-undirected-link? __layout-magspring layout-radial layout-spring layout-tutte link-heading link-length link-neighbor? link links links-own link-neighbors link-with my-in-links my-links my-out-links no-links other-end out-link-neighbor? out-link-neighbors out-link-to show-link tie untie
syn keyword reserved movie-cancel movie-close movie-grab-view movie-grab-interface movie-set-frame-rate movie-start movie-status
syn keyword reserved behaviorspace-run-number
syn keyword reserved netlogo-applet? netlogo-version
syn keyword reserved breed color heading hidden? label label-color pen-mode pen-size shape size who xcor ycor
syn keyword reserved pcolor plabel plabel-color pxcor pycor
syn keyword reserved breed color end1 end2 hidden? label label-color shape thickness tie-mode
syn keyword reserved ?
syn keyword reserved breed directed-link-breed extensions globals __includes patches-own to-report turtles-own undirected-link-breed

syn match reserved "[[:alnum:]-]*-at"
syn match reserved "[[:alnum:]-]*-here"
syn match reserved "[[:alnum:]-]*-on"
syn match reserved "create-[[:alnum:]-]*"
syn match reserved "create-ordered-[[:alnum:]-]*"
syn match reserved "hatch-[[:alnum:]-]*"
syn match reserved "is-[[:alnum:]-]*?"
syn match reserved "sprout-[[:alnum:]-]*"
syn match reserved "sprout-[[:alnum:]-]*"
syn match reserved "[[:alnum:]-]*-at"
syn match reserved "[[:alnum:]-]*-here"
syn match reserved "[[:alnum:]-]*-on"
syn match reserved "create-[[:alnum:]-]*-from"
syn match reserved "create-[[:alnum:]-]*-from"
syn match reserved "create-[[:alnum:]-]*-to"
syn match reserved "create-[[:alnum:]-]*-to"
syn match reserved "create-[[:alnum:]-]*-with"
syn match reserved "create-[[:alnum:]-]*-with"
syn match reserved "in-[[:alnum:]-]*-neighbor?"
syn match reserved "in-[[:alnum:]-]*-neighbors"
syn match reserved "in-[[:alnum:]-]*-from"
syn match reserved "[[:alnum:]-]*-neighbor?"
syn match reserved "[[:alnum:]-]*-neighbors"
syn match reserved "[[:alnum:]-]*-with"
syn match reserved "[[:alnum:]-]*-own"
syn match reserved "my-[[:alnum:]-]*"
syn match reserved "my-in-[[:alnum:]-]*"
syn match reserved "my-out-[[:alnum:]-]*"
syn match reserved "out-[[:alnum:]-]*-neighbor?"
syn match reserved "out-[[:alnum:]-]*-neighbors"
syn match reserved "out-[[:alnum:]-]*-to"

syn keyword flow and ask ask-concurrent carefully error-message every foreach if ifelse ifelse-value let loop map not or repeat report run runresult semicolon set stop startup to-report wait while with-local-randomness without-interruption xor
syn keyword flow back bk can-move? clear-turtles ct create-ordered-turtles cro create-turtles crt die distance distancexy downhill downhill4 dx dy face facexy forward fd hatch hide-turtle ht home inspect is-turtle? jump layout-circle left lt move-to myself nobody no-turtles of other patch-ahead patch-at patch-at-heading-and-distance patch-here patch-left-and-ahead patch-right-and-ahead pen-down pd pen-erase pe pen-up pu random-xcor random-ycor right rt self set-default-shape __set-line-thickness setxy shapes show-turtle st sprout stamp stamp-erase subject subtract-headings tie towards towardsxy turtle turtle-set turtles turtles-at turtles-here turtles-on turtles-own untie uphill uphill4

syn match const "[[:alnum:]]\@<!-\?[0-9]*\.\?[0-9]\+[[:alnum:]]\@!"
syn keyword const nobody false true white green red blue grey gray cyan black white yellow orange

hi reserved ctermfg=darkmagenta
hi const ctermfg=darkred
hi flow ctermfg=darkblue
hi definition ctermfg=green

hi Comment ctermfg=LightGrey

set foldmethod=syntax

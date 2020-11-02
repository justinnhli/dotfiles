" copy HTML of Moodle roster into a buffer and source this file
:%!grep -o '<img [^>]*>'
:%s#.*src="\([^"]*\)".*Picture of \([^"]*\).*#<div style="display:inline-block; text-align:center;"><img src="\1" style="height:250px;"><br>\2</div>#
:%s/\<f2\>/f3/g

#!/bin/zsh
directory=/Users/julesgraybill/Downloads
foreach image ( $directory/*.jpg )
n=${image%.*}
magick $image -adaptive-resize 400x -density 72 $n.png
end
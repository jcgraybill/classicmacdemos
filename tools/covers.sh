#!/bin/zsh
foreach image ( *.jp2 )
n=${image%.*}
mkdir $n
magick $image -adaptive-resize 500x -density 72 $n/image-1.png
end
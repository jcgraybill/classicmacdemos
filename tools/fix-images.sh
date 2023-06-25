#!/bin/zsh
mkdir out
foreach image ( *.png )
magick $image -adaptive-resize 752x -density 72 -gravity center -crop 640x630+0+0 +repage -gravity South -crop 640x554+0+0 +repage -gravity North -crop 640x480+0+0 out/$image
end

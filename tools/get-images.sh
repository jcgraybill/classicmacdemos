#!/bin/bash
clear

(
cd ~/Desktop/discs/
for dir in */; do
echo "$dir"
	( 
	cd "$dir"
	magick mogrify -resize 400 -format png disc.tif 2> /dev/null
	mv disc.png image-1.png 2> /dev/null
	magick mogrify -resize 400 -format png "disc 1.tif" 2> /dev/null
	mv "disc 1.png" image-1.png 2> /dev/null
	magick mogrify -resize 400 -format png "disc 2.tif" 2> /dev/null
	mv "disc 2.png" image-2.png 2> /dev/null
	)
done
)
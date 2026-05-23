#!/bin/bash 

clear
for dir in ~/Desktop/*/; do
	echo -n $dir
	
	if [ -f "$dir/.done" ]; then 
	 echo ": ✅"
	elif [ -f "$dir/.skip" ]; then
	 echo ": 👉"	
	else
	 	echo
		(
			cd "$dir"
			for tiff in *.tiff; do
				root="${tiff%.tiff}"
				mv "$root.tiff" "$root.tif" 2> /dev/null
			done			
			for cdr in *.cdr; do
				root="${cdr%.cdr}"
				mv "$root.cdr" "$root.iso" 2> /dev/null
			done
			for toast in *.toast; do
				root="${toast%.toast}"
				mv "$root.toast" "$root.iso" 2> /dev/null
			done

			echo -n "title:       "
			read title

			identifier=""
			while [ "$identifier" = "" ]; do
				echo -n "identifier:  "
				read identifier
				files=`ia list $identifier`
				if [ "$files" = "" ]; then 
					echo -n "year [####]: "
					read year
					echo -n "month [##]:   "
					read month
					if [ "$month" = "" ]; then
						date="$year"
					else
						date="$year-$month"
					fi			
					echo
					echo "$title ($identifier) $date"
					echo -n "Upload? [y/N]: "
					read confirmation
					if [ "$confirmation" = "y" ]; then
						caffeinate ia upload $identifier *.iso *.tif \
							--metadata="mediatype:software" \
							--metadata="collection:open_source_software" \
							--metadata="language:eng" \
							--metadata="title:$title" \
							--metadata="date:$date" \
							--metadata="creator:Macworld" \
							--metadata="subject:CD-ROM" \
							--metadata="subject:Macworld" \
							--metadata="subject:coverdisc" \
							--metadata="subject:vintagesoftware" \
							--metadata="subject:Macintosh" 
							
						echo -n "Success? [y/N]: "
						read success
						if [ "$success" = "y" ]; then					
							echo "🎉"
							touch .done
						else
							echo "😕"
							touch .skip
						fi
						echo 
					else
						echo "CANCELED - proceeding to next folder"
						exit 0
					fi
					else
					echo "$identifier is already taken; suggest another"
					identifier=""
				fi
			done
		)
		echo
	fi
done
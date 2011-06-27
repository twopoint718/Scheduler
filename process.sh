#!/bin/sh

if [[ $1 == "summary.ps" ]]
then
    echo "skipping summary"
else
    gs -q -r300 -dSAFER -dBATCH -dNOPAUSE -dNOCACHE -sDEVICE=pnggray \
        -sOutputFile=tmp.png $1
    convert tmp.png -resize 800x800 $2
    # clean up
    rm tmp.png
fi


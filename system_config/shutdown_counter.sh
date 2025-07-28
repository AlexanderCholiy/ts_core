#!/bin/bash
filename='/tmp/counter.txt'

if ! test -e "$filename"; then
  echo "Counter file does not exist. Creating"
  echo 0 > $filename

fi

gpiostate=gpioget gpiochip0 12

if [[ $gpiostate -eq 1 ]]; then
   counter=0
else
   counter=cat $filename
   counter=$((counter+1))
fi
echo $counter > $filename

if [[ $counter -gt 10 ]]; then
  echo "Counter > 10. Shutting down"
  shutdown -P now
fi
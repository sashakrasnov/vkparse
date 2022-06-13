#!/bin/sh

# Option 1

for wall in https://vk.com/publicXYZ https://vk.com/publicABC https://vk.com/public123
do
    echo Parsing: $wall
    python3 vkparse.py $wall &
done


# Option 2

python3 vkparse.py https://vk.com/publicXXX https://vk.com/publicYYY https://vk.com/publicZZZ

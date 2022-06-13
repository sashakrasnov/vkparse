@echo off

rem Option 1

(FOR %%w IN (
    https://vk.com/publicXYZ
    https://vk.com/publicABC
    https://vk.com/public123
    ) DO (
        echo Parsing: %%w
        start python vkparse.py %%w
))

rem Option 2

python vkparse.py https://vk.com/publicXXX https://vk.com/publicYYY https://vk.com/publicZZZ

export PYTHONPATH=~/git/projects/web-copy-py/src
python -c "from jomi.webcopy.ClipboardCopy import *; web_copy_main()" "$*"
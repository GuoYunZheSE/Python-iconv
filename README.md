# Pyiconv
A small iconv implemented by python3
## Description
This program will accept a `filepath/directory`, the `origin`(or can be determined in the runtime) and `dst` encoding, then it will transfer the specific file(s) to the `dst` encoding.
Now, the encoding supported are:
- utf-8
- utf-16
- gb18030
- ascii

## Usage
```shell
git@github.com:GuoYunZheSE/Python-iconv.git
pip3 install -r requirments.txt

python3 iconv.py --help

iconv

optional arguments:
  -h, --help            show this help message and exit
  -p path, --path path  The directory or file path
  -o origin, --origin origin
                        The origin file encode
  -d destination, --dst destination
                        The destination file encode

```

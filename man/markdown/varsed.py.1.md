varsed.py -- replace non-quoted semi-colons with newlines
=============================================

## SYNOPSIS

`varsed.py -i <file>`

## DESCRIPTION

`varsed.py` prints the contents of a file, except replacing non-quoted semi-colons with newlines. The script considers each line individually and therefore ignores block quotations.

## EXAMPLES

For a file `v.txt` with the content:

```
a="1;2"
b='3;4'
5;6
```

Running the command:

```
varsed.py -i v.txt
```

Prints this to console:

```
a="1;2"
b='3;4'
5
6
```

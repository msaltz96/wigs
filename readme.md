# Pre-WIGs Validator (Linux)

The Pre-WIGs Validator is a tool for validating whether or not an instance is prepared for ingestion via WIGs into AMS

Please see the documentation.md for information about configuring the validation tests.


## Getting Started


### Usage
**Note: must run as root**

```
sudo ./pre-wigs-validator --help

usage: pre-wigs-validator [-h] [-l] [-v] [-q]

Validates that a Linux machine is prepared for ingestion into AMS via WIGs

optional arguments:
  -h, --help     show this help message and exit
  -l, --log      create json log file of results in logs folder
  -v, --verbose  include in-depth error messages in console output
  -q, --quiet    suppress console output


```

## Building / Converting Code into Binary


The following steps describe how to build a binary from the source code


### Prerequisites


Python3 and pip must be installed to build


### Build Steps


Open command prompt and navigate to directory of application


Install dependencies from setup.py and PyInstaller

```
pip3 install . pyinstaller
```


Run PyInstaller

```
pyinstaller --onefile --name=pre-wigs-validator control_script.py
```

Move binary to root directory of the application

```
mv dist/pre-wigs-validator ./pre-wigs-validator
```



## Alternate Process (no PyInstaller)

Python3.6 or higher and pip must be installed to run

Install dependencies from setup.py (notice the dot)

```
pip3 install .
```

Run script

```
python3 control_script.py
```


---



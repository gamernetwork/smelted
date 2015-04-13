# smelted

Simple GUI for [melted](https://github.com/mltframework/melted).

## Requirements

For Ubuntu 14.04

```
gir1.2-gtk-3.0
libxml2-dev
libxslt-dev
virtualenv
python-gi
python-lxml # or install via pip in a venv
```
## Running

Assuming melted is already running on default port:

```
python main.py
```
## configuration

Melted configuation is up to you, but default config is usually `/etc/melted.conf`.

Edit `Smelted_Settings.py` to change port number or to change default unit ID, if you've done so in `melted.conf`.


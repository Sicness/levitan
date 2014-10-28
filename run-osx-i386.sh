#!/bin/bash
defaults write com.apple.versioner.python Prefer-32-Bit -bool yes
arch -i386 /usr/bin/python $(pwd)/main.py
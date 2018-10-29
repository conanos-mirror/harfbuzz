#!/usr/bin/env python
# -*- coding: utf-8 -*-


from bincrafters import build_template_default
import os

os.environ['CONAN_USERNAME'] = os.environ.get('CONAN_USERNAME','conanos')

if __name__ == "__main__":

    builder = build_template_default.get_builder()
    builder.run()

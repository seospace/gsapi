import os
from shutil import copy

engine_path = os.path.dirname(os.path.abspath(__file__)) + '\\' + '{{ cookiecutter.engine_name }}.ini'
gsa_dir = r"{{ cookiecutter.gsa_engines_directory }}"

copy(engine_path, gsa_dir)
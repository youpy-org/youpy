# -*- encoding: utf-8 -*-
"""
"""


from pathlib import Path

from youpy._engine.error import YoupyException


class InvalidProjectDir(YoupyException):

    def __init__(self, path):
        self.path = path

    def __str__(self):
        return f"invalid project path: '{self.path}'"

INTERNAL_DIR = ".youpy"

def is_project_dir(path):
    return (path / INTERNAL_DIR).exists()

def get_project_dir(path):
    p = Path(path).resolve()
    while str(p) != p.root and not is_project_dir(p):
        p = p.parent
    if str(p) == p.root:
        raise InvalidProjectDir(path)
    return p

class Project:

    STAGE_DIR = "stage"

    def __init__(self, path):
        self._path = Path(path)
        assert self._path.is_absolute() and self._path.is_dir()

    @property
    def path(self):
        return self._path

    @property
    def name(self):
        return self._path.name

    @property
    def stage_dir(self):
        return self._path / self.STAGE_DIR

    def iter_sprite_dirs(self):
        for p in self._path.iterdir():
            if p.name not in (self.STAGE_DIR, "__pycache__", INTERNAL_DIR) \
               and p.is_dir():
                yield p

    @property
    def config_file(self):
        return self._path / INTERNAL_DIR / "config.json"

    @property
    def stage_module_path(self):
        return self.sprite_module_path(self.STAGE_DIR)

    def sprite_module_path(self, name):
        return f"{self.name}.{name}.{name}"

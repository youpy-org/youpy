# -*- encoding: utf-8 -*-
"""
"""


from pathlib import Path

from funpyschool._engine.media import iter_images_set


def is_project_dir(path):
    return (path / "__main__.py").exists()

def get_project_dir(path):
    p = Path(path).resolve()
    while p != p.root and not is_project_dir(p):
        p = p.parent
    if p == p.root:
        raise ValueError("invalid project path: '{path}'")
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

    def iter_backdrop_images(self):
        yield from iter_images_set(self.stage_dir)

    def iter_sprite_dirs(self):
        for p in self._path.iterdir():
            if p.name != self.STAGE_DIR and p.name != "__pycache__" \
               and p.is_dir():
                yield p

    @property
    def config_file(self):
        return self._path / "config.json"

    @property
    def stage_module_path(self):
        return self.sprite_module_path(self.STAGE_DIR)

    def sprite_module_path(self, name):
        return f"{self.name}.{name}.{name}"

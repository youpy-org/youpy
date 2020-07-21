# -*- encoding: utf-8 -*-
"""
"""


from ._tools import extended_sys_path
from ._engine.api import Engine
from ._project import Project
from ._project import get_project_dir


def run(path, show_fps=False):
    project_dir = get_project_dir(path)
    project = Project(project_dir)
    engine = Engine(project, show_fps=show_fps)
    with extended_sys_path(project_dir.parent):
        return engine.run()

# -*- encoding: utf-8 -*-
"""
"""


from youpy.tools import extended_sys_path
from youpy.engine import Engine
from youpy.project import Project
from youpy.project import get_project_dir
from youpy.logging import init_logger


def run(path, show_fps=False, log_level=None):
    project_dir = get_project_dir(path)
    project = Project(project_dir)
    engine = Engine(project, show_fps=show_fps)
    init_logger(project, log_level=log_level)
    with extended_sys_path(project_dir.parent):
        return engine.run()

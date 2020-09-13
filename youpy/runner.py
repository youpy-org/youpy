# -*- encoding: utf-8 -*-
"""
"""


from youpy.tools import extended_sys_path
from youpy.engine import Engine
from youpy.engine import Simulation
from youpy.project import Project
from youpy.project import get_project_dir
from youpy.logging import init_logger


def run(path, show_fps=False, log_level=None, syslog_level=None,
        log_context=False):
    project_dir = get_project_dir(path)
    project = Project(project_dir)
    simu = Simulation(project, show_fps=show_fps)
    engine = Engine(simu)
    init_logger(project, log_level=log_level, syslog_level=syslog_level,
                log_context=log_context)
    with extended_sys_path(project_dir.parent):
        return engine.run()

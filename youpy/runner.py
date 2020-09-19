# -*- encoding: utf-8 -*-
"""
"""


from youpy.tools import extended_sys_path
from youpy.engine import Engine
from youpy.engine import Simulation
from youpy.project import Project
from youpy.project import get_project_dir
from youpy import logging
LOGGER = logging.getLogger(__name__)


def run(path,
        show_fps=False, fps=30,
        log_level=None, syslog_level=None, log_context=False):
    project_dir = get_project_dir(path)
    project = Project(project_dir)
    logging.init_logger(project, log_level=log_level, syslog_level=syslog_level,
                        log_context=log_context)
    LOGGER.info("=" * 60)
    LOGGER.info(f"running {project.name}")
    simu = Simulation(project, show_fps=show_fps)
    engine = Engine(simu, target_fps=fps)
    with extended_sys_path(project_dir.parent):
        return engine.run()

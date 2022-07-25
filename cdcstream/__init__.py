"""Top-level package for cdcstream."""

__author__ = """Martin Trat"""
__email__ = 'trat@fzi.de'
__version__ = '0.1.3'

import sys
import logging

from .cdcstream import DriftDetector, CDCStream
from .dilca_wrapper import DilcaDistance, dilca_workflow

from . import tools


logger = logging.getLogger(__name__)

WEKA_DEPENDENCIES = [DilcaDistance]


# Check if external dependencies fulfilled
tools.manage_jvm_start()
any_installations = False
for dep in WEKA_DEPENDENCIES:
    installed = tools.check_package_installed(
        package_name=dep._weka_package_name, package_version=dep._weka_package_version_min,
        raise_error=False)
    if not installed:
        any_installations = True
        tools.attempt_install_package(package_name=dep._weka_package_name, defer_application_exit=True)
if any_installations:
    logger.warning('An application restart is necessary - exiting.')
    tools.manage_jvm_stop()
    sys.exit(0)

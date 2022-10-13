"""Top-level package for cdcstream."""

"""
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

__author__ = 'Martin Trat'
__email__ = 'trat@fzi.de'
__license__ = 'GNU General Public License v3.0'
__version__ = '0.1.6'


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

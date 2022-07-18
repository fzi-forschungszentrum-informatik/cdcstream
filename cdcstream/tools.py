
import sys
import logging

import weka.core.jvm as jvm
from weka.core import packages
import javabridge
from packaging import version


logger = logging.getLogger(__name__)


def manage_jvm_start(packages=True):
    if not jvm.started:
        jvm.start(packages=packages)
        return
    else:
        # lost contact to running java vm --> regain
        #   (also, it is advisable to call javabridge.detach() at the end of workloads as clean-up)
        if javabridge._javabridge.get_vm().is_active() and javabridge.get_env() is None:
            logger.info('Reattaching to running Java VM after losing connection.')
            javabridge.attach()
        if not jvm.with_package_support and packages:
            manage_jvm_stop()
            # stop and restart not possible with javabridge (as of 2022.06)
            raise RuntimeError('Package support found deactivated. Exiting...')

def manage_jvm_detach():
    javabridge.detach()

def manage_jvm_stop():
    jvm.stop()

def check_package_installed(package_name, package_version=None, raise_error=False):
    res = packages.is_installed(package_name, version=None)
    if res and package_version:
        p = packages.installed_package(package_name)
        res = version.parse(p.version) >= version.parse(package_version)

    if not res:
        err_msg = f'Required package "{package_name}" or version is not installed.'
        if package_version is not None:
            err_msg += f' Required version is {package_version}'
        if raise_error:
            manage_jvm_stop()
            raise RuntimeError(err_msg)
        else:
            logger.error(err_msg)
    return res

def attempt_install_package(package_name):
    logger.warning(f'An attempt to install package "{package_name}" is in progress.')
    packages.establish_cache()
    packages.refresh_cache()
    p = packages.available_package(package_name)
    if p:
        # we assume that dependency packages are available
        p = [p] + [i.target.get_package() for i in p.dependencies]
        success = []
        for pack in p:
            success.append(packages.install_package(pack.name))
        if all(success):
            logger.warning(f'Successfully installed package(s) {p}. '
                           'An application restart is necessary - exiting.')
            manage_jvm_stop()
            sys.exit(0)
        else:
            manage_jvm_stop()
            raise RuntimeError(f'Error installing package "{package_name}"')
    else:
        manage_jvm_stop()
        raise RuntimeError(f'Could not find package "{package_name}" in official registry.')

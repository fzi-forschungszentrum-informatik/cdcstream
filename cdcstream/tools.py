
import logging

import weka.core.jvm as jvm
import javabridge


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

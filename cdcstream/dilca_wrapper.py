
__author__ = "Martin Trat"
__email__ ="trat@fzi.de"
__license__ = "MIT"


from typing import Union
import logging
from math import sqrt

import numpy as np
import pandas as pd
import weka
import weka.filters as filters
from weka.core.dataset import create_instances_from_matrices
from weka.core.converters import load_any_file
from weka.core.distances import DistanceFunction
import javabridge

from . import tools


logger = logging.getLogger(__name__)


class DilcaDistance(DistanceFunction):
    """
    Wrapper for the external Weka package DilcaDistance
    https://svn.cms.waikato.ac.nz/svn/weka/trunk/packages/external/DilcaDistance/src/main/java/weka/core/DilcaDistance.java

    # to install package via python:
    import weka.core.packages as packages
    
    if not packages.is_installed('DilcaDistance'):
        packages.refresh_cache()
        packages.install_package('DilcaDistance')
    
    # to instantiate (alternatively to this class-based approach, https://stackoverflow.com/a/66947489):
    from weka.core.classes import from_commandline
    import weka.core.distances as distances

    DD = distances.DistanceFunction(
        jobject=from_commandline('weka.core.DilcaDistance -R 1-5 -D', 
                                 classname='weka.core.distances.DistanceFunction').jobject,
                                 options=["-R", "1-5", "-D"])
    # or
    DD = from_commandline('weka.core.DilcaDistance -R 1-5 -D', classname='weka.core.distances.DistanceFunction')  
    # check result
    DD.to_commandline()
    """

    _weka_package_name = 'DilcaDistance'
    _weka_package_version_min = '1.0.2'

    def __init__(self, supervised=False, attribute_indices=None):
        """Instantiates DILCA Distance.
        Per default, unsupervised discretization is performed.

        Args:
            supervised (bool, optional): Supervised discretization of numerical attributes (unsupervised if False). Defaults to False.
            attribue_indices (list or str, optional): List of attribute indices (int, 0-based) 
                or str containing WEKA-style attribute indices to use (1-based). If None, alle attributes are used.
                Defaults to None.
        """
        tools.manage_jvm_start()

        _jobject = DistanceFunction.new_instance('weka.core.' + self._weka_package_name)
        self.enforce_type(_jobject, 'weka.core.DistanceFunction')
        super().__init__(jobject=_jobject, options=None)
        self.is_optionhandler = True  # forcefully...

        self.set_supervised_discretization(supervised)

        if attribute_indices:
            if type(attribute_indices) == str:
                self.attribute_indices = attribute_indices
            elif type(attribute_indices) == list:
                self.set_formatted_attribute_indices(attribute_indices)

    def set_supervised_discretization(self, sup):
        # Java method: void setSupervisedDiscretization(boolean value)
        javabridge.call(self.jobject, 'setSupervisedDiscretization', '(Z)V', sup)
        
    def set_formatted_attribute_indices(self, indices):
        """Accepts 0-based attribute indices, converts them to 1-based indices string
        and sets those.

        Args:
            indices (list): attribute indices (0-based)
        """
        ind_form = [str(i + 1) for i in indices]
        ind_form = ','.join(ind_form)
        self.attribute_indices = ind_form

    def get_matrices_dilca(self):
        """Fetches dilca matrices from Java and loads those as numpy arrays.
        Matrix computation is done on a batch of data instances set via self.instances.

        Args:

        Returns:
            list: list of dilca matrices (numpy.ndarray each)
        """
        if not self.instances:
            raise ValueError('No instances provided.')

        # based on toString method implemented in DilcaDistance
        # (version 1.0.2, https://weka.sourceforge.io/packageMetaData/DilcaDistance/1.0.2.html)
        arr_list = self.__str__().split('\n\n\n')[:-1]
        matrices_dilca = []
        for arr in arr_list:
            mat_flat = np.fromstring(arr.replace('\n', ''), sep=' ')
            n_rows = int(sqrt(mat_flat.shape[0]))
            matrices_dilca.append(
                mat_flat.reshape(n_rows, -1)
            )
        return matrices_dilca

    def extract_summary(self):
        """Returns a scalar summary, extracted from all dilca matrices, computed on a batch of data instances

        Returns:
            float: Dilca matrix summary value.
        """
        matrices_dilca = self.get_matrices_dilca()
        n_matrices = len(matrices_dilca)  # corresponds to numAttributes
        attr_wise_summaries = []
        for m_idx, m in enumerate(matrices_dilca):
            m_cardi = m.shape[0]
            if m_cardi <= 0:
                raise ValueError(f'Dilca matrix associated to column {m_idx} has illegal shape.')
            norm_factor = m_cardi * (m_cardi - 1) * 0.5 if m_cardi > 1 else 1
            # feature with constant value results in m_cardi=1, upper triangular nonexistent i.e. =0 -> summary=0
            m_triu_sq_sum_sqr = np.sqrt(np.sum(np.square(np.triu(m)), axis=None))  
            # sum applied to all elements --> scalar
            attr_wise_summaries.append(m_triu_sq_sum_sqr / norm_factor)
        return np.sum(attr_wise_summaries) / n_matrices

    def get_information(self, print_instances=False):
        print('is_optionhandler:', self.is_optionhandler)  # outputs false if not forced in __init__
        print('options:', self.options)
        print('config:', self.config)
        # associated setter: DD.config = {'type': 'OptionHandler', 'class': 'weka.core.DilcaDistance', 'options': ''}
        if self.instances and print_instances:
            print('-------------')
            print(self.instances)

    def export(self, to_format='json'):
        if to_format == 'json':
            print(self.to_json())
        elif to_format == 'dict':
            print(self.to_dict())
        
    def cleanup(self):
        tools.manage_jvm_stop()

def dilca_workflow(data: pd.DataFrame, nominal_cols: Union[list,str], supervised: bool) -> float:
    """Executes a DilcaDistance-related workflow for a given batch of data resulting in its summary value.
    
    Args:
        data (pd.DataFrame): The data batch.
        nominal_cols (list): A list of nominal columns.
        supervised (bool): Use supervised distance calculation.

    Returns:
        float: The calculated summary value.
    """
    data_weka = create_weka_dataset(
        data, 'data', cols_nom=nominal_cols)

    DD = DilcaDistance(supervised=supervised)
    # compute necessary matrices and execute the FCBF-Search on a specific batch of data
    DD.instances = data_weka
    # fetch dilca matrices, built based on the provided data
    return DD.extract_summary()


# WEKA
def create_weka_dataset(
    data: pd.DataFrame, name: str, cols_nom: Union[list,str] =[]) -> weka.core.dataset.Instances:
    """Converts data to a WEKA-style dataset.
    Possibly useful methods:
    # dataset.subset('5')  # returns only a copy, attribute indices need to be provided
    # dataset._mc_set_class_index(0)

    Args:
        data (pd.DataFrame): The input data.
        name (str): The name of WEKA dataset.
        cols_nom (list or "all", optional): The list of nominal columns. For nominal conversion to happen,
            at least one dataset column needs to be in this list. If "all", all columns are converted. Defaults to [].
        verbose (bool, optional): Verbose output. Defaults to False.

    Returns:
        weka.core.dataset.Instances: The WEKA dataset.
    """
    tools.manage_jvm_start()
    
    ds_weka = create_instances_from_matrices(data.to_numpy(), name=name)
    nom_cols_indices = []
    nom_cols = []
    if cols_nom == 'all':
        cols_nom = data.columns.to_list()
    else:
        if type(cols_nom) != list:
            raise ValueError(f'Provided cols_nom "{cols_nom} is unsupported."')

    for idx, col_name in enumerate(data.columns):
        if col_name in cols_nom:
            nom_cols_indices.append(idx)
            nom_cols.append(col_name)
    if nom_cols_indices:
        logger.debug(f'Converting following {len(nom_cols)} colums to nominal: {nom_cols}')
        num2nom = filters.Filter('weka.filters.unsupervised.attribute.NumericToNominal',
                                 options=['-R', ','.join(str(i + 1) for i in nom_cols_indices)])  # 1-based indexing
        num2nom.inputformat(ds_weka)
        ds_weka = num2nom.filter(ds_weka)
    return ds_weka

def load_weka_dataset(path, cls_idx=None):
    tools.manage_jvm_start()
    return load_any_file(path, class_index=cls_idx)

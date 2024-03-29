
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


from typing import Callable, Union

import numpy as np
import pandas as pd

from cdcstream.dilca_wrapper import dilca_workflow


class DriftDetector:
    ALERT_NONE = 0
    ALERT_NONE_MSG = ''
    ALERT_WARN = 1
    ALERT_WARN_MSG = 'warning'
    ALERT_CHANGE = 2
    ALERT_CHANGE_MSG = 'change'

    ALERT_COL_NAME = 'alert'

class UnsupervisedDriftDetector(DriftDetector):
    supervised = False


class CDCStream(UnsupervisedDriftDetector):

    def __init__(self,
                 alert_callback: Callable=None,
                 summary_extractor: Callable=dilca_workflow,
                 summary_extractor_args: dict={'nominal_cols': 'all'},
                 factor_warn: float=2.0,
                 factor_change: float=3.0,
                 factor_std_extr_forg: Union[float, int] =0,
                 cooldown_cycles: int =0) -> None:
        """Instantiates a CDCStream Drift Detector.

        BibTex:
        ```
        @inproceedings{Ienco2014,
        doi = {10.1145/2554850.2554864},
        url = {https://doi.org/10.1145/2554850.2554864},
        year = {2014},
        month = mar,
        publisher = {{ACM}},
        author = {Dino Ienco and Albert Bifet and Bernhard Pfahringer and Pascal Poncelet},
        title = {Change detection in categorical evolving data streams},
        booktitle = {Proceedings of the 29th Annual {ACM} Symposium on Applied Computing}
        }
        ```

        Args:
            alert_callback (Callable, optional): Function being called after each batch with an
                alert code of ALERT_NONE, ALERT_WARN, ALERT_CHANGE. Must accept as arguments:
                alert_code: int, alert_msg: str. Defaults to None.
            summary_extractor (Callable, optional): Function for extracting a summary value from a
                batch of data. Must accept as first parameter: data; as named parameter:
                supervised. Defaults to cdcstream.dilca_wrapper.dilca_workflow.
            summary_extractor_args (dict, optional): Other named parameters (apart from first
                parameter data and named parameter supervised) to pass to summary_extractor.
                Defaults to {'nominal_cols': 'all'}.
            factor_warn (float, optional): Parameter for Chebychev's Inequality for issuing a drift
                warning. Must be smaller than or equal to factor_change. Defaults to 2.0.
            factor_change (float, optional): Parameter for Chebychev's Inequality for signaling a
                detected drift. Must be greater than or equal to factor_warn. In case of equality,
                warnings are treated as changes. Defaults to 3.0.
            factor_std_extr_forg (float, optional): Parameter implementing forgetting of standard
                deviation extrema (novel algorithm extension; untested). Value between 0 and 1.
                Larger values result in faster forgetting. Defaults to 0 (no forgetting).
            cooldown_cycles (int, optional): Parameter implementing a cooldown mechanism (novel
                algorithm extension). Positive value or 0. Passed value sets the number of cycles
                (passed batches) during which no warning/change evaluation is done after a change
                is detected. Defaults to 0 (no cooldown).
                Cite this extension as (BibTex):
                ```
                @techreport{TratBenderOvtcharova2023_1000155196,
                    author       = {Trat, Martin and Bender, Janek and Ovtcharova, Jivka},
                    year         = {2023},
                    title        = {Sensitivity-Based Optimization of Unsupervised Drift Detection for Categorical Data Streams},
                    doi          = {10.5445/IR/1000155196},
                    institution  = {{Karlsruher Institut für Technologie (KIT)}},
                    issn         = {2194-1629},
                    series       = {KIT Scientific Working Papers},
                    keywords     = {unsupervised conceptdriftdetection, data streammining, productiveartificialintelligence, categorical data processing},
                    pagetotal    = {10},
                    language     = {english},
                    volume       = {208}
                }
                ```
        """
        super().__init__()

        self.history = []  # holding history of batch summaries
        self.batch_current_summary_statistic = None  # current batch summary value
        self.batch_current_data = None  # current batch data

        self.summary_extractor = summary_extractor
        self.summary_extractor_args = summary_extractor_args

        self.history_mean = None
        self.history_std = None
        self.history_std_min = None
        self.history_std_max = None

        self.factor_warn = factor_warn
        self.factor_change = factor_change
        self.current_warn = False  # True if warning detected in current cycle
        self.current_change = False  # True if change detected in current cycle

        self._alert_callback = alert_callback

        self._log = []

        self.factor_std_extr_forg = factor_std_extr_forg

        self.cooldown_cycles = cooldown_cycles
        self._cur_cooldown_cycles = 0

        self._check_parameters()

    def _check_parameters(self) -> None:
        if not self.factor_warn <= self.factor_change:
            raise ValueError('factor_warn has to be smaller than or equal to factor_change')

    def feed_new_batch(self, batch: pd.DataFrame) -> None:
        """Called in order to analyze new data batch.

        Args:
            batch (pandas.DataFrame): The new data batch.
        """
        self.batch_current_data = batch
        self._cycle_routine()

    def _cycle_routine(self) -> None:
        """Main cycle of drift detector. It is being called with each new batch being fed.
        """
        self._reset()
        self._extract_current_batch_summary_statistic()
        self._std_extrema_forgetting()  # BEFORE history statistics (especially stds) are being computed
        self._compute_history_statistics()
        self.evaluate()
        self._update_log()
        self._alert()  # AFTER _update_log
        self._cleanup_current_cycle()

    def _cleanup_current_cycle(self) -> None:
        """Executes cycle finishing tasks.
        In accordance with Ienco's algorithm, the batch history will be reset BEFORE a batch
        causing a change being detected will be appended to it (- history now only reflects data
        from the "new distribution"). The history lenght will, after the first cycle, never again
        fall below 1 (even after a change being detected).
        """
        if self.current_change:  # React to CHANGE
            self.reset_history()
            self.start_cooldown()

        if self.batch_current_summary_statistic is not None:
            self.history.append(self.batch_current_summary_statistic)
            # AFTER history is being resetted and history statistics are being computed!

    def _extract_current_batch_summary_statistic(self) -> None:
        self.batch_current_summary_statistic = self.summary_extractor(
            self.batch_current_data, supervised=self.supervised,
            **self.summary_extractor_args)
        if np.isnan(self.batch_current_summary_statistic):  # TODO: implement this check in extractor callable?
            raise ValueError('Summary statistic with nan value detected.')

    def _compute_history_statistics(self) -> None:
        """Computes statistical history metrics.
        After the first cycle following initial start, a history mean will be calculated in each
        cycle (as history length then always >= 1). After the first two cycles following initial
        start, also a history standard deviation will be calculated in each cycle. Both, mean and
        standard deviation will also be recalculated immediately after a change being detected.
        """
        if len(self.history) == 0:
            return  # gather more batches, at least one summary statistic value necessary

        # also calculate mean with only one value in history
        self.history_mean = np.mean(self.history)
        _std = None
        if len(self.history) == 1:
            if self.history_std_min is None:
                return  # gather more batches, at least two summary statistic values necessary
            else:
                _std = (self.history_std_min + self.history_std_max) / 2.0

        elif len(self.history) > 1:
            _std = np.std(self.history)

            if self.history_std_min is None or _std < self.history_std_min:
                self.history_std_min = _std
            if self.history_std_max is None or _std > self.history_std_max:
                self.history_std_max = _std

        self.history_std = _std

    def _std_extrema_forgetting(self) -> None:
        """ Novel extension to Ienco's algorithm. Causes maximum and minimum standard deviation to
        shrink and grow respectively by a specified factor in each cycle.
        Shrinking or growing stops as extrema cross each other (i.e. minimum becomes larger than
        maximum or opposite scenario).
        Shrinking or growing happens BEFORE extrema being potentially updated through new summary
        statistic value. (This way, we do not apply forgetting directly after extrema are updated.)
        """
        if self.history_std_min is None or self.factor_std_extr_forg == 0:
            return
        pot_std_min = self.history_std_min * (1 + self.factor_std_extr_forg)
        pot_std_max = self.history_std_max * (1 - self.factor_std_extr_forg)
        if pot_std_min > pot_std_max:
            return
        else:
            self.history_std_min = pot_std_min
            self.history_std_max = pot_std_max

    def start_cooldown(self) -> None:
        """Implements a change detection cooldown to prevent immediate change detections after an
        initial change was detected. During cooldown_cycles cycles, no change detections are being
        embraced and the history might recover itself. This causes a decrease in this detector's
        sensitivity and might be suitable for data resulting in temporily highly volatile summary
        statistic values. It might especially mitigate the effect of history std being recalculated
        as a rather low value, with only one summary statistic value being present in the history
        after a detected change (which caused a history reset).
        """
        self._cur_cooldown_cycles = self.cooldown_cycles

    def _reset(self):
        self.current_warn = False
        self.current_change = False

    def reset_history(self) -> None:
        self.history = []

    def _trigger(self, factor: float) -> bool:
        return abs(self.batch_current_summary_statistic - self.history_mean) >= \
            (factor * self.history_std)

    def evaluate(self) -> None:
        """Evaluates the occurence of drift based on Chebychev's Inequality. Is called in every
        cycle. With attribute history_std being None (first two cycles after initial detector start),
        this step is skipped.
        """
        if self.history_std is None:
            return

        if self._cur_cooldown_cycles != 0:
            self._cur_cooldown_cycles -= 1
            return

        if self._trigger(self.factor_change):  # CHANGE DETECTED
            self.current_change = True
            return  # do not trigger change AND warning!
        elif self._trigger(self.factor_warn):  # WARNING DETECTED
            self.current_warn = True

    def _alert(self) -> None:
        """Publishes a detected alert. Important to keep in mind is that the program will execute
        all code inside the callback self._alert_callback before returning to self._cycle_routine!
        """
        if self.current_change:
            alert_code = self.ALERT_CHANGE
            alert_msg = self.ALERT_CHANGE_MSG
        elif self.current_warn:
            alert_code = self.ALERT_WARN
            alert_msg = self.ALERT_WARN_MSG
        else:
            alert_code = self.ALERT_NONE
            alert_msg = self.ALERT_NONE_MSG
        try:
            self._alert_callback(alert_code, alert_msg)
        except TypeError:
            pass  # if user provided no alert_callback

    def _update_log(self) -> None:
        log_el = ()
        log_el = log_el + (self.batch_current_summary_statistic,)

        if self.history_mean:
            log_el = log_el + (self.history_mean,)
        else:
            log_el = log_el + (0.,)
        if self.history_std:
            log_el = log_el + (self.history_std,)
        else:
            log_el = log_el + (0.,)

        if self.current_warn:
            log_el = log_el + (self.ALERT_WARN,)
        elif self.current_change:
            log_el = log_el + (self.ALERT_CHANGE,)
        else:
            log_el = log_el + (self.ALERT_NONE,)

        self._log.append(log_el)

    @property
    def log(self) -> pd.DataFrame:
        """Returns a log array of the drift analysis.
        Columns: 'batch_summary_statistic', 'history_mean', 'history_std', 'alert'

        Returns:
            pandas.DataFrame: The log array.
        """
        if not self._log:
            return pd.DataFrame()  # empty
        log = pd.DataFrame(self._log)
        log.columns = ['batch_summary_statistic', 'history_mean', 'history_std', self.ALERT_COL_NAME]
        log = log.astype({self.ALERT_COL_NAME: int})  # convert alert column to int
        if np.isnan(log.to_numpy()).any():
            raise RuntimeError('Problems with log formatting.')
        return log


if __name__ == '__main__':
    from cdcstream import tools


    N_BATCHES = 50
    tools.manage_jvm_start()


    # instatiate drift detector
    def alert_cbck(alert_code, alert_msg):
        if not alert_msg:
            alert_msg = 'no msg'
        print(f'{alert_msg} (code {alert_code})')

    c = CDCStream(
        alert_callback=alert_cbck,
        summary_extractor=dilca_workflow,
        summary_extractor_args={'nominal_cols': 'all'},
        factor_warn=2.0,
        factor_change=3.0,
        factor_std_extr_forg=0,
        cooldown_cycles=0
    )

    # create random data (will be interpreted as being nominal)
    batches = []
    for i in range(N_BATCHES):
        batches.append(
            pd.DataFrame(np.random.randint(1, 10, size=(10,5)))
        )

    # employ created data as stream and feed it to drift detector
    for b in batches:
        c.feed_new_batch(b)

    tools.manage_jvm_stop()

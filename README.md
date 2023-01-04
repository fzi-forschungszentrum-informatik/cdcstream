# Change Detection in Categorical Evolving Data Streams - CDCStream

Implementation of an augmented version of Dino Ienco's algorithm CDCStream ([https://doi.org/10.1145/2554850.2554864](https://doi.org/10.1145/2554850.2554864)).

Cite as TODO(Bibtex info).

## Installation
### Requirements
* WEKA v3.8.6 or greater: [Installation](https://waikato.github.io/weka-wiki/downloading_weka/), [GitHub](https://github.com/Waikato/weka-3.8/)
  * Without this requirement, **code execution fails**.
* Java
  * Download and install Java 11 OpenJDK 11, e.g. from [RedHat](https://developers.redhat.com/products/openjdk/download) (more recent versions might work as well).
  * Note that I experienced issues using Temurin (via adoptium.net).
  * Make sure that the Java folder (path ending in `/bin`) is added to environment variable PATH.
  * Without this requirement, attempting to **install package javabridge might fail**.
* Build tools
  * Ubuntu: Based on the [python-weka-wrapper3 documentation](https://fracpete.github.io/python-weka-wrapper3/install.html#ubuntu), fulfill build requirements.
    ```sh
    sudo apt-get install build-essential python3-dev
    ```
  * Windows: Microsoft Visual C++ 14.0 or greater. For this, [download Build Tools from Microsoft](https://visualstudio.microsoft.com/de/visual-cpp-build-tools/) and install those (installation of Core Features for C++ Build Tools, C++ 2019 Redistributable Update, Windows 10 SDK and MSVC v142 (or greater) should suffice; a subsequent restart might be necessary).
  * Without these requirements, attempting to **install package javabridge might fail**.
* Python >=3.7

### Setup
* Use pip (**after** installing above-stated requirements!):
  ```sh
  python -m pip install cdcstream
  ```
* @poetry users: trouble installing python-javabridge? --> See [Development section](#development)
* First usage of the cdcstream package should automatically add all required WEKA packages.
  **If this does not succeed**: Manually add package [DilcaDistance](https://weka.sourceforge.io/packageMetaData/DilcaDistance/index.html) v1.0.2 or greater to WEKA:
  * Start WEKA GUI
  * Select `Tools` / `Package manager` and install the latest version of `DilcaDistance` (Dependency [fastCorrBasedFS](https://weka.sourceforge.io/packageMetaData/fastCorrBasedFS/index.html) should be installed after confirming prompted request.); It might be necessary to click the `Toggle load` button with `DilcaDistance` selected in order to get `Yes` in the Loaded column.

## Example

```py
import numpy as np
import pandas as pd
from cdcstream.dilca_wrapper import dilca_workflow
from cdcstream import CDCStream, tools


N_BATCHES = 50
tools.manage_jvm_start()  # start a Java VM in order to integrate WEKA


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

tools.manage_jvm_stop()  # cleanup
```

## Development
* Python poetry
  * strangely, installation of python-javabridge fails with poetry versions > 1.1.15 (at the time of writing, newest poetry version is 1.3.1); this might be related to [PEP 621](https://peps.python.org/pep-0621/) --> a workaround is to install python-javabridge via pip:
    ```sh
    python -m poetry run pip install python-javabridge  # from outside the virtual environment
    ```
## License
Code is copyright to the FZI Research Center for Information Technology and released under the [GNU General Public License v3.0](LICENSE).
All dependencies are copyright to the respective authors and released under the respective licenses.
A copy of these licenses is provided in [LICENSE_LIBRARIES](LICENSE_LIBRARIES).

## Acknowledgements
<img src="doc/bmbf_en.svg" alt="BMBF Logo" height="150">

This software was developed at the FZI Research Center for Information Technology.
The associated research was funded by the German Federal Ministry of Education and Research (grant number: 02K18D033) within the context of the project SEAMLESS.


## To Do
* provide BibTex information
* add tests

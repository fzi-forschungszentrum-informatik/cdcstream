# Change Detection in Categorical Evolving Data Streams - CDCStream

Implementation of an augmented version of Dino Ienco's algorithm CDCStream ([https://doi.org/10.1145/2554850.2554864](https://doi.org/10.1145/2554850.2554864)).

Cite as TODO(Bibtex info).

## Installation
### Requirements
* WEKA v3.8.6 or greater, including OpenJDK 17: [Installation](https://waikato.github.io/weka-wiki/downloading_weka/), [GitHub](https://github.com/Waikato/weka-3.8/)
  * Without these requirements, **code execution fails**.
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
* First usage of the cdcstream package should automatically add all required WEKA packages.
  **If this does not succeed**: Manually add package [DilcaDistance](https://weka.sourceforge.io/packageMetaData/DilcaDistance/index.html) v1.0.2 or greater to WEKA:
  * Start WEKA GUI
  * Select `Tools` / `Package manager` and install the latest version of `DilcaDistance` (Dependency [fastCorrBasedFS](https://weka.sourceforge.io/packageMetaData/fastCorrBasedFS/index.html) should be installed after confirming prompted request.); It might be necessary to click the `Toggle load` button with `DilcaDistance` selected in order to get `Yes` in the Loaded column.

## Development
* Python poetry
  * strangely, installation of python-javabridge fails with poetry versions > 1.1.15 (at the time of writing, newest poetry version is 1.2.1)
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
* publish package to PyPI: as soon as python-weka-wrapper3 publishes 0.2.11
* add tests

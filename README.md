# Change Detection in Categorical Evolving Data Streams - CDCStream

Implementation of Dino Ienco's algorithm CDCStream ([https://doi.org/10.1145/2554850.2554864](https://doi.org/10.1145/2554850.2554864))


## Installation
### Requirements
* Microsoft Visual C++ 14.0 or greater: [Download Build Tools from Microsoft](https://visualstudio.microsoft.com/de/visual-cpp-build-tools/) and restart subsequently
* WEKA v3.8.6 or greater: [Download](https://waikato.github.io/weka-wiki/downloading_weka/), [GitHub](https://github.com/Waikato/weka-3.8/)
  * [Install WEKA via release](https://sourceforge.net/projects/weka/) or build it from scratch (requiring Java-related dependencies not mentioned here).

### Setup this Package
* TODO:(publish to PyPI) Use pip (**after** installing above-stated requirements):
  ```sh
  python -m pip install cdcstream
  ```
* First usage of the cdcstream package should automatically add all required WEKA packages.
  **If this does not succeed**: Manually add package [DilcaDistance](https://weka.sourceforge.io/packageMetaData/DilcaDistance/index.html) v1.0.2 or greater to WEKA:
  * Start WEKA GUI
  * Select `Tools` / `Package manager` and install the latest version of `DilcaDistance` (Dependency [fastCorrBasedFS](https://weka.sourceforge.io/packageMetaData/fastCorrBasedFS/index.html) should be installed after confirming prompted request.); It might be necessary to click the `Toggle load` button with `DilcaDistance` selected in order to get `Yes` in the Loaded column.

## License
This software is licensed under the [MIT license](LICENSE).
All dependencies are copyright to the respective authors and released under the licenses listed in [LICENSE_LIBRARIES](LICENSE_LIBRARIES) TODO.

## Acknowledgements
This software was developed at the FZI Research Center for Information Technology.
The associated research was supported by the German Federal Ministry of Education and Research (grant number: 02K18D033) within the context of the project SEAMLESS.

TODO(add logo) <img src="img/BMBF.jpg" alt="BMBF Logo" height="150" style="padding-right: 20px">

## To Do
* add tests
* evaluate suitability of alternative ways of matrix transfer from WEKA
  * ~~Option 1 - authors of WEKA include my code augmentation~~
  * Option 2 - Upload extension of WEKA package DilcaDistance with my Java code augmentation
  * Option 3 - Provide custom DilcaDistance jar in this repository
    * Build it TODO(add code file)
    * User instruction: Move the resulting `.jar` to (overwrite the existing `.jar`)
      * Windows: `C:\Users\USERNAME\wekafiles\packages\DilcaDistance\DilcaDistance.jar` 
      * Linux-based systems: TODO(path Linux)

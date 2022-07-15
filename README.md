# Change Detection in Categorical Evolving Data Streams - CDCStream

Implementation of Dino Ienco's algorithm CDCStream ([https://doi.org/10.1145/2554850.2554864](https://doi.org/10.1145/2554850.2554864))


## Installation
### Requirements
* Microsoft Visual C++ 14.0 or greater: [Download Build Tools from Microsoft](https://visualstudio.microsoft.com/de/visual-cpp-build-tools/) and restart subsequently
* WEKA v3.8.6 or greater: [Download](https://waikato.github.io/weka-wiki/downloading_weka/), [GitHub](https://github.com/Waikato/weka-3.8/)
  * [Install WEKA via release](https://sourceforge.net/projects/weka/) or build it from scratch (requiring Java-related dependencies not mentioned here).
  * Add package [DilcaDistance](https://weka.sourceforge.io/packageMetaData/DilcaDistance/index.html) v1.0.2 or greater to WEKA:
    * Start WEKA GUI
    * Select `Tools` / `Package manager` and install the latest version of `DilcaDistance` (Dependency [fastCorrBasedFS](https://weka.sourceforge.io/packageMetaData/fastCorrBasedFS/index.html) should be installed after confirming prompted request.); It might be necessary to click the `Toggle load` button with `DilcaDistance` selected in order to get `Yes` in the Loaded column.
  * TODO: Option 0 - use toString based transfer of matricesDilca vector as available in published version of DilcaDistance package
  * TODO: Option 1 - authors of WEKA include my code augmentation
  * TODO: Option 2 - Update using custom DilcaDistance jar
    * Build it TODO(add code file)
    * Move the resulting `.jar` to (overwrite the existing `.jar`)
      * Windows: `C:\Users\USERNAME\wekafiles\packages\DilcaDistance\DilcaDistance.jar` 
      * Linux-based systems: TODO(path Linux)

### Setup this Package
* TODO:(publish to PyPI) Use pip:
  ```sh
  python -m pip install cdcstream
  ```

## To Do
* add tests

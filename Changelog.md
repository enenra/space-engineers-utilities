# Changelog
* Added: Support for using Better FBX importer code in SEUT import.
* Added: Import materials from model XMLs
* Added: Automatic material import from model XMLs during FBX import (only materials defined in that XML, not MaterialRefs)
* Fixed: Empty resizing after export.
* Fixed: Rare issue when fixing scratched materials on import.
* Fixed: Rare issue when grid scale would be changed after export.
* Fixed: Rare issue with MatLib linking / unlinking
* Fixed: Issues with different modes and pre 2.91 Blender.
* Fixed: issues with material creation and pre 2.90 Blender.

# Installation
Refer to the [install guide](https://space-engineers-modding.github.io/modding-reference/tutorials/tools/3d-modelling/seut/setup.html).

# How to Update
1. Open a new, empty, file in Blender.
2. Go to `Edit --> Preferences... --> Add-ons` and remove `Modding: Space Engineers Utilities`.
3. Click `Install...` and select the newly downloaded `space_engineers_utilities_***.zip`.
4. Re-enter the paths in the addon's preferences.
5. Restart Blender.
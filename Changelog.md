# Changelog
* Added: Support for using Better FBX importer code in SEUT import.
* Added: Import materials from model XMLs.
* Added: Ability to customize bounding box color and transparency.
* Improved: Code around creation of subpart empties. Now handles targeted objects better.
* Added: Automatic material import from model XMLs during FBX import (only materials defined in that XML, not MaterialRefs).
* Added: Warning for main- and subpart-scene having different `Grid Export`-settings.
* Changed: Bounding box is no longer displayed in anything but the main scene type.
* Fixed: Empty resizing after export.
* Fixed: Mountpoints not being saved on export if MP mode is still active.
* Fixed: LOD distances not getting patched to new format properly.
* Fixed: Error on export when no highlight object is assigned to a highlight empty.
* Fixed: Export issue when a "myempty.001"-empty existed but not a "myempty".
* Fixed: Rare issue when fixing scratched materials on import.
* Fixed: Rare issue when grid scale would be changed after export.
* Fixed: Rare issue with MatLib linking / unlinking.
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
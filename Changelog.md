# Changelog
* Added: Support for using Better FBX importer code in SEUT import.
* Added: Import materials from model XMLs.
* Added: Ability to customize bounding box color and transparency.
* Added: Ability to export to "medium grid". (Thanks to @dbenson24)
* Improved: Code around creation of subpart empties. Now handles targeted objects better.
* Improved: Clarified functionality of `DECAL` material technique.
* Improved: Export log now outputs the current dev version as well.
* Added: Automatic material import from model XMLs during FBX import (only materials defined in that XML, not MaterialRefs).
* Added: Warning for main- and subpart-scene having different `Grid Export`-settings.
* Changed: Bounding box is no longer displayed in anything but the main scene type.
* Changed: Labeling of SEMREF-button in SEUT Notification panel made more clear.
* Changed #291: Reduced max allowed collision objects to 10 as per Keen change.
* Changed #292: Switched all links to SEMREF to new SEMREF 2.0 website.
* Changed #298: Removed Bounding Box Automatic. It was broken and not useful enough to invest time into fixing.
* Changed #294: Display of Link Subpart Instances button - now has separate functionality to update and to unlink.
* Fixed: Empty resizing after export.
* Fixed: Mountpoints not being saved on export if MP mode is still active.
* Fixed: LOD distances not getting patched to new format properly.
* Fixed: Error on export when no highlight object is assigned to a highlight empty.
* Fixed: Export issue when a "myempty.001"-empty existed but not a "myempty".
* Fixed: Rare issue when fixing scratched materials on import.
* Fixed: Rare issue when grid scale would be changed after export.
* Fixed: Rare issue with MatLib linking / unlinking.
* Fixed: Issues with different modes and pre 2.91 Blender.
* Fixed: Issues with material creation and pre 2.90 Blender.
* Fixed: Simultaneous export not properly correcting for export folder.
* Fixed: Simulatneous export not properly adjusting subtype IDs.
* Fixed: Nonstandard empties getting rescaled on export.
* Fixed: Issue with textpanel empty not working correctly.
* Fixed #283: Enabled mountpoint area creation when a side area is selected.
* Fixed #287: Let users reduce icon render mode camera distance down to 0.
* Fixed #296: Blender crash in some cases after renaming a copied scene.
* Fixed #297: Simulteneous export sometimes did not correctly update the export path.
* Fixed #286: Error when trying to fix scratched materials.

# Installation
Refer to the [install guide](https://space-engineers-modding.github.io/modding-reference/tutorials/tools/3d-modelling/seut/setup.html).

# How to Update
1. Open a new, empty, file in Blender.
2. Go to `Edit --> Preferences... --> Add-ons` and remove `Modding: Space Engineers Utilities`.
3. Click `Install...` and select the newly downloaded `space_engineers_utilities_***.zip`.
4. Re-enter the paths in the addon's preferences.
5. Restart Blender.
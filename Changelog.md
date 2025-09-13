Relevant Milestone: [SEUT 1.2.1](https://github.com/enenra/space-engineers-utilities/milestone/31)

# Changelog
* Added [#381](https://github.com/enenra/space-engineers-utilities/issues/381): New scene type: Generic item. For environment items, hand items, components, etc. (Alpha 1)
* Added [#402](https://github.com/enenra/space-engineers-utilities/issues/402): Option for icon render in character animation scenes. (Alpha 1)
* Added [#410](https://github.com/enenra/space-engineers-utilities/issues/410): Button to copy icon render offset options to all scenes. (Alpha 1)
* Added: Alternative FBX import option in case normal import is broken. (Alpha 3)
* Added: Option to disable character rotation on export. This is needed for characters not based on the male / female skeleton. (Alpha 3)
* Added: Option to disable preserving GLB files on import. (Alpha 2)
* Improved: Added Planet Editor preview sphere.
* Improved: Allow material wind parameters to be set for all material techniques.
* Improved: Material definition export to `XML` now only exports the materials used on the exported object(s).
* Improved: Icon path adjustments during simultaneous export.
* Improved: Added more safeties for empty import from FBX. (Alpha 3)
* Improved: Remap materials duplicate detection. (Alpha 2)
* Improved: Changed FBX import to use GLTF as an intermediary format to fix imported objects being weirdly arranged. ASCII FBX can now also be imported through this workaround. Thanks to @quantum-unicorn for the help on this. (Alpha 1)
* Improved: Remap materials no longer remaps materials that have asset data - to enable local overrides. (Alpha 1)
* Improved: Prevent too long SubtypeIds as they can break SEUT. (Alpha 1)
* Fixed [#421](https://github.com/enenra/space-engineers-utilities/issues/421): Texture Conversion functionality would generate files with `.DDS` extension instead of `.dds`.
* Fixed [#420](https://github.com/enenra/space-engineers-utilities/issues/420): Blender 4.5 import issue.
* Fixed [#418](https://github.com/enenra/space-engineers-utilities/issues/418): Allow relative paths for relevant properties in 4.5 .
* Fixed [#415](https://github.com/enenra/space-engineers-utilities/issues/415): Character export empty scale was messed up. (Alpha 3)
* Fixed [#400](https://github.com/enenra/space-engineers-utilities/issues/400): Center empty SBC output was incorrect. (Alpha 1)
* Fixed [#403](https://github.com/enenra/space-engineers-utilities/issues/403): Broken materials on export with Blender 4.2 . (Alpha 1)
* Fixed [#404](https://github.com/enenra/space-engineers-utilities/issues/404): Bug with non-transparent icon background in Blender 4.2 . (Alpha 1)
* Fixed [#407](https://github.com/enenra/space-engineers-utilities/issues/407): Export error when user has set a custom scripts directory. (Alpha 1)
* Fixed: Planet Editor image output.
* Fixed: Material import sometimes failed when the material did not have a `NG`-texture.
* Fixed: Rotate character option was present in `item`-type scenes. (Alpha 3)
* Fixed: Error in SEUT panel display in asset browser. (Alpha 3)
* Fixed: BBOX display in Blender 4.4 . (Alpha 3)
* Fixed: Some export options were available in scene types that did not support them. (Alpha 3)
* Fixed: SEUT Asset information panel not displaying in Blender 4.3 . (Alpha 2)
* Fixed: Error when initializing scene in Blender 4.3 . (Alpha 2)
* Fixed: SEUT not setting grid scale properly when initializing a scene. (Alpha 2)
* Fixed: SEUT not being able to handle it when the BLEND file was located in the mod folder. (Alpha 2)
* Fixed: Some issues with emptys not being the correct scale. (Alpha 1)
* Fixed: Error when using QuickTool's Mirror and Apply with non-mesh objects. (Alpha 1)

# Installation
Refer to the [install guide](https://spaceengineers.wiki.gg/wiki/Modding/Tutorials/Tools/SEUT/Installation_Guide).

# How to Update
## Manually
1. Open a new, empty, file in Blender.
2. Go to `Edit --> Preferences... --> Add-ons` and remove `Modding: Space Engineers Utilities`.
3. Click `Install...` and select the newly downloaded `space_engineers_utilities_***.zip`.
4. Re-enter the paths in the addon's preferences.
5. Restart Blender.

## With BAU
Closely follow the instructions inside the BAU menu, including restarting Blender after the update is complete.
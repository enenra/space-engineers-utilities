Relevant Milestone: [SEUT 1.2.1](https://github.com/enenra/space-engineers-utilities/milestone/31)

# Changelog
* Added [#381](https://github.com/enenra/space-engineers-utilities/issues/381): New scene type: Generic item. For environment items, hand items, components, etc. (Alpha 1)
* Added [#402](https://github.com/enenra/space-engineers-utilities/issues/402): Option for icon render in character animation scenes. (Alpha 1)
* Added [#410](https://github.com/enenra/space-engineers-utilities/issues/410): Button to copy icon render offset options to all scenes. (Alpha 1)
* Improved: Changed FBX import to use GLTF as an intermediary format to fix imported objects being weirdly arranged. ASCII FBX can now also be imported through this workaround. Thanks to @quantum-unicorn for the help on this. (Alpha 1)
* Improved: Remap materials no longer remaps materials that have asset data - to enable local overrides. (Alpha 1)
* Improved: Prevent too long SubtypeIds as they can break SEUT. (Alpha 1)
* Fixed [#400](https://github.com/enenra/space-engineers-utilities/issues/400): Center empty SBC output was incorrect. (Alpha 1)
* Fixed [#403](https://github.com/enenra/space-engineers-utilities/issues/403): Broken materials on export with Blender 4.2 . (Alpha 1)
* Fixed [#404](https://github.com/enenra/space-engineers-utilities/issues/404): Bug with non-transparent icon background in Blender 4.2 . (Alpha 1)
* Fixed [#407](https://github.com/enenra/space-engineers-utilities/issues/407): Export error when user has set a custom scripts directory. (Alpha 1)
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
Relevant Milestone: [SEUT 1.2.1](https://github.com/enenra/space-engineers-utilities/milestone/31)

# Changelog

* Changed: SEUT now uses the asset tag system to determine if a material is `Vanilla` or `DLC`. The previous toolbar is no longer accessible. The corresponding tags are `is_vanilla` and `is_dlc` and can be set like any other asset tag. (Alpha 1)
* Changed: SEUT now primarily uses the new Blender FBX importer. The GLTF importer is now the alternate mode. (Alpha 1)
* Changed: Icon Render mode now gets its compositing node tree from SEUT assets - which means it can be locally overridden / adjusted. (Alpha 1)
* Changed: Planet Editor SBC maximum values now default to their maximum. (Alpha 1)
* Changed: Minimum supported version of Blender to 5.0 . (Alpha 1)
* Fixed: Various issues around Icon Render mode in Blender 5.0 . (Alpha 1)

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

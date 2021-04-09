# Changelog
* Added #264: Saving tool paths to config file and setting them automatically after a (future) SEUT version update.
* Added #258: Error if "Remap Materials" is used but no MatLib enabled.
* Added #254: "Copy Icon Render Options" button to copy icon render options to all other scenes in the BLEND file.
* Added #250: Better error handling for faulty Havok installation.
* Added #248: Better error handling for missing Assimp32.dll .
* Added #246: Missing materials `ScreenArea90`, `ScreenArea180` and `ScreenArea270`.
* Added #245: Option to replace scratched textures on imported FBX on import.
* Added #241: "Complete Import" button, which attempts to import all BS, LOD, BS_LOD FBX models into the current scene.
* Added #240: Automatically color SEUT collections if on Blender version 2.91 or higher.
* Added #239: Implemented support for individual collision models per main and BS models.
* Added #235: Functionality to import materials from XML MaterialLibs.
* Added #228: Support for multiple highlight objects per highlight empty.
* Added #215: Implemented support for unlimited LOD, BS and BS_LOD models. 
* Added: `SEUT Notifications`-button to main panel. Displays the latest SEUT-generated notifications. Is red when an error appeared.
* Added: Better error handling for ASCII FBX import, UVM error on export (#236), Havok error on export (#237).
* Added: Proper support for dev mode and releasing SEUT dev versions.
* Added: `emitter` dummy for exhaust-type blocks.
* Added: `RotatingLightDummy` subpart empty type.
* Added: SEUT now automatically sorts collections in Outliner when "Recreate Collections" is pressed. Also in some other scenarios.
* Added: Warning when exporting a model using DLC materials.
* Added: `FOLIAGE` Material Technique.
* Added: Integration of BAU - Blender Addon Updater.
* Added: SEUT now saves the paths in the Addon Preferences to a config file and loads them from there if the addon is updated.
* Improved: Main collection is set to active after scene is initialized.
* Improved: Selecting a file inside the `Materials`-folder will still correctly set the `Materials` path.
* Changed #255: MP and BS numbers now formatted in 0.00-style in SBC.
* Changed #239: Internal collection handling has been reworked significantly.
* Changed: Massive rework of the SEUT texture system. No changes ingame but significant improvements for texture creation and maintainability. All MatLibs have been converted to the new format.
* Changed: `MatLib_Presets` is no longer required and is removed from `SEUT.zip`.
* Changed: Mountpoint and Mirroring information objects are now locked and not selectable.
* Changed: Scenes without initialized SEUT are skipped during `Export All Scenes`.
* Changed: Lights and cameras in `Main` collection can be unparented.
* Changed: Linked subparts are now locked & protected as a safety measure and to prevent potential duplication issues.
* Fixed #267: Missing dummies `conveyorline_small_in` and `conveyorline_small_out`.
* Fixed #257: Fix scratched materials option for import would sometimes do the opposite.
* Fixed #256: In some cases, empties would still have .001 etc. numbers in their names.
* Fixed #253: Various issues with simultaneous export, mainly with exporting both sizes to a single folder.
* Fixed #251: Error on preset subpart creation with no selected object.
* Fixed #243: Rare error when adding dummy.
* Fixed #242: Modes were not toggled off before export.
* Fixed #238: Bug when using Copy Settings when creating a new scene.
* Fixed: Link Subparts sometimes not showing subparts correctly - thanks derekt!
* Fixed: `GenericGlass` material displaying as pink initially.
* Fixed: `Link Subpart Instances` still being displayed in `Character Animation`-type scenes.
* Fixed: Textpanel empty was not set to use index.
* Fixed: Issue with highlight and subpart empties not being connected properly on import.
* Fixed: Rare issue where icon wouldn't be rendered.
* Fixed: Error when trying to display certain warning or error messages.

# Installation
Refer to the [install guide](https://space-engineers-modding.github.io/modding-reference/tutorials/tools/3d-modelling/seut/setup.html).

# How to Update
1. Open a new, empty, file in Blender.
2. Go to `Edit --> Preferences... --> Add-ons` and remove `Modding: Space Engineers Utilities`.
3. Click `Install...` and select the newly downloaded `space_engineers_utilities_***.zip`.
4. Re-enter the paths in the addon's preferences.
5. Restart Blender.

# Notes
MatLibs have been updated. No need for running texture conversion again but make sure to replace your existing MatLibs with the ones contained in `SEUT.zip`.
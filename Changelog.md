# Changelog
* Added #317: API caching to prevent "Rate Limit exceeded!"-errors. (Beta 1)
* Added #306: Config files for empty-type storage to `SEUT Assets`. (Beta 1)
* Added #300: Button to export Blender logs for easy issue search. (Beta 1)
* Improved #321: Asset dir is not allowed to be set as game directory or SDK directory. (Beta 1)
* Improved #320: Setting Game directory should check for presence of game `EXE`-file. (Beta 1)
* Improved #318: Characters and character animations default pathing improved. (Beta 1)
* Improved #316: New `SBC` files are numbered correctly. (Beta 1)
* Improved #315: Conversion of `NG`-textures to `TIF`. (Beta 1)
* Improved #303: Specify why materials cannot be exported on button hover. (Beta 1)
* Improved #266: Allow for instancing of character animation scenes under the `dummy_character`-empty. (Beta 1)
* Improved: Don't write texture references for `HOLO` and `GLASS`-technique materials to xml. (Beta 1)
* Improved: Simple Navigation no longer affects Render, Mirroring or Mountpoint-collections. (Beta 1)
* Improved: Logic to find parent collection of object. (Beta 1)
* Improved: `ALPHA_MASKED`-technique for materials also supports wind-parameters. (Beta 1)
* Improved: Change to `HKO` file that should let users rotate rigidbody shapes. (Beta 1)
* Improved: Display current version of `SEUT Assets` and `MWMBuilder` in Addon Preferences. (Beta 1)
* Improved: Icon render path should display absolute path in success message. (Beta 1)
* Improved: Highlight description for SEUT Asset Browser parameters. (Beta 1)
* Improved: Time needed to convert textures in seconds was not rounded. (Beta 1)
* Fixed #324: Highlight empty without target getting rescaled on export. (Beta 1)
* Fixed #322: Various issues with automatic texture conversion to `DDS` on model export. (Beta 1)
* Fixed #319: Error during export of character scene. (Beta 1)
* Fixed #313: Error during error handling of UVM issue. (Beta 1)
* Fixed #312: Image nodes that do not contain images should be ignored. (Beta 1)
* Fixed #311: Issue where MaxRequests was exceeded. (Beta 1)
* Fixed: Build stage collections not using correct collisions until reload. (Beta 2)
* Fixed: Rare issue where SEUT version could not be parsed. (Beta 1)
* Fixed: Error during creation of highlight empty. (Beta 1)
* Fixed: Materials with wind-parameters not being imported properly. (Beta 1)
* Fixed: Wind material parameters not being rounded on export. (Beta 1)
* Fixed: `vent`-dummy not being named correctly. (Beta 1)
* Fixed: Issue during collection creation when `SEUT`-collection was selected. (Beta 1)
* Fixed: UVM-warning cancelling export instead of UVM-error. (Beta 1)
* Fixed: Rare issue with `BLEND` patching of scenes containing unsupported collection types. (Beta 1)
* Fixed: Turning off color overlay for icons not applying correctly. (Beta 1)

# Installation
Refer to the [install guide](https://space-engineers-modding.github.io/modding-reference/tutorials/tools/3d-modelling/seut/setup.html).

# How to Update
1. Open a new, empty, file in Blender.
2. Go to `Edit --> Preferences... --> Add-ons` and remove `Modding: Space Engineers Utilities`.
3. Click `Install...` and select the newly downloaded `space_engineers_utilities_***.zip`.
4. Re-enter the paths in the addon's preferences.
5. Restart Blender.
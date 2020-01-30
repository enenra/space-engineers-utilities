# Space Engineers Utilities
A Blender 2.8+ addon.

## Features
* Full Blender 2.8+ integration using collections instead of layers
* Spawn dummies, highlight empties and subparts directly from the context menu
* See full SE materials in Blender, as close to how they appear in the game as possible
* Create your own custom materials in Blender from presets
* Vanilla materials of imported FBX are automatically switched to make them display correctly
* Empties on imported FBX are automatically switched to cube display
* Set LOD distances directly in the UI
* Change grid scale between large and small grid directly
* See bounding box of block (respects grid scale setting)
* Exports collision model
* Exports basic CubeBlocks entry
* Exports directly to MWM
* HKT is automatically rescaled with rescalefactor along with rest of model
* Support for Blender files with multiple scenes
* Structure conversion to convert BLEND files created with the old plugin to the new structure
* Support for Build Stage LOD
* Empty target objects can be set in dedicated panel
* Subpart scenes within the same file can be instanced into their parent scenes
* Full multi-scene support

## Installation
1. Download the latest release of the addon from the releases section, enable it in Blender.
2. Download the supplementary ZIP (SEUT.zip) containing additional required files.
3. Ensure you have downloaded the Space Engineers Mod SDK. (Library --> Enable tool display --> Space Engineers Mod SDK in your available games list)
4. Unpack the supplementary ZIP file onto a drive with ~15GB available disk space. (for the unpacked textures)
5. Within the resulting directory you should have the following structure:
```
SEUT\Materials\
SEUT\Tools\
SEUT\convert_textures.bat
```
5. Download [Eikester's MWM Builder](https://forum.keenswh.com/threads/mwmbuilder-fixes.7391806/) and place it into `SEUT\Tools\MWMB\`.
6. Download Harag's [Custom FBX Importer](https://github.com/harag-on-steam/fbximporter/releases/tag/havok2013.1-fbx2015.1) and place it into `SEUT\Tools\`.
7. Download the Havok Content Tools ([64bit](https://drive.google.com/open?id=1bXqAcIvzTHpxuAcMogduHqohL0zXq90i)/[32bit](https://drive.google.com/open?id=1DL3-evI3LSIstVTjYvjw01rtpI3iAhDh)) and install them to `SEUT\Tools\Havok\`.
8. Run the BAT file. Point it at the correct folder for your SE installation and SE Mod SDK's `texconv.exe`
9. Once the textures are unpacked, you should have the following structure:
```
SEUT\Materials\
SEUT\Textures\
SEUT\Tools\
SEUT\convert_textures.bat
```
10. In Blender, use File --> Link and navigate to the MatLib_*.blend files within the `SEUT\Materials\`-folder. Select `MatLib_Materials.blend` and link all its contained materials. Do the same for `MatLib_Armors.blend` and `MatLib_Items.blend`. You likely won't usually need the remaining ones.
11. Go to Edit --> Preferences --> Add-ons --> Scene: Space Engineers Utilities and set the paths to the respective folders and files within `SEUT\`.
12. Open the Toolbar in Blender by pressing `N` in the 3D View or Node Editor. Access Empty spawning by right-clicking into the 3D View.

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
* Export material library to XML
* Link MatLibs directly from the UI
* Warning when empties are set up in a way that won't work ingame
* Rotate empties in mirroring-mode to output mirror information to the SBC
* Create new character models
* Create new character animations and poses
* Define mountpoints by placing areas on the six sides of the bounding box in mountpoint-mode

## Installation
1. Download the latest release of the addon from the releases section, enable it in Blender.
2. Download the supplementary ZIP (SEUT.zip) containing additional required files.
3. Ensure you have downloaded the Space Engineers Mod SDK. (Library --> Enable tool display --> Space Engineers Mod SDK in your available games list)
4. Unpack the supplementary ZIP file onto a drive with ~15GB available disk space. (for the unpacked textures)
5. Within the resulting directory you should have the following structure:
```
SEUT\Materials\
SEUT\Textures\
SEUT\Tools\
```
5. Download [Stollie's MWM Builder](https://github.com/cstahlhut/MWMBuilder/releases) (StollieMWMBuilder.rar) and unzip it into `SEUT\Tools\MWMB\`.
6. Download Harag's [Custom FBX Importer](https://github.com/harag-on-steam/fbximporter/releases/tag/havok2013.1-fbx2015.1) and place it into `SEUT\Tools\`.
7. Download the Havok Content Tools ([64bit](https://drive.google.com/open?id=1bXqAcIvzTHpxuAcMogduHqohL0zXq90i)/[32bit](https://drive.google.com/open?id=1DL3-evI3LSIstVTjYvjw01rtpI3iAhDh)) and install them to `SEUT\Tools\Havok\`.
8. Run `bulkTexConverter.exe`. Point it at the correct folders for your SE installation, SEUT Tools folder and SEUT Textures folder and load presets by using File --> Load Presets. Then run the conversion.
9. In Blender, go to Edit --> Preferences --> Add-ons --> Scene: Space Engineers Utilities and set the paths to the respective folders and files within `SEUT\`.
10. Open the Toolbar in Blender by pressing `N` in the 3D View or Node Editor. Access Empty spawning by right-clicking into the 3D View.
11. In the `N`-toolbar within the Node Editor / Shader Editor, enable `MatLib_Presets.blend`. Also enable any of the other `MatLib_*`-files to link their materials into the current file.

## Support	
Please consider supporting the development of this addon by becoming one of Stollie's patreons! Without him, the development of the addon would never have gotten this far.	

[![](https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/Patreon_logo_with_wordmark.svg/512px-Patreon_logo_with_wordmark.svg.png)](https://www.patreon.com/Stollie)	

## Credits	
* **Stollie** - So much general help but also writing everything character, export and MWM-related, which I wouldn't have been able to do at all.	
* **Harag** - Writing the [original Blender SE plugin](https://github.com/harag-on-steam/se-blender). A lot of code in this addon is based on his.	
* **Wizard Lizard** - For hours of testing as well as writing the [SE Texture Converter](https://github.com/TheWizardLizard/SETextureConverter) to save us all from having to deal with batch files.
* **Kamikaze (Blender Discord)** - Writing the `remapMaterials()`-function and generally helping out constantly by answering a lot of questions.
* **CGCookie** - For the creation of the fantastic [Blender Addon Updater](https://github.com/CGCookie/blender-addon-updater) that is being used for SEUT.

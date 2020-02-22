---
layout: default
---

[Home](./index.html) | [Download](./download.html) | **Installation** | [Documentation](./documentation.html) | [Report Issue](https://github.com/enenra/space-engineers-utilities/issues/new) | [About](./about.html)

# Installation
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
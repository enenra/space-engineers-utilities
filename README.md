# Space Engineers Utilities
A Blender 2.8+ addon to streamline working on assets for Space Engineers.

## Features
### Blender
* **Full Blender 2.8+ support** using collections to organize models.
* **Simple Navigation** to easily edit models one collection at a time.
* Robust **error handling** and extensive **feedback** to help you avoid issues further down the road and inform you **if and what** is the problem.
* Full support for **multiple scenes** per BLEND file.
* Set the **grid scale** to preset Space Engineers values to easily see the size of your model.
* Through a **Addon Auto Updater** the addon will notify the user of newly released versions.

##### Modes
* Use **Bounding Box Mode** to define the bounding box of your model.
* **Mirroring Mode** allows for easy setup of mirroring for blocks.
* By using **Mountpoint Mode** the user can define the mountpoints on a block in a straightforward manner.
* Use **Icon Render Mode** to easily create icons for your blocks in the style of vanilla Space Engineers blocks.

### Import
* Import Space Engineers **FBX files** through the addon to automatically display its materials in Blender.
* **Structure Conversion** functionality allows for easy conversion of BLEND files created with the old 2.7x plugin to the new format.

### Materials
* **Displays** most vanilla Space Engineers materials **directly in Blender**.
* Contains **Material Libraries** with most vanilla materials, ready to apply to new models.
* Create **your own** Space Engineers materials.
* Create **your own Material Libraries**.

### Empties
* **Subparts are instanced** into other scenes to show how the model will look ingame.
* Easily **create and manage** empties for different purposes by selecting from exhaustive lists.

### Export
* Define a **RescaleFactor** to easily convert your large grid models to small grid.
* Define **LOD Distances** to set from which distance your LOD models are displayed.
* Directly export to **MWM**-format, ready to be loaded into the game.
* Additional definitions are exported to a **CubeBlocks** file.
* Full support for creating **character models** and **character poses & animations**.

## Installation
Please follow the [installation guide](https://space-engineers-modding.github.io/modding-reference/tutorials/tools/3d-modelling/seut/setup.html).

## Support	
Please consider supporting the development of this addon by becoming one of Stollie's patreons! Without him, the development of the addon would never have gotten this far.	

[![](https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/Patreon_logo_with_wordmark.svg/256px-Patreon_logo_with_wordmark.svg.png)](https://www.patreon.com/Stollie)

## Credits	
* **Stollie** - So much general help but also writing everything character, export and MWM-related, which I wouldn't have been able to do at all.	
* **Harag** - Writing the [original Blender SE plugin](https://github.com/harag-on-steam/se-blender). A lot of code in this addon is based on his.	
* **Wizard Lizard** - For hours of testing as well as writing the [SE Texture Converter](https://github.com/TheWizardLizard/SETextureConverter) to save us all from having to deal with batch files.
* **Kamikaze (Blender Discord)** - Writing the `remapMaterials()`-function and generally helping out constantly by answering a lot of questions.
* **CGCookie** - For the creation of the fantastic [Blender Addon Updater](https://github.com/CGCookie/blender-addon-updater) that is being used for SEUT.

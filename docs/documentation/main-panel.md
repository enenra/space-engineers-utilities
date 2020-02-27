---
layout: default
---

[Home](../index.html) | [Download](../download.html) | [Installation](../installation.html) | **Documentation** | [Troubleshooting](../troubleshooting.html) | [About](../about.html)

---

**[Documentation](../documentation.html)** | [Tutorials](../tutorials.html)

---

**Main Panel** | [Node Editor Panel](./node-editor-panel.html) | [Context / Add Menu](./context-menu.html) | [Object Properties](./object-properties.html) | [Preferences](./preferences.html) 

# Main Panel
The main SEUT panel holds the vast majority of the functionality of the addon. It can be found on the right side of the `3D Viewport` (button marked in green) of Blender and opened by pressing `N` while the cursor is within the viewport.

![](../assets/images/main-panel.png)

---

## Space Engineers Utilities
![](../assets/images/main-panel_1.png)

### MyAwesomeBlock
This is the scene name that is synced with the SubtypeId.

### Type
Allows selection of scene type. Depending on the scene type, a scene is **exported differently** and certain **functionality becomes available**. Valid types are:

* **Main** - This is the default scene type. Most of your scenes will be of this type.
* **Subpart** - This scene contains a subpart that is part of a `Main` scene. Refer to the [Subpart Tutorial]() to learn how to use subparts.
* **Mirroring** - This scene is the mirror model for another scene. Refer to the [Mirroring Tutorial]() for more details.
* **Character** - This scene contains a character model. It is treated in a specific way by the exporter to make it appear correctly ingame. Refer to the [Character Modding Tutorial]() for further details.
* **Character Animation** - This scene contains either a character pose or character animation and is treated differently by the exporter. Refer to the [Character Modding Tutorial]() for further details.

### SubtypeId
The SubtypeId is your model's **unique identifier**. It is written both into the `SBC` as well as written into the filename of the exported models. In scenes of type `Subpart`, `Character` and `Character Animation` it only defines the filename as no `SBC` is created for these on export.
The SubtypeId is furthermore used to **mark all collections** belonging to a scene so that they can be differntiated from same-function collections in other scenes.

| **Note:** SubtypeId **must be unique within a blend file**. Measures have been implemented to ensure that it is but there's still a small chance of it happening. If it does happen, undo to before it did. |

### Grid Scale
This option sets your Blender grid to align to the size of either large or small grid *within Space Engineers*. The grid is set to half the size of either to allow you to **correctly place the blocks** on world origin in Blender.
This setting is also used to by the addon to adjust what gets **written to the SBC** as well as to **scale the bounding box** so make sure it's set to the correct scale for your block.

### Recreate Collections
This button will create the various collections SEUT uses to **organize your models** within the active scene. The addon requires you to place **all objects** it should handle **within one of these collections**.

### Simple Navigation
By default, because SEUT relies on collections to organize your model, you will be switching between collections fairly often. However, generally you'll only really want to look at the contents of a single collection at a time. Enabling this option will **hide all non-active collections** automatically. Thus, whenever you click on another of the SEUT collections, it will be unhidden and all other collections will be hidden in turn.

---

## Bounding Box
![](./../assets/images/bounding-box_1.png)

The bounding box **indicates the size of the block** inside Space Engineers. Be sure to adjust it so all of your block is within it (unless in some special cases). 

| **Note:** Especially the entirety of the collision model must be within the bounding box - otherwise the block will revert to cube collision. |

### Size
Use the `X`, `Y` and `Z`-properties to adjust the size of the bounding box. These values are written to the SBC.

### Automatic
This button will make the addon attempt to automatically set the bounding box to encompass the entire geometry. It is currently not very accurate.

---

## Mirroring Mode
![](./../assets/images/mirror-mode_1.png)

Mirroring Mode is used to set up block mirroring options within Space Engineers. Its results are written to the SBC. Refer to the [Mirroring Tutorial]() for more details.

### Model
This links to a `Mirroring`-type scene, which is used instead of an instance of the normal model contained within the `Main`-collection for mirroring display.

---

## Mountpoint Mode
![](./../assets/images/mountpoint-mode_1.png)

Mountpoint Mode allows the user to define the **areas of the block** that **attach to other blocks**. Mountpoints are divided by the block's `Sides`. Each `Side` can have multiple defined `Areas` that are valid attachment points.Refer to the [Mountpoint Tutorial]() for more details.

### Side
Select one of the six sides of the block as a target for the `Add Area`-button.

### Add Area
Adds a new area to a side that can be repositioned and rescaled (rotation is not saved).

---

## Icon Render Mode
![](./../assets/images/icon-render-mode_1.png)

Icon Render Mode allows the easy rendering of icons for a block.

### Render
This button will save the current camera view as a render to the specified `Output Path`. It will only render the scene's `Main`-collection.

### Zoom
This property adjusts the camera's zoom level.

### Rotation
These properties allow for the rotation of the camera and lighting setup around the point of origin.

### Color Overlay
Untoggling this property will remove the blue tint from the resulting icon render.

### Resolution
Sets the resolution in pixels of the resulting render.

### File Format
Sets the file format of the resulting image.

### Output Path
Sets the path to which the render will be saved when `Render` is pressed.

---

## Export
![](./../assets/images/export_1.png)

### Export All Scenes
This button will iterate through all scenes and their collections within the `BLEND`-file and export them one by one. 

### Export Current Scene
Exports all collections within the current scene.

### Delete Loose Files
By default, the only files resulting from export are the `SBC` and `MWM` files, as all **intermediary files are automatically cleaned up**. Untoggling this option will prevent these "loose files" from being cleaned up and thus allows for debugging issues.

### Rescale Factor
The rescale factor allows for the rescaling of the exported models. A large grid block can be exported as a small grid block by setting this value to `0.2`.

| **Note:** Don't forget to change your SubtypeId before exporting a small grid version of your block or it will overwrite your previously exported large grid version. |

### Export Folder
The directory to export your model to. Must contain `Models\` in its path to be eligible. Set this to directly export into your mod's directory.

#### Copy Export Folder
This button copies the current `Export Folder` to all other scenes within the `BLEND`-file.

---

## Import
![](./../assets/images/import_1.png)

### Import FBX
This button allows for the import of FBX files. Imported geometry is automatically processed further, thus it is heavily recommended to use this button over the default Blender FBX import option.

### Display Empties as 'Cube'

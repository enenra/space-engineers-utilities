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

## Space Engineers Utilities
![](../assets/images/main-panel_1.png)

### MyAwesomeBlock
This is the scene name that is synced with the SubtypeId.

### Type
Allows selection of scene type. Depending on the scene type, a scene is exported differently and certain functionality becomes available. Valid types are:

* **Main** - This is the default scene type. Most of your scenes will be of this type.
* **Subpart** - This scene contains a subpart that is part of a `Main` scene. Refer to the [Subpart Tutorial]() to learn how to use subparts.
* **Mirroring** - This scene is the mirror model for another scene. Refer to the [Mirroring Tutorial]() for more details.
* **Character** - This scene contains a character model. It is treated in a specific way by the exporter to make it appear correctly ingame. Refer to the [Character Modding Tutorial]() for further details.
* **Character Animation** - This scene contains either a character pose or character animation and is treated differently by the exporter. Refer to the [Character Modding Tutorial]() for further details.

### SubtypeId
The SubtypeId is your model's unique identifier. It is written both into the SBC as well as written into the filename of the exported models. In scenes of type `Subpart`, `Character` and `Character Animation` it only defines the filename as no SBC is created for these on export.
The SubtypeId is furthermore used to mark all collections belonging to a scene so that they can be differntiated from same-function collections in other scenes.

| **Note:** SubtypeId must be unique within a blend file. Measures have been implemented to ensure that it is but there's still a small chance of it happening. If it does happen, undo to before it did. |

### Grid Scale


## Bounding Box
![](./../assets/images/bounding-box_1.png)

## Mirroring Mode
![](./../assets/images/mirror-mode_1.png)

## Mountpoint Mode
![](./../assets/images/mountpoint-mode_1.png)

## Icon Render Mode
![](./../assets/images/icon-render-mode_1.png)

## Export
![](./../assets/images/export_1.png)

## Import
![](./../assets/images/import_1.png)
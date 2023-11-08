Relevant Milestone: [SEUT 1.2.0](https://github.com/enenra/space-engineers-utilities/milestone/30)

# Changelog
* Added [#13](https://github.com/enenra/space-engineers-utilities/issues/13): Animation support. Create and export animations with Blender and SEUT to use with the [Animation Engine by Math0424](https://steamcommunity.com/sharedfiles/filedetails/?id=2880317963). (Alpha 1)
* Added: `SEUT QuickTools` - shortcuts for various commonly used actions when making SE models. (Alpha 1)
* Added: Checkboxes to `Addon Preferences` to enable `Quick Tools` and `Animation Support`. (Alpha 1)
* Improved [#373](https://github.com/enenra/space-engineers-utilities/issues/373): Added error for incompatible physics shape (`COMPOUND`). (Alpha 1)
* Improved [#374](https://github.com/enenra/space-engineers-utilities/issues/374): Added warning for exporting to a different grid size than scene is set to while subpart empties are present. (Alpha 1)
* Improved [#375](https://github.com/enenra/space-engineers-utilities/issues/375): Ignore Collision collections that are not associated with a main or BS collection. (Alpha 1)
* Improved [#376](https://github.com/enenra/space-engineers-utilities/issues/376): Added error for trying to launch `Mountpoint` or `Mirror Mode` while not having set an `Asset` path.(Alpha 1)
* Improved: Export errors now properly interrupt the entire export process. (Alpha 1)
* Improved: Switched material technique error to warning. (Alpha 1)
* Improved: The way some error messages would display empty paths. (Alpha 1)
* Changed [#371](https://github.com/enenra/space-engineers-utilities/issues/371) & [#372](https://github.com/enenra/space-engineers-utilities/issues/372): Updated the way the `Bounding Box` is drawn to ensure Blender 4.0 compatibility. (Alpha 1)
* Fixed [#378](https://github.com/enenra/space-engineers-utilities/issues/378): BAU would not offer to update to a newer release version if user was on a dev version. (Alpha 1)
* Fixed: Longstanding bug that would lead to subpart duplication. (Alpha 1)
* Fixed: Issue where icon render would create folders named after files. (Alpha 1)
* Fixed: SBC export icon path not being able to handle `PNG` icons. (Alpha 1)
* Fixed: `Complete Import` not setting `HKT` path correctly. (Alpha 1)
* Fixed: Issue during SEUT patching process. (Alpha 1)
* Fixed: Issue during `Planet Editor` baking process when image nodes were not present in materials. (Alpha 1)

# Installation
Refer to the [install guide](https://semref.atlassian.net/wiki/spaces/tutorials/pages/131411/SEUT+Installation+Guide).

# How to Update
## Manually
1. Open a new, empty, file in Blender.
2. Go to `Edit --> Preferences... --> Add-ons` and remove `Modding: Space Engineers Utilities`.
3. Click `Install...` and select the newly downloaded `space_engineers_utilities_***.zip`.
4. Re-enter the paths in the addon's preferences.
5. Restart Blender.

## With BAU
Closely follow the instructions inside the BAU menu, including restarting Blender after the update is complete.
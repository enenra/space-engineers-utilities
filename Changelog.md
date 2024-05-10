Relevant Milestone: [SEUT 1.2.0](https://github.com/enenra/space-engineers-utilities/milestone/30)

# Changelog
* Added [#379](https://github.com/enenra/space-engineers-utilities/issues/379): Mark unpainted and ungrouped vertices in groups. (RC 1)
* Added: `SEUT QuickTools` - shortcuts for various commonly used actions when making SE models. (Beta 1)
* Added: Material variation dropdown menu, allowing the user to quickly switch between versions of a material. (RC 1)
* Added: Checkboxes to `Addon Preferences` to enable `Quick Tools` and `Animation Support`. (Beta 1)
* Changed: Switched all documentation links to instead link to the new [Space Engineers Official Wiki](https://spaceengineers.wiki.gg/). SEMREF will be retired, but all its content has been migrated to the SE wiki. (RC 1)
* Improved [#373](https://github.com/enenra/space-engineers-utilities/issues/373): Added error for incompatible physics shape (`COMPOUND`). (Beta 1)
* Improved [#374](https://github.com/enenra/space-engineers-utilities/issues/374): Added warning for exporting to a different grid size than scene is set to while subpart empties are present. (Beta 1)
* Improved [#375](https://github.com/enenra/space-engineers-utilities/issues/375): Ignore Collision collections that are not associated with a main or BS collection. (Beta 1)
* Improved [#376](https://github.com/enenra/space-engineers-utilities/issues/376): Added error for trying to launch `Mountpoint` or `Mirror Mode` while not having set an `Asset` path.(Beta 1)
* Improved: Channel settings on imported images. (RC 1)
* Improved: Paint Color handling. This will unfortunately reset all paint color in your exisitng `BLEND`-files. (RC 1)
* Improved: Sum up imported materials instead of reporting them one by one. (RC 1)
* Improved: Export errors now properly interrupt the entire export process. (Beta 1)
* Improved: Switched material technique error to warning. (Beta 1)
* Improved: The way some error messages would display empty paths. (Beta 1)
* Improved: Warning when using outdated version of Blender. (Beta 2)
* Changed [#371](https://github.com/enenra/space-engineers-utilities/issues/371) & [#372](https://github.com/enenra/space-engineers-utilities/issues/372): Updated the way the `Bounding Box` is drawn to ensure Blender 4.0 compatibility. (Beta 1)
* Fixed [#378](https://github.com/enenra/space-engineers-utilities/issues/378): BAU would not offer to update to a newer release version if user was on a dev version. (Beta 1)
* Fixed: Paths in exported logs sometimes not getting properly anonymized. (RC 1)
* Fixed: `SEUT Material` being remapped to a linked one. (RC 1)
* Fixed: Remap Materials sometimes erroring. (RC 1)
* Fixed: Missing character weighting error not triggering (RC 1)
* Fixed: Longstanding bug that would lead to subpart duplication. (Beta 1)
* Fixed: Issue where icon render would create folders named after files. (Beta 1)
* Fixed: SBC export icon path not being able to handle `PNG` icons. (Beta 1)
* Fixed: `Complete Import` not setting `HKT` path correctly. (Beta 1)
* Fixed: Issue during SEUT patching process. (Beta 1)
* Fixed: Issue during `Planet Editor` baking process when image nodes were not present in materials. (Beta 1)
* Fixed: Export error with Blender 4.0 . (Beta 1)

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
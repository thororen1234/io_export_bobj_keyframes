# BOBJ keyframe Blender exporter add-on

This is resository is contains a Blender3d add-on that adds a menu item in the File > Export called `BOBJ keyframes`. With this add-on you can export BOBJ keyframes to be used with Emoticons mod.

## How to install

Download this as zip, then in Blender's Preferences > Get Extensions (or Add-ons) panel, use "Install from Disk..." and choose the downloaded zip. That should install this exporter script.

Note: this `master` branch packages the add-on as a Blender Extension (`blender_manifest.toml`) and targets Blender **5.2+**. For older Blender, use the `2.8` branch (2.80-5.2, legacy add-on) or the `2.7` branch (2.7x).

## How to use

Once you animated some actions, you can use this add-ons' File > Export > `BOBJ keyframes` menu item to generate a BOBJ file with keyframe data. Export it to Minecraft's `config/emoticons/emotes/` under any filename (don't modify the file extension though).

**If you made some emotes, and want them to be accessible in the emote configuration menu**, then create a file by the same name, but with JSON extension (`test.bobj` becomes `test.json`), and for every `emote_` action you created (every emote animation must begin with `emote_`) define title and description:

```json
{
 "cool_dance": {
  "looping": true,
  "title": "Cool Dance",
  "description": "Very cool dance"
 },
 "superhero_pose": {
  "title": "Supehero Pose",
  "description": "\"I'm a superhero\""
 },
 "worm": {
  "looping": true,
  "title": "Worm",
  "description": "Wiggle!" 
 }
}
```

This would be the config if we'd have, let's say, five actions in Blender: `emote_cool_dance`, `emote_superhero_pose`, `emote_worm`, `creeping_walk` and `alt_death`. Once both BOBJ and JSON files are exported and configured, Cool Dance, Superhero Pose and Worm will be available as emotes, while `creeping_walk` and `alt_death` would be available to be used in Actions panel of the Emoticons morph, which you can replace the original walk and death cycles.

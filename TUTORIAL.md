# Squad-VoteTalkLimit Tutorial

**English** · [Türkçe](./TUTORIAL_TR.md) · [Español](./TUTORIAL_ES.md) · [简体中文](./TUTORIAL_ZH.md) · [Русский](./TUTORIAL_RU.md)

[README](./README.md) · [Changelog](./CHANGELOG.md)

This tutorial goes from an empty machine to a finished voice test, in order. Neither variant has been tested on a live server, so the last part is how to test and what to report.

---

## 📑 Contents
1. [Overview](#-overview)
2. [Step by step](#-step-by-step)
3. [Settings](#️-settings)
4. [Reading the test](#-reading-the-test)
5. [Troubleshooting](#-troubleshooting)
6. [Glossary](#-glossary)

---

## 🔭 Overview
### What it does

While the end-of-match map vote and faction vote run, each player has a talk budget. Talking spends it, silence refills it. When it is empty the player is muted for a short time, then can talk again. When the vote ends everybody is unmuted.

### How it works

A Blueprint ruleset (`BP_VoteTalkLimit`, parent `SQGameRuleSet`) runs on the server. Each tick it reads the vote state, keeps one number per player (the budget) and decides who is muted. The two variants differ only in how the mute reaches the players:

- `server-only`: the server calls `ToggleMutePlayer` on every listener.
- `client-rpc`: the server spawns `BP_VTLClientHelper`, owned by the speaker's controller. It replicates to that client only. On that client the helper toggles the voice on begin play and toggles it back when it ends. The server sets its lifespan to the mute time and destroys every helper when the vote ends.

### File layout

```
src/mod/server-only/VoteTalkLimit/   mod folder for the server-only variant
src/mod/client-rpc/VoteTalkLimit/    mod folder for the client-rpc variant
src/core/                            graph generators (Python)
tests/integration/                   talk simulations
docs/guides/                         notes
```

---

## 🪜 Step by step
**A. Get the Squad SDK.** Install the Squad SDK (Unreal Editor) and open the `SquadGame` project once so it finishes its first load.

**B. Choose a variant.** Download `VoteTalkLimit-server-only.zip` or `VoteTalkLimit-client-rpc.zip` from the [latest release](https://github.com/Miabeyefendi/Squad-VoteTalkLimit/releases/latest). Use one at a time.

**C. Copy the mod.** Unzip it into `Squad/Plugins/Mods/` inside the SDK. The result is `Squad/Plugins/Mods/VoteTalkLimit/` with a `VoteTalkLimit.mi` file and a `Content` folder.

**D. Open the project.** Start the editor. Open the Content Browser, enable the plugin content folder if needed and find `VoteTalkLimit Content`.

**E. Open the Blueprint.** Double click `BP_VoteTalkLimit`. In the `client-rpc` variant also look at `BP_VTLClientHelper`.

**F. Compile.** Press Compile. The result line must say "successful" with no warnings. If it does not, see [Troubleshooting](#-troubleshooting).

**G. Save.** Save all assets.

**H. Package the mod.** In the Modding Hub open the Share tab and press Package. If it ends with `Cook failed`, use the command in [Troubleshooting](#-troubleshooting). The output holds `Content/Paks/WindowsServer` for the server and `Content/Paks/Windows` for clients.

**I. Upload to the Workshop.** Upload the packaged mod to the Steam Workshop as a private or unlisted item so only your test server can use it.

**J. Add it to ModLoader.** Copy the packaged mod folder into the server's `SquadGame/Plugins/Mods/`, together with the ModLoader mod. Put the `ModLoader_v1` layer first in the rotation and register the ruleset in `SquadGame/Saved/ModLoader/ModLoader.json` (version 2 form, see the README). A mod without a Steam ID (`ID=0` in the `.mi`) is skipped: give it any number for a local test, or upload it as an unlisted item.

**K. Optional settings.** Create or edit `CustomOptions.cfg` in the server config folder. See [Settings](#️-settings).

**L. Restart the server.** Start it and check the log for the mod loading.

**M. Client side (`client-rpc` only).** Players who join download the mod from the Workshop automatically if the server lists it. Check on the test client that the mod is present.

**N. Get a second player.** You need one speaker and one listener on the same team or squad.

**O. Reach a vote.** Play or fast forward a match to the end so the map vote opens.

**P. Speak.** The speaker says a short call again and again without pausing, for example "top mid top mid".

**Q. Listen.** The listener notes when the speaker's voice stops. The speaker notes the messages on screen.

**R. Wait for the mute to end.** After the mute time the speaker should be heard again.

**S. Check the end of the vote.** When the vote ends the speaker must be unmuted at once, even if the mute time is not over.

**T. Check the scoreboard.** On the scoreboard before the votes, nobody may be limited.

**U. Check a leave.** Mute the speaker, then have them leave the server and rejoin. They must not be muted.

**V. Write the result down.** See [Reading the test](#-reading-the-test).

**W. Try the other variant.** Remove the mod, install the other variant and repeat from step C.

**X. Tune.** Change `VTL_TalkSeconds` and `VTL_MuteSeconds` to taste.

**Y. Report.** Open an issue with the variant, what you heard and what you saw on screen.

**Z. Remove it.** To uninstall, remove the mod from ModLoader and delete the mod folder.

---

## ⚙️ Settings
| Setting | Default | Meaning |
|---|---|---|
| `VTL_Enabled` | `true` | Master switch |
| `VTL_TalkSeconds` | `4.0` | Talk budget T |
| `VTL_MuteSeconds` | `10.0` | Mute length M |

The budget refills at `T / (T + M)` per second. A long sentence is cut after `T * (T + M) / M` seconds, which is 5.6 seconds for the defaults and 4.1 for `T = 3`, `M = 8`. Settings are read live, so a change applies without recompiling.

### Where the settings are stored

In the server's `CustomOptions.cfg`, read through the SDK's custom server setting functions. The exact file syntax has not been checked on a live server. If a setting does not seem to apply, the default inside the Blueprint is used.

---

## 🧪 Reading the test
Write down, for each variant:

| Question | Answer |
|---|---|
| Was the speaker cut after about T seconds of talking? | yes / no |
| Did the listener stop hearing them? | yes / no |
| Did the speaker hear themselves muted? | yes / no |
| Was the speaker heard again after M seconds? | yes / no |
| Was everybody unmuted when the vote ended? | yes / no |
| Was anybody still muted after leaving and rejoining? | yes / no |
| Did the on-screen messages appear? | yes / no |

---

## 🔧 Troubleshooting
### The Blueprint does not compile

Open the compiler results panel. The usual causes are a missing `BP_VTLClientHelper` (copy the whole `Content` folder) or a different Squad SDK version with renamed pins.

### Nothing is muted

That is the most likely outcome for `server-only` if the SDK's mute functions only act on the calling client. Try `client-rpc`.

### The messages appear but the voice is not cut

The gate and the budget work, only the mute step does not. Report it with the variant name.

### Somebody stays muted

Remove the mod from ModLoader and restart the server, then report it. This should not happen.


### Package ends with Cook failed

The SDK's own assets `BP_MutableSoldier` and `SQSquidBot` log errors because the `SQAimAssist` module is missing from the SDK, and the cook counts them as failure. The mod is not the cause. Close the editor, then run the cook by hand with `-IgnoreCookErrors`:

```powershell
$s = 'C:\path\to\SquadEditor'
& "$s\UnrealEngine\Engine\Build\BatchFiles\RunUAT.bat" -noP4 BuildCookRun -Project="$s\Squad\SquadGame.uproject" -dlcname=VoteTalkLimit -cook -stage -pak -iostore -compressed -SKIPEDITORCONTENT -BasedOnReleaseVersion=20 -DLCIncludeEngineContent -manifests -VersionCookedContent -IgnoreCookErrors -AdditionalCookerOptions="-IgnoreWeaponSkinRefresh -cooksinglepackagenorefs -nullrhi -IgnoreCookErrors" -server -targetplatform=Win64
```

The result is in `Squad/Plugins/Mods/VoteTalkLimit/Saved/StagedBuilds/WindowsServer/SquadGame/Plugins/Mods/VoteTalkLimit` (server) and the same path under `Windows` (client). Copy the `.mi` file next to the `.uplugin`.

### The server skips the mod

The log says `Failed to find a valid mod ID for VoteTalkLimit (needs to be uploaded to Steam)`. Put a number in `ID=` of the `.mi` and add it to `ModLoadOrder` in `ServerConfig/ModsConfig.cfg`, or upload the mod as an unlisted Workshop item.

---

## ❓ FAQ
**Do I need SquadJS?** No. SquadJS has no voice control.

**Does it affect the scoreboard or the match?** No, only the end-of-match votes.

---

## 📕 Glossary
- **Budget**: the seconds of talk a player has left.
- **Gate**: the condition "a vote is running" that switches the limit on.
- **Helper**: `BP_VTLClientHelper`, the small actor used by the `client-rpc` variant.
- **Ruleset**: a ModLoader Blueprint class based on `SQGameRuleSet`.

# Changelog

All notable changes to **Squad-VoteTalkLimit** are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

[English](./CHANGELOG.md) · [README](./README.md) · [Tutorial](./TUTORIAL.md)

---

## [Unreleased]

### Documentation

- Both variants were loaded on a local Windows dedicated server (Squad 10.6) with ModLoader and run in the SDK editor (Play In Editor, one local player, a vote started from a script), with no Blueprint errors and no crash. The gate, the talk budget, the mute, the helper actor and the cleanup behaved as designed. Whether the voice is cut for other players, the on-screen notices and reading `CustomOptions.cfg` are still unverified.
- Added server setup notes in all five languages: a local mod needs a non-zero ID in its `.mi`, the first layer must be `ModLoader_v1`, `ModLoader.json` is now version 2, and packaging in SDK 10.6 needs `-IgnoreCookErrors`
- Tutorial steps H and J rewritten to match, with two new troubleshooting entries

## [0.1.0] - 2026-11-15

First public experiment. Neither variant has been tested on a live server.

### Added

- `server-only` variant: a ModLoader ruleset that limits talk time during the end-of-match map and faction votes and mutes through `ToggleMutePlayer` on each listener
- `client-rpc` variant: the same ruleset plus `BP_VTLClientHelper`, a small replicated actor owned by the speaker's controller that toggles the local voice on begin play and back on end play
- Per-player talk budget that refills slowly, with an info line, a warning, a mute notice and a resume notice
- Server settings `VTL_Enabled`, `VTL_TalkSeconds` and `VTL_MuteSeconds` with built-in defaults
- Talk simulations used to choose the defaults
- README and tutorial in English, Turkish, Spanish, Chinese and Russian

[0.1.0]: https://github.com/Miabeyefendi/Squad-VoteTalkLimit/releases/tag/v0.1.0

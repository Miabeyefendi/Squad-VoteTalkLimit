# Changelog

All notable changes to **Squad-VoteTalkLimit** are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

[English](./CHANGELOG.md) · [README](./README.md) · [Tutorial](./TUTORIAL.md)

---

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

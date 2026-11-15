"""How long should the talk window (T) and the wait (M) be? Two ways to gate voice at the end of a match.

G  global schedule: everyone is open for T seconds, then closed for M seconds, repeating from the start of the end screen.
P  per player: the window opens when a player starts talking; after T seconds of that player's own speech
   he is muted for M seconds, then the quota is fresh again.

Players (model, not game data), end screens of 100 s, step 0.1 s:
  normal   says one thing about every 15 s, 1 to 4 s long (mean 2.5 s), only when he is allowed to talk
  spammer  repeats a 0.8 s phrase with 0.3 s gaps for the whole time, blind to the mute

Metrics: speech of a normal player delivered (share of his speaking seconds that were audible), utterances heard
complete (at least 95%), spam audible (share of the end screen in which the spam is audible), longest uninterrupted
audible spam stretch.
"""
import numpy as np

DT = 0.1
PHASE = 100.0
N = int(PHASE / DT)
RNG = np.random.default_rng(7)


def spam_signal():
    s = np.zeros(N, dtype=bool)
    t = 0.0
    while t < PHASE:
        a, b = int(t / DT), int((t + 0.8) / DT)
        s[a:b] = True
        t += 1.1
    return s


def normal_utterances():
    out = []
    t = RNG.exponential(15.0)
    while t < PHASE:
        out.append((t, RNG.uniform(1.0, 4.0)))
        t += RNG.exponential(15.0)
    return out


def audible_global(speech, T, M):
    cyc = T + M
    t = np.arange(N) * DT
    open_ = (t % cyc) < T
    return speech & open_


def audible_player(speech, T, M):
    out = np.zeros(N, dtype=bool)
    used, muted_until, window = 0.0, -1.0, False
    for i in range(N):
        t = i * DT
        if t < muted_until:
            continue
        if speech[i]:
            used += DT
            out[i] = True
            if used >= T - 1e-9:
                muted_until = t + DT + M
                used = 0.0
        # the quota is fresh again once the mute is over (used was reset when it started)
    return out


def run(policy, T, M, reps=300):
    deliv, complete, spam_share, longest = [], [], [], []
    for _ in range(reps):
        utt = normal_utterances()
        for (start, length) in utt:
            sp = np.zeros(N, dtype=bool)
            sp[int(start / DT):int((start + length) / DT)] = True
            # a normal player talks when he wants: the others in the room do not change his own gate
            au = policy(sp, T, M)
            heard = au.sum() / max(sp.sum(), 1)
            deliv.append(heard)
            complete.append(heard >= 0.95)
        sp = spam_signal()
        au = policy(sp, T, M)
        spam_share.append(au.sum() * DT / PHASE)
        run_len, best = 0, 0
        for v in au:
            run_len = run_len + 1 if v else 0
            best = max(best, run_len)
        longest.append(best * DT)
    return np.mean(deliv), np.mean(complete), np.mean(spam_share), np.mean(longest)


print("%-4s %-4s %-4s | %-16s %-18s %-14s %-12s" % ("mode", "T", "M", "speech heard", "utterances whole", "spam audible", "longest spam"))
for name, pol in (("G", audible_global), ("P", audible_player)):
    for T in (2, 3, 4, 5):
        for M in (3, 5, 8):
            d, c, s, l = run(pol, T, M)
            print("%-4s %-4d %-4d | %5.1f%%           %5.1f%%             %5.1f%%         %4.1f s" % (name, T, M, 100 * d, 100 * c, 100 * s, l))

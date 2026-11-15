import os
HERE = os.path.dirname(os.path.abspath(__file__))
import numpy as np
exec(open(os.path.join(HERE, "talk_sim.py"), encoding="utf-8").read().split('print("%-4s')[0])


def audible_bucket(speech, T, M):
    """Token bucket: holds T seconds of speech, refills at T/(T+M) per second. Empty = muted until M seconds of refill."""
    out = np.zeros(N, dtype=bool)
    rate = T / (T + M)
    bucket, muted = float(T), False
    for i in range(N):
        if muted:
            bucket = min(T, bucket + rate * DT)
            if bucket >= rate * M - 1e-9:
                muted = False
            else:
                continue
        else:
            bucket = min(T, bucket + rate * DT)
        if speech[i]:
            bucket -= DT * 1.0
            out[i] = True
            if bucket <= 0:
                bucket, muted = 0.0, True
    return out


def polite(period_talk, pause):
    s = np.zeros(N, dtype=bool)
    t, burst = 0.0, 0.0
    while t < PHASE:
        s[int(t / DT):int((t + 0.8) / DT)] = True
        t += 1.1
        burst += 1.1
        if burst >= period_talk:
            t += pause
            burst = 0.0
    return s


cont = spam_signal()
print("token bucket: holds T s of speech, refills T/(T+M) per second, empty bucket = muted for M s")
print("%-3s %-3s | %-13s %-16s | %-14s %-22s" % ("T", "M", "speech heard", "utterances whole", "spam audible", "rule-aware spammer"))
for T, M in ((3, 5), (3, 8), (4, 5), (4, 8), (4, 10), (5, 8)):
    d, c, _, _ = run(audible_bucket, T, M)
    sc = audible_bucket(cont, T, M).sum() * DT / PHASE
    sp = audible_bucket(polite(T - 0.5, 2.2), T, M).sum() * DT / PHASE
    print("%-3d %-3d | %5.1f%%        %5.1f%%           | %5.1f%%         %5.1f%%" % (T, M, 100 * d, 100 * c, 100 * sc, 100 * sp))

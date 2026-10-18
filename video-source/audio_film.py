"""Cinematic score + sound design for the Masari 3D film (synthesized, royalty-free)."""
import json
import numpy as np
from scipy.signal import butter, lfilter, fftconvolve
from scipy.io import wavfile

SR = 48000
cfg = json.load(open("events_film.json"))
T = cfg["T"]; N = int(SR * T)
L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(21)

def t_(d): return np.arange(int(SR * d)) / SR
def lp(x, f, o=2): b, a = butter(o, min(f, SR / 2 - 100) / (SR / 2)); return lfilter(b, a, x)
def hp(x, f, o=2): b, a = butter(o, f / (SR / 2), "high"); return lfilter(b, a, x)
def bp(x, lo, hi): b, a = butter(2, [lo / (SR / 2), hi / (SR / 2)], "band"); return lfilter(b, a, x)
def hz(m): return 440 * 2 ** ((m - 69) / 12)
def env(n, a, r):
    e = np.ones(n); a = int(a * SR); r = int(r * SR)
    if a: e[:a] = np.linspace(0, 1, a)
    if r: e[-r:] *= np.linspace(1, 0, r)
    return e
def add(sig, at, g=1.0, pan=0.0):
    i = int(at * SR)
    if i < 0: sig = sig[-i:]; i = 0
    if i >= N: return
    s = sig[: N - i]
    L[i:i + len(s)] += s * g * (1 - max(pan, 0)); R[i:i + len(s)] += s * g * (1 + min(pan, 0))
def reverb(x, decay=1.8, mix=0.25):
    ir_t = t_(decay); ir = rng.standard_normal(len(ir_t)) * np.exp(-ir_t * 4.5 / decay)
    ir = lp(ir, 6000); ir /= np.sqrt(np.sum(ir ** 2))
    wet = fftconvolve(x, ir)[: len(x)]
    return x * (1 - mix) + wet * mix

DROP = 6.15; ARCH = 24.0; WORDS = 28.7; CTA = 32.1
BPM = 100; beat = 60 / BPM; bar = beat * 4
# D minor: Dm  Bb  F  C
chords = [[62, 65, 69], [58, 62, 65], [57, 60, 65], [55, 60, 64]]
roots = [38, 34, 41, 36]

pad = np.zeros(N)
def saw(f, tt, det): return 2 * ((f * (1 + det / 100) * tt) % 1) - 1
for k in range(int(T / bar) + 1):
    st = k * bar; ch = chords[k % 4]; d = bar + 1.0; tt = t_(d); s = np.zeros(len(tt))
    for m in ch + [ch[0] - 12]:
        for det in (-0.15, 0, 0.15): s += saw(hz(m), tt, det) * 0.33
    cut = 900 if st < DROP else (1800 if st < ARCH else 1200)
    s = lp(s, cut) * env(len(tt), 0.8, 1.0)
    i = int(st * SR); n = min(len(s), N - i)
    if n > 0: pad[i:i + n] += s[:n]
pad = reverb(pad, 2.5, 0.35)
add(pad, 0, 0.05, 0.2); add(np.roll(pad, 600), 0, 0.05, -0.2)

def kick():
    tt = t_(0.6); f = 42 + 110 * np.exp(-tt * 24)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 5.5)
def hat():
    tt = t_(0.07); return hp(rng.standard_normal(len(tt)), 8000) * np.exp(-tt * 60)
def snare():
    tt = t_(0.35); n = bp(rng.standard_normal(len(tt)), 1200, 6000) * np.exp(-tt * 14)
    return reverb(n + np.sin(2 * np.pi * 190 * tt) * np.exp(-tt * 30) * .5, 1.2, .4)
def bass(m, d):
    tt = t_(d); f = hz(m); s = np.tanh(2.2 * (np.sin(2 * np.pi * f * tt) + .3 * np.sin(4 * np.pi * f * tt)))
    return lp(s, 380) * env(len(tt), 0.004, 0.06)
def pluck(m):
    tt = t_(0.5); f = hz(m)
    return (np.sin(2 * np.pi * f * tt) + .35 * np.sin(2 * np.pi * 2 * f * tt) * np.exp(-tt * 12)) * np.exp(-tt * 8)

arp_bus = np.zeros(N)
for b in range(int(T / beat)):
    st = b * beat; k = int(st / bar) % 4
    if st >= T - 1.2: continue
    main = DROP <= st < ARCH
    if main or ARCH <= st < WORDS or CTA <= st:
        add(kick(), st, 0.5 if main or st >= CTA else (0.35 if b % 2 == 0 else 0))
    if main or st >= CTA:
        for e8 in range(2): add(bass(roots[k] + (12 if e8 else 0), beat / 2 * .9), st + e8 * beat / 2, 0.2 if e8 == 0 else 0.12)
        add(hat(), st + beat / 2, 0.06, 0.3)
        if b % 4 == 2: add(snare(), st, 0.14)
        arp = chords[k] + [chords[k][2] + 5]
        for s16 in range(4):
            seg = pluck(arp[(b * 4 + s16) % 4] + 12); i = int((st + s16 * beat / 4) * SR); n = min(len(seg), N - i)
            if n > 0: arp_bus[i:i + n] += seg[:n] * (0.8 if s16 % 2 == 0 else 0.55)
    if ARCH <= st < WORDS:
        arp = chords[k]
        for s8 in range(2):
            seg = pluck(arp[(b * 2 + s8) % 3] + 24); i = int((st + s8 * beat / 2) * SR); n = min(len(seg), N - i)
            if n > 0: arp_bus[i:i + n] += seg[:n] * 0.5
arp_bus = reverb(arp_bus, 1.6, 0.35)
add(arp_bus, 0, 0.04, 0.35); add(np.roll(arp_bus, 900), 0, 0.03, -0.35)

# ---------- sound design ----------
def drone(d):
    tt = t_(d); s = np.sin(2 * np.pi * hz(26) * tt) + .5 * np.sin(2 * np.pi * hz(38) * tt * 1.002)
    return lp(s, 200) * env(len(tt), 1.5, 1.0)
def shimmer():
    tt = t_(2.0); s = np.zeros(len(tt))
    for m in (86, 89, 93, 98): s += np.sin(2 * np.pi * hz(m) * tt + rng.uniform(0, 6)) * np.exp(-tt * 2)
    return reverb(s * env(len(tt), .3, .5), 2.0, .5)
def whoosh(d=0.8, lo=300, hi=6000):
    tt = t_(d); n = rng.standard_normal(len(tt) + 2048); out = np.zeros(len(tt)); seg = 512
    for i in range(0, len(tt), seg):
        c = lo + (hi - lo) * np.sin(np.pi * i / len(tt)) ** 2
        out[i:i + seg] = bp(n[i:i + seg + 1024], c * .6, min(c * 1.5, 22000))[:len(out[i:i + seg])]
    return out * np.sin(np.pi * np.linspace(0, 1, len(tt))) ** 1.5
def riser(d):
    tt = t_(d); f = 120 * (10 ** (tt / d))
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * .3 + hp(rng.standard_normal(len(tt)), 1500) * .6
    return reverb(s * (tt / d) ** 2.2, 1.0, .3)
def impact(big=True):
    tt = t_(2.2); s = np.sin(2 * np.pi * np.cumsum(34 + 70 * np.exp(-tt * 8)) / SR) * np.exp(-tt * (1.8 if big else 3))
    s += lp(rng.standard_normal(len(tt)), 3000) * np.exp(-tt * 10) * .7
    return reverb(s, 2.2, .3)
def tick(f=2600):
    tt = t_(0.05); return np.sin(2 * np.pi * f * tt) * np.exp(-tt * 110)
def pop(up=True):
    tt = t_(0.1); f = np.linspace(480, 1200, len(tt)) if up else np.linspace(1100, 600, len(tt))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 40)
def sweep(d):
    tt = t_(d); f = 300 + 900 * (tt / d) ** 1.5
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * (tt / d) * env(len(tt), .02, .08) * .6
def node():
    tt = t_(0.9); f = hz(86)
    return reverb((np.sin(2 * np.pi * f * tt) + .3 * np.sin(2 * np.pi * f * 2.99 * tt) * np.exp(-tt * 15)) * np.exp(-tt * 6), 1.5, .35)
def thump():
    tt = t_(1.2); s = np.sin(2 * np.pi * np.cumsum(48 + 90 * np.exp(-tt * 22)) / SR) * np.exp(-tt * 4)
    return reverb(s + hp(rng.standard_normal(len(tt)), 2500) * np.exp(-tt * 50) * .35, 1.4, .3)
def chime():
    tt = t_(3.5); s = np.zeros(len(tt))
    for m, g in [(74, 1), (77, .7), (81, .55), (86, .4)]:
        f = hz(m); s += g * (np.sin(2 * np.pi * f * tt) + .2 * np.sin(2 * np.pi * f * 2.76 * tt) * np.exp(-tt * 3)) * np.exp(-tt * 1.2)
    return reverb(s, 2.5, .4)

G = dict(drone=.2, shimmer=.06, whoosh=.32, riser=.22, impact=.85, impact2=.6, tick=.09, tick2=.08, pop=.15, pop2=.14,
         swish=.2, whip=.3, sweep=.06, node=.12, thump=.6, chime=.2)
for e in cfg["events"]:
    ty, at = e["type"], e["t"]; g = G[ty]
    if ty == "drone": add(drone(e.get("d", 4) + 2), at, g)
    elif ty == "shimmer": add(shimmer(), at, g)
    elif ty == "whoosh": add(whoosh(.9), at - .3, g)
    elif ty == "riser": add(riser(e.get("d", 1)), at, g)
    elif ty == "impact": add(impact(True), at, g)
    elif ty == "impact2": add(impact(False), at, g)
    elif ty == "tick": add(tick(), at, g, rng.uniform(-.3, .3))
    elif ty == "tick2": add(tick(3200), at, g, rng.uniform(-.3, .3))
    elif ty == "pop": add(pop(True), at, g, .2)
    elif ty == "pop2": add(pop(False), at, g, -.2)
    elif ty == "swish": add(whoosh(.45, 800, 9000), at - .1, g, -.3)
    elif ty == "whip": add(whoosh(.55, 600, 10000), at - .05, g)
    elif ty == "sweep": add(sweep(e.get("d", 1)), at, g)
    elif ty == "node": add(node(), at, g, rng.uniform(-.4, .4))
    elif ty == "thump": add(thump(), at, g)
    elif ty == "chime": add(chime(), at, g)

mix = np.stack([L, R], 1)
fade = np.ones(N); fi = int(.3 * SR); fo = int(2.5 * SR)
fade[:fi] = np.linspace(0, 1, fi); fade[-fo:] = np.linspace(1, 0, fo) ** 1.6
mix *= fade[:, None]
mix = np.tanh(mix * 1.4) / np.tanh(1.4)
mix /= np.max(np.abs(mix)) / 0.89
wavfile.write("audio_film.wav", SR, (mix * 32767).astype(np.int16))
print("ok")

"""Original music bed + sound effects for the Masari X video (royalty-free, synthesized)."""
import json
import numpy as np
from scipy.signal import butter, lfilter
from scipy.io import wavfile

SR = 48000
cfg = json.load(open("events.json"))
T = cfg["T"]
N = int(SR * T)
L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(7)

def t_(d): return np.arange(int(SR * d)) / SR
def lp(x, f, o=2): b, a = butter(o, f / (SR / 2)); return lfilter(b, a, x)
def hp(x, f, o=2): b, a = butter(o, f / (SR / 2), "high"); return lfilter(b, a, x)
def bp(x, lo, hi): b, a = butter(2, [lo / (SR / 2), hi / (SR / 2)], "band"); return lfilter(b, a, x)
def add(sig, at, g=1.0, pan=0.0):
    i = int(at * SR)
    if i >= N or i + len(sig) <= 0: return
    s = sig[: max(0, N - i)]
    L[i:i + len(s)] += s * g * (1 - max(pan, 0))
    R[i:i + len(s)] += s * g * (1 + min(pan, 0))
def hz(m): return 440 * 2 ** ((m - 69) / 12)
def env(n, a, r):  # attack/release linear in samples
    e = np.ones(n); a = int(a * SR); r = int(r * SR)
    if a: e[:a] = np.linspace(0, 1, a)
    if r: e[-r:] *= np.linspace(1, 0, r)
    return e

BPM = 120; beat = 60 / BPM; bar = beat * 4
CUT = [3.4, 6.8, 22.8, 28.4, 32.0]
# A minor: Am  F  C  G   (one chord per bar)
chords = [[57, 60, 64], [53, 57, 60], [48, 55, 60], [55, 59, 62]]
roots = [45, 41, 48, 43]

# ---------- pad ----------
for k in range(int(T / bar) + 1):
    st = k * bar
    ch = chords[k % 4]
    d = bar + 0.6
    tt = t_(d)
    sig = np.zeros(len(tt))
    for m in ch + [ch[0] + 12]:
        f = hz(m)
        for det in (-0.12, 0.12):
            ph = 2 * np.pi * f * (1 + det / 100) * tt
            sig += (2 * ((ph / (2 * np.pi)) % 1) - 1) * 0.5  # saw
    sig = lp(sig, 1400) * env(len(tt), 0.5, 0.8)
    g = 0.035 if st < CUT[0] else 0.028
    add(sig, st, g, pan=0.25); add(np.roll(sig, 400), st, g, pan=-0.25)

# ---------- drums / bass / pluck ----------
def kick():
    tt = t_(0.45); f = 45 + 95 * np.exp(-tt * 28)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 7)
def hat():
    tt = t_(0.06); return hp(rng.standard_normal(len(tt)), 7000) * np.exp(-tt * 70)
def clap():
    tt = t_(0.22); n = bp(rng.standard_normal(len(tt)), 900, 3500)
    e = np.exp(-tt * 18); e[:int(.012 * SR)] *= 1.6
    return n * e
def bass(m, d):
    tt = t_(d); f = hz(m)
    s = np.tanh(1.8 * np.sin(2 * np.pi * f * tt)) * np.exp(-tt * 3)
    return lp(s, 500) * env(len(tt), 0.005, 0.05)
def pluck(m):
    tt = t_(0.35); f = hz(m)
    s = (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(4 * np.pi * f * tt)) * np.exp(-tt * 11)
    return s

nb = int(T / beat)
for b in range(nb):
    st = b * beat; k = int(st / bar) % 4
    full = CUT[0] <= st < CUT[3] or st >= CUT[4]
    groove = (CUT[1] <= st < CUT[3]) or st >= CUT[4]
    if st >= T - 1.0: continue
    if full:
        add(kick(), st, 0.55)
        add(bass(roots[k], beat * 0.9), st, 0.22)
        add(bass(roots[k] + 12, beat * 0.4), st + beat / 2, 0.10)
    if groove:
        add(hat(), st + beat / 2, 0.07, pan=0.3)
        add(hat(), st + beat * 0.75, 0.035, pan=-0.3)
        if b % 2 == 1: add(clap(), st, 0.12)
        arp = chords[k] + [chords[k][1] + 12]
        for s16 in range(4):
            add(pluck(arp[(b * 4 + s16) % 4] + 12), st + s16 * beat / 4, 0.045, pan=0.4 if s16 % 2 else -0.4)
    if CUT[3] <= st < CUT[4]:  # tension section: pulsing kick only on halves
        if b % 2 == 0: add(kick(), st, 0.4)

# ---------- sound effects ----------
def whoosh(d=0.7):
    tt = t_(d); n = rng.standard_normal(len(tt)); out = np.zeros(len(tt))
    seg = 256
    for i in range(0, len(tt), seg):
        c = 400 + 5000 * np.sin(np.pi * i / len(tt)) ** 2
        out[i:i + seg] = bp(n[i:i + seg + 512], c * .7, min(c * 1.4, 20000))[:len(out[i:i + seg])]
    return lp(out, 9000) * np.sin(np.pi * np.linspace(0, 1, len(tt))) ** 1.5
def riser(d):
    tt = t_(d); f = 200 * (8 ** (tt / d))
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.3 + hp(rng.standard_normal(len(tt)), 2000) * 0.5
    return s * (tt / d) ** 2
def impact():
    tt = t_(1.6); s = np.sin(2 * np.pi * np.cumsum(40 + 60 * np.exp(-tt * 9)) / SR) * np.exp(-tt * 2.6)
    s += lp(rng.standard_normal(len(tt)), 2500) * np.exp(-tt * 14) * 0.6
    return s
def tick():
    tt = t_(0.05); return np.sin(2 * np.pi * 2300 * tt) * np.exp(-tt * 120)
def pop(up=True):
    tt = t_(0.09); f = np.linspace(500, 1150, len(tt)) if up else np.linspace(1050, 620, len(tt))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 45)
def node():
    tt = t_(0.6); f = hz(81)
    return (np.sin(2 * np.pi * f * tt) + .4 * np.sin(2 * np.pi * f * 3.01 * tt) * np.exp(-tt * 20)) * np.exp(-tt * 7)
def thump():
    tt = t_(0.6); s = np.sin(2 * np.pi * np.cumsum(55 + 80 * np.exp(-tt * 25)) / SR) * np.exp(-tt * 6)
    return s + hp(rng.standard_normal(len(tt)), 3000) * np.exp(-tt * 60) * .3
def chime():
    tt = t_(3.0); s = np.zeros(len(tt))
    for m, g in [(81, 1), (84, .7), (88, .5), (93, .3)]:
        f = hz(m); s += g * (np.sin(2 * np.pi * f * tt) + .25 * np.sin(2 * np.pi * f * 2.76 * tt) * np.exp(-tt * 4)) * np.exp(-tt * 1.4)
    return s

G = dict(whoosh=0.35, riser=0.22, impact=0.75, tick=0.10, pop=0.16, pop2=0.15, swish=0.18, node=0.16, thump=0.55, chime=0.22)
for e in cfg["events"]:
    ty, at = e["type"], e["t"]
    if ty == "whoosh": add(whoosh(), at, G[ty])
    elif ty == "riser": add(riser(e.get("d", 1.4)), at, G[ty])
    elif ty == "impact": add(impact(), at, G[ty])
    elif ty == "tick": add(tick(), at, G[ty], pan=rng.uniform(-.3, .3))
    elif ty == "pop": add(pop(True), at, G[ty], pan=.2)
    elif ty == "pop2": add(pop(False), at, G[ty], pan=-.2)
    elif ty == "swish": add(whoosh(0.35), at - .1, G[ty])
    elif ty == "node": add(node(), at, G[ty])
    elif ty == "thump": add(thump(), at, G[ty])
    elif ty == "chime": add(chime(), at, G[ty])

# ---------- master ----------
mix = np.stack([L, R], 1)
fade = np.ones(N); fi = int(.25 * SR); fo = int(2.2 * SR)
fade[:fi] = np.linspace(0, 1, fi); fade[-fo:] = np.linspace(1, 0, fo) ** 1.5
mix *= fade[:, None]
mix = np.tanh(mix * 1.6) / np.tanh(1.6)
mix /= np.max(np.abs(mix)) / 0.89
wavfile.write("audio_x.wav", SR, (mix * 32767).astype(np.int16))
print("ok", mix.shape, float(np.sqrt(np.mean(mix ** 2))))

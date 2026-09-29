import numpy as np, wave, os, json
SR = 44100
HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, 'sfx.json')))
END = D['end']
N = int(SR * (END + 0.5))
rng = np.random.default_rng(11)

def T(d): return np.arange(int(SR * d)) / SR
def hz(m): return 440 * 2 ** ((m - 69) / 12)
def fir(x, h):
    L = len(x) + len(h) - 1; F = 1 << (L - 1).bit_length()
    return np.fft.irfft(np.fft.rfft(x, F) * np.fft.rfft(h, F), F)[:L][len(h) // 2:len(h) // 2 + len(x)]
def lowpass(x, fc, k=255):
    n = np.arange(k) - k // 2; h = np.sinc(2 * fc / SR * n) * np.hamming(k); h /= h.sum(); return fir(x, h)
def highpass(x, fc): return x - lowpass(x, fc)
def bandpass(x, lo, hi): return lowpass(highpass(x, lo), hi)
def adsr(n, a, d, s, r):
    t = np.arange(n) / SR; dur = n / SR
    e = np.where(t < a, t / max(a, 1e-4), np.where(t < a + d, 1 - (1 - s) * (t - a) / max(d, 1e-4), s))
    return e * np.clip((dur - t) / max(r, 1e-4), 0, 1)
def pan(x, p): p = np.clip(p, -1, 1); return np.stack([x * np.sqrt((1 - p) / 2), x * np.sqrt((1 + p) / 2)], 1)
def add(buf, x, t0, g=1.0):
    i = int(round(t0 * SR));
    if i < 0: x = x[-i:]; i = 0
    if i >= len(buf): return
    x = x[:len(buf) - i]
    buf[i:i + len(x)] += x * g
def saw(f, t): return 2 * ((f * t) % 1) - 1
def sq(f, t, duty=.5): return np.where((f * t) % 1 < duty, 1.0, -1.0)
def tri(f, t): return 2 * np.abs(saw(f, t)) - 1
def sweep(f0, f1, d, curve='exp'):
    t = T(d)
    f = f0 * (f1 / f0) ** (t / d) if curve == 'exp' else f0 + (f1 - f0) * t / d
    return np.sin(2 * np.pi * np.cumsum(f) / SR)
def noise(d): return rng.standard_normal(len(T(d)))
def reverb(x, dec=1.6, mix=.25, pre=.012):
    n = int(SR * dec); t = np.arange(n) / SR
    ir = rng.standard_normal(n) * np.exp(-t * 6.9 / dec); ir = lowpass(ir, 5000); ir[: int(pre * SR)] = 0; ir /= np.sqrt((ir ** 2).sum())
    out = np.zeros_like(x)
    for c in range(x.shape[1]):
        ir_c = np.roll(ir, c * 37)
        y = fir(np.concatenate([x[:, c], np.zeros(n)]), np.concatenate([np.zeros(len(ir_c) - 1), ir_c]) if False else ir_c)
        L = len(x[:, c]) + n
        F = 1 << (L - 1).bit_length()
        y = np.fft.irfft(np.fft.rfft(x[:, c], F) * np.fft.rfft(ir_c, F), F)[:len(x)]
        out[:, c] = y
    return x * (1 - mix) + out * mix

# =================== INSTRUMENTS ===================
def kick(g=1., tone=48):
    t = T(.45); f = tone + 120 * np.exp(-t * 32)
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7.5) + .25 * np.exp(-t * 220) * rng.standard_normal(len(t))) * g
def snare(g=1.):
    t = T(.28); return (0.75 * highpass(rng.standard_normal(len(t)), 1800) * np.exp(-t * 17) + .45 * np.sin(2 * np.pi * 185 * t) * np.exp(-t * 26)) * g
def clap(g=1.):
    t = T(.3); n = bandpass(rng.standard_normal(len(t)), 900, 7000)
    e = sum(np.exp(-np.clip(t - d, 0, None) * 70) * (t >= d) for d in (0, .01, .021)) + .55 * np.exp(-t * 13)
    return n * e * .55 * g
def hat(g=1., op=False):
    t = T(.28 if op else .05); return highpass(rng.standard_normal(len(t)), 7500) * np.exp(-t * (11 if op else 75)) * g
def shaker(g=1.):
    t = T(.09); return bandpass(rng.standard_normal(len(t)), 5000, 11000) * np.sin(np.pi * t / .09) ** 2 * g * .5
def pad(ms, d, cut=1600, det=.1):
    t = T(d); x = np.zeros(len(t))
    for m in ms:
        for k in (-det, 0, det): x += saw(hz(m + k), t + rng.random())
    return lowpass(x / (3 * len(ms)), cut) * adsr(len(t), .35, .3, .85, .45)
def epiano(m, d=1.0, g=1.):
    t = T(d); f = hz(m)
    x = np.sin(2 * np.pi * f * t + 1.2 * np.exp(-t * 5) * np.sin(2 * np.pi * f * t)) + .25 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 4)
    return x * np.exp(-t * 2.6) * adsr(len(t), .004, .1, 1, .08) * g
def pluck(m, d=.4, g=1., bright=3500):
    t = T(d); f = hz(m); x = (saw(f, t) + .5 * sq(2 * f, t, .3)) * np.exp(-t * 8.5)
    return lowpass(x, bright) * .5 * g
def bassn(m, d, g=1.):
    t = T(d); f = hz(m); x = .55 * saw(f, t) + np.sin(2 * np.pi * f * t)
    return lowpass(x, 420) * adsr(len(t), .006, .12, .75, .05) * g
def chip(m, d, duty=.25, g=1.):
    t = T(d); return sq(hz(m), t, duty) * adsr(len(t), .003, .04, .6, .02) * .32 * g
def bell(m, d=1.4, g=1.):
    t = T(d); f = hz(m)
    return np.sin(2 * np.pi * f * t + 1.4 * np.sin(2 * np.pi * f * 3.5 * t) * np.exp(-t * 4.5)) * np.exp(-t * 3.2) * g
def glock(m, d=.9, g=1.):
    t = T(d); f = hz(m); return (np.sin(2 * np.pi * f * t) + .3 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 9)) * np.exp(-t * 5) * g
def sub_drop(d=1.2, g=1.):
    t = T(d); f = 110 * np.exp(-t * 2.2) + 32; return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.2) * g
def riser(d, g=1., f0=300, f1=5000):
    t = T(d); n = rng.standard_normal(len(t)); out = np.zeros(len(t)); seg = int(SR * .05)
    for i in range(0, len(t), seg):
        fc = f0 * (f1 / f0) ** (i / len(t)); out[i:i + seg] = bandpass(n[i:i + seg + 400], fc * .6, fc * 1.4)[:len(out[i:i + seg])]
    return out * (t / d) ** 2 * g

music = np.zeros((N, 2))
BPM = 120; B = 60 / BPM
# key: D minor -> F major lift. progression per bar
PROG = [(38, [62, 65, 69, 72]), (34, [62, 65, 70, 74]), (41, [65, 69, 72, 76]), (36, [64, 67, 72, 76])]
def bars(t0, t1):
    out = []; t = t0
    while t < t1 - 1e-3: out.append(t); t += 4 * B
    return out
def mbar(tb, bar, lvl, t_end, kick_on=True, hats=True, arp=True, bass=True, clapon=True):
    root, ch = PROG[bar % 4]
    add(music, pan(pad([c - 12 for c in ch], 4 * B + .3, 900 + 1500 * lvl, .08), 0) * .22, tb)
    for s in range(16):
        tt = tb + s * B / 4
        if tt >= t_end: break
        if bass and s % 2 == 0: add(music, pan(bassn(root + (12 if s % 8 == 6 else 0), B / 2 * .8), 0) * (.5 if s % 4 else .35), tt)
        if kick_on and s % 4 == 0: add(music, pan(kick(.95, 46), 0), tt)
        if clapon and s in (4, 12): add(music, pan(clap(.45 + .3 * lvl), 0), tt)
        if hats and s % 2 == 1: add(music, pan(hat(.18 + .1 * lvl), .3), tt)
        if hats and lvl > .6 and s % 4 == 3: add(music, pan(hat(.12, True), -.3), tt)
        if arp and s % 2 == 0:
            m = ch[[0, 2, 1, 3, 2, 1, 3, 2][(s // 2) % 8]] + 12
            add(music, pan(pluck(m, .3, .7, 1800 + 3000 * lvl), -.35 if (s // 2) % 2 else .35) * .26 * lvl, tt)
# sections (voice-driven) — original card-layout arrangement
SEC = [
    (0.0, 3.3, .45, dict(kick_on=False, clapon=False)),
    (3.3, 11.9, .0, None),                     # retro chip section (special)
    (11.9, 20.2, .0, None),
    (20.67, 28.35, .45, dict(kick_on=False, clapon=False, hats=True)),
    (28.35, 36.8, .75, {}),
    (36.8, 42.2, .9, {}),
    (44.53, 55.67, .8, {}),
    (55.67, 59.9, .45, dict(clapon=False)),
    (59.9, 69.6, 1.0, {}),
    (69.6, 79.3, .9, {}),
    (79.3, 81.9, .4, dict(kick_on=False, clapon=False)),
]
bar = 0
for (a0, b0, lvl, kw) in SEC:
    if kw is None: continue
    for tb in bars(a0, b0): mbar(tb, bar, lvl, b0, **kw); bar += 1
# 8-bit chip music for the legacy-interface passage (3.3 – 20.2)
prog_r = [(48, [60, 64, 67]), (45, [57, 60, 64]), (41, [57, 60, 65]), (43, [59, 62, 67])]
mel = [76, 79, 84, 79, 77, 76, 74, 72, 72, 76, 79, 76, 74, 72, 71, 74]
rb = 0
for tb in bars(3.3, 20.2):
    root, ch = prog_r[rb % 4]
    for s8 in range(8):
        tt = tb + s8 * B / 2
        if tt >= 20.15: break
        add(music, pan(chip(root + (12 if s8 % 2 else 0), B / 2 * .9, .5), 0) * .45, tt)
        add(music, pan(chip(ch[s8 % 3] + 12, B / 4, .125), .35) * .16, tt)
        if rb >= 1: add(music, pan(chip(mel[(rb * 8 + s8) % 16], B / 2 * .8, .25), -.25) * .3, tt)
        if s8 % 4 == 0: add(music, pan(kick(.6), 0), tt)
        add(music, pan(hat(.14), .2), tt)
    rb += 1
t = T(.5); f = hz(60) * np.exp(-t * 6)
add(music, pan(np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * np.exp(-t * 3) * .22, 0), 19.9)
# transition "hello" chord at 20.66
for i, m in enumerate([62, 69, 74, 77, 81]): add(music, pan(bell(m + 12, 3.0, .08), (i - 2) * .22), 20.66 + i * .02)
add(music, pan(pad([62, 69, 74, 77], 3.2, 2600), 0) * .32, 20.66)
# stop at 你一停
t = T(.6); f = 220 * np.exp(-t * 5); add(music, pan(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 4) * .25, 0), 42.2)
for i, m in enumerate([74, 69, 65, 62]): add(music, pan(epiano(m, 1.2, .16), (i % 2 - .5) * .6), 42.6 + i * .45)
add(music, pan(riser(1.1, .18), 0), 43.4)
for tt in [20.66, 28.35, 36.1, 44.53, 59.9, 72.3]: add(music, pan(sub_drop(1.1, .5), 0), tt)
for (a0, b0) in [(27.3, 28.35), (35.1, 36.1), (56.8, 57.7), (71.2, 72.3), (77.5, 78.55)]: add(music, pan(riser(b0 - a0, .14), 0), a0)
for i, m in enumerate([62, 65, 69, 74, 77]): add(music, pan(epiano(m + 12, 2.2, .18), (i - 2) * .2), 80.1 + i * .02)
fade = np.ones(N); i0 = int(81.1 * SR); fade[i0:] = np.clip(1 - (np.arange(N - i0) / SR) / .8, 0, 1) ** 1.3
music *= fade[:, None]

# =================== SFX ===================
sfx = np.zeros((N, 2))
def whoosh(d=.45, bright=2500):
    n = noise(d); t = T(d); out = np.zeros(len(t)); seg = int(SR * .03)
    for i in range(0, len(t), seg):
        k = i / len(t); fc = 300 + bright * np.sin(np.pi * k)
        out[i:i + seg] = bandpass(n[i:i + seg + 300], fc * .5, fc * 1.5)[:len(out[i:i + seg])]
    return out * np.sin(np.pi * t / d) ** 2 * .9
def popS(m=84):
    t = T(.12); f = hz(m) * (1 + 1.6 * np.exp(-t * 60)); return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 32) * .6
def ding(m=88, d=1.0): return bell(m, d, .38)
def click(): t = T(.02); return highpass(rng.standard_normal(len(t)), 2500) * np.exp(-t * 350) * .45
def thock(): t = T(.07); return (lowpass(rng.standard_normal(len(t)), 1800) * np.exp(-t * 90) + np.sin(2 * np.pi * 220 * t) * np.exp(-t * 60) * .5) * .6
def hitS(g=1.):
    t = T(1.0); k = np.zeros(len(t)); kk = kick(1., 42); k[:len(kk)] = kk
    sd = sub_drop(1., .4); k[:len(sd)] += sd
    return (k + lowpass(rng.standard_normal(len(t)), 5000) * np.exp(-t * 7) * .35) * .75 * g
def boing():
    t = T(.4); f = 180 + 260 * np.exp(-t * 6) * (1 + .3 * np.sin(2 * np.pi * 16 * t)); return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6) * .45
def err95():
    t = T(.3); return (sq(hz(69), t, .5) * (t < .12) + sq(hz(64), t, .5) * (t >= .12)) * np.exp(-t * 6) * .16
def win_pop():
    return np.concatenate([chip(76, .06, .5, 1.3), chip(83, .1, .5, 1.3)])
def glitchS(d=.4):
    t = T(d); x = sq(80 + 900 * (np.floor(t * 45) % 3), t) * rng.standard_normal(len(t)) * .5
    return lowpass(x, 7000) * np.exp(-t * 2.5) * .5
def crash():
    t = T(.8); return (lowpass(rng.standard_normal(len(t)), 3000) * np.exp(-t * 5) * .6 + np.sin(2 * np.pi * 70 * t) * np.exp(-t * 6) * .6 + sq(hz(40), t) * np.exp(-t * 8) * .15)
def bsodS():
    t = T(.9); g = glitchS(.9); a = (sq(hz(45), t, .5) * .12 + sin_(55, t) * .5) * np.exp(-t * 2.5); n = min(len(a), len(g)); return a[:n] + g[:n] * .3
def sin_(f, t): return np.sin(2 * np.pi * f * t)
def flap(d=.5):
    out = np.zeros(len(T(d))); k = 0
    while k * .075 < d - .05:
        n = bandpass(noise(.06), 400, 2600) * np.sin(np.pi * T(.06) / .06) ** 2
        i = int(k * .075 * SR); out[i:i + len(n)] += n[:len(out) - i] * (1 - .1 * k); k += 1
    return out * .55
def chirp(n=2, f0=2600, f1=4200):
    out = []
    for i in range(n):
        d = .07 + .03 * rng.random(); t = T(d)
        f = f0 + (f1 - f0) * np.sin(np.pi * t / d) + 300 * np.sin(2 * np.pi * 40 * t)
        out.append(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / d) ** .8); out.append(np.zeros(int(SR * .035)))
    return np.concatenate(out) * .28
def squawk(d=.42):
    t = T(d); f0 = 850 + 350 * np.sin(np.pi * t / d) - 200 * t
    ph = 2 * np.pi * np.cumsum(f0) / SR
    x = sum(np.sin(k * ph) / k ** .7 for k in range(1, 9)) + .35 * rng.standard_normal(len(t))
    x = bandpass(x, 700, 5200) * adsr(len(t), .01, .05, .85, .08)
    x *= 1 + .5 * np.sin(2 * np.pi * 34 * t)
    return x * .22
def peck():
    t = T(.035); return (highpass(rng.standard_normal(len(t)), 1800) * np.exp(-t * 260) + np.sin(2 * np.pi * 1600 * t) * np.exp(-t * 200) * .4) * .55
def landS():
    a = lowpass(noise(.1), 900) * np.exp(-T(.1) * 40) * .6; b = flap(.2) * .4
    out = np.zeros(max(len(a), len(b))); out[:len(a)] += a; out[:len(b)] += b; return out
def rise(d=.6):
    a = sweep(300, 1400, d) * np.sin(np.pi * T(d) / d) * .12; b = riser(d, .12); n = min(len(a), len(b)); return a[:n] + b[:n]
def notif(): return np.concatenate([glock(88, .18, .3)[:int(.09 * SR)], glock(95, .5, .3)])
def bubble_pop():
    t = T(.12); f = 500 + 1800 * t / .12; a = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 30) * .5; b = popS(90) * .5; n = min(len(a), len(b)); return a[:n] + b[:n]
def dock():
    t = T(.18); f = hz(76) * (1 + .5 * (1 - t / .18)); return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 18) * .3
def coin(): return np.concatenate([chip(83, .07, .5, 1.1), chip(88, .3, .5, 1.1) * np.exp(-T(.3) * 8)])
def agent(): return np.concatenate([chip(72, .05, .25), chip(79, .09, .25)]) * 1.2
def hum(d): t = T(d); return (sin_(110, t) * .5 + sin_(220, t) * .2 + sin_(330.5, t) * .1) * np.minimum(1, t / .5) * np.minimum(1, (d - t) / .3) * .12
def powerdown():
    t = T(1.1); f = 900 * np.exp(-t * 3.5) + 30; return (np.sin(2 * np.pi * np.cumsum(f) / SR) + .3 * sq(f[0] * 0 + 60, t)) * np.exp(-t * 2) * .35
def snore(d):
    out = np.zeros(len(T(d))); k = 0
    while k * .75 < d:
        tt = T(.5); n = lowpass(noise(.5), 500) * np.sin(np.pi * tt / .5) ** 2 * (.8 + .4 * sin_(28, tt)) * .3
        wh = sweep(1800, 900, .25) * np.sin(np.pi * T(.25) / .25) * .05
        i = int(k * .75 * SR); seg = np.concatenate([n, wh]); out[i:i + len(seg)] += seg[:len(out) - i]; k += 1
    return out
def slide(d): t = T(d); return (sweep(200, 900, d) * .1 + bandpass(noise(d), 1500, 5000) * .15) * np.sin(np.pi * t / d)
def rscratch():
    t = T(.45); f = 1200 * np.exp(-t * 7) * (1 + .6 * np.sin(2 * np.pi * 9 * t)); return np.sin(2 * np.pi * np.cumsum(f) / SR) * bandpass(noise(.45), 800, 4000) * .9 * np.exp(-t * 3)
def steps(d):
    out = np.zeros(len(T(d))); k = 0
    while k * .11 < d:
        s = lowpass(noise(.05), 1400) * np.exp(-T(.05) * 70) * .5; i = int(k * .11 * SR); out[i:i + len(s)] += s[:len(out) - i]; k += 1
    return out
def swoosh(): return whoosh(.3, 4000) * .7
def typing(d, rate=15):
    out = np.zeros(len(T(d))); tt = 0.
    while tt < d:
        c = thock() * .3; c[:len(click())] += click() * rng.uniform(.5, 1); i = int(tt * SR); out[i:i + len(c)] += c[:len(out) - i]; tt += 1 / rate * rng.uniform(.6, 1.4)
    return out
def tick_run(d):
    out = np.zeros(len(T(d))); k = 0
    while k * .1 < d:
        t = T(.03); s = sin_(2400, t) * np.exp(-t * 200) * .22; i = int(k * .1 * SR); out[i:i + len(s)] += s[:len(out) - i]; k += 1
    return out
def counter(d):
    out = np.zeros(len(T(d))); k = 0
    while k * .05 < d:
        t = T(.025); s = sin_(1800 + 600 * (k % 3), t) * np.exp(-t * 220) * .14; i = int(k * .05 * SR); out[i:i + len(s)] += s[:len(out) - i]; k += 1
    return out
def game_bleeps(d):
    out = np.zeros(len(T(d))); k = 0
    while k * .12 < d:
        s = chip(72 + [0, 7, 12, 5, 9, 16][k % 6], .08, .5); i = int(k * .12 * SR); out[i:i + len(s)] += s[:len(out) - i]; k += 1
    return out * .8
def creak(d): t = T(d); f = 180 + 60 * np.sin(2 * np.pi * 3 * t); return bandpass(sq(1, t) * 0 + np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * .5, 300, 2500) * np.sin(np.pi * t / d) * .16
def sparkle():
    out = np.zeros(len(T(1.0)))
    for k in range(8):
        s = glock(96 + [0, 4, 7, 12, 16, 19, 24, 28][k], .5, .16); i = int(k * .05 * SR); out[i:i + len(s)] += s[:len(out) - i]
    return out
def chime():
    out = np.zeros(len(T(2.2)))
    for k, m in enumerate([77, 81, 84, 89]): s = bell(m, 1.8, .18); i = int(k * .09 * SR); out[i:i + len(s)] += s[:len(out) - i]
    return out
def write(d): return bandpass(noise(d), 2500, 8000) * (.5 + .5 * np.abs(np.sin(2 * np.pi * 5 * T(d)))) * .12 * np.sin(np.pi * T(d) / d)
def thud(): return (lowpass(noise(.15), 600) * np.exp(-T(.15) * 30) + sin_(90, T(.15)) * np.exp(-T(.15) * 25)) * .55
def msg(): return np.concatenate([glock(84, .12, .35)[:int(.06 * SR)], glock(91, .5, .35)])
def check(n=0): return np.concatenate([glock(84 + [0, 2, 4, 7][n % 4], .08, .3)[:int(.05 * SR)], glock(91 + [0, 2, 4, 7][n % 4], .6, .35)])
def stamp():
    a = hitS(1.0) * .8; b = lowpass(noise(.2), 2000) * np.exp(-T(.2) * 25) * .5; a[:len(b)] += b; return a
def marker(): t = T(.25); return bandpass(noise(.25), 3000, 9000) * np.sin(np.pi * t / .25) * .18
def achieve():
    out = np.zeros(len(T(1.4)))
    for k, m in enumerate([72, 76, 79, 84]): s = epiano(m + 12, .8, .25); i = int(k * .08 * SR); out[i:i + len(s)] += s[:len(out) - i]
    return out
def key_thock():
    a = thock() * 1.1; b = click() * .5; a[:len(b)] += b; return a
def landsfx(): return landS()


def tickS(): t = T(.03); return (sin_(3200, t) * np.exp(-t * 180) * .18 + highpass(noise(.03), 4000) * np.exp(-t * 300) * .15)
def swipeS(): return whoosh(.25, 5000) * .5
def cardS(): return whoosh(.3, 2500) * .45 + 0
def clockS(d):
    out = np.zeros(len(T(d))); k = 0
    while k * .09 < d:
        s2 = sin_(2600 if k % 2 else 2100, T(.025)) * np.exp(-T(.025) * 200) * .2; i = int(k * .09 * SR); out[i:i + len(s2)] += s2[:len(out) - i]; k += 1
    return out
def crackS():
    t = T(.6); x = highpass(noise(.6), 1200) * np.exp(-t * 18) * .7
    x[:len(T(.25))] += sin_(90, T(.25)) * np.exp(-T(.25) * 14) * .7; return x
def alertS(): return np.concatenate([sq(hz(81), T(.09), .5) * .1, np.zeros(int(.04 * SR)), sq(hz(81), T(.09), .5) * .1])
def scrollS(): return bandpass(noise(.14), 1500, 6000) * np.sin(np.pi * T(.14) / .14) ** 2 * .35
def suckS(d):
    t = T(d); f = 300 * np.exp(-t * 1.2) + 40
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * .25 + lowpass(noise(d), 800) * .15) * np.minimum(1, t / .3) * np.minimum(1, (d - t) / .2)
def enterS():
    a = thock() * 2.2; b = lowpass(noise(.18), 3000) * np.exp(-T(.18) * 35) * .5; a2 = np.zeros(len(b)); a2[:len(a)] += a; return a2 + b
def fallS(): return sweep(1600, 300, .32) * np.sin(np.pi * T(.32) / .32) * .15
def repS(): a = thud() * .8; return a
def slashS(): return bandpass(noise(.22), 2000, 9000) * np.sin(np.pi * T(.22) / .22) ** .5 * .45
def shineS():
    out = np.zeros(len(T(1.2)))
    for k, m in enumerate([86, 90, 93, 98]): s2 = glock(m, .8, .16); i = int(k * .06 * SR); out[i:i + len(s2)] += s2[:len(out) - i]
    return out
def fillS(d):
    out = np.zeros(len(T(d))); k = 0
    while k * .023 < d:
        s2 = sin_(1400 + 30 * k, T(.02)) * np.exp(-T(.02) * 250) * .09; i = int(k * .023 * SR); out[i:i + len(s2)] += s2[:len(out) - i]; k += 1
    return out
def typeS(d): return typing(d, 18) * .8

def crtS():
    t = T(.9); return (sin_(15700, t) * .02 + lowpass(noise(.9), 900) * np.exp(-t * 8) * .3 + sin_(60, t) * np.exp(-t * 3) * .25)
def hddS(d):
    out = np.zeros(len(T(d))); k = 0
    while k * .06 < d:
        s2 = bandpass(noise(.03), 800, 3000) * np.exp(-T(.03) * 120) * (.2 + .2 * hash01(k)); i = int(k * .06 * SR); out[i:i + len(s2)] += s2[:len(out) - i]; k += 1
    return out
def hash01(k): return (np.sin(k * 12.9898) * 43758.5453) % 1
def dissolveS(d): return bandpass(noise(d), 3000, 10000) * np.sin(np.pi * T(d) / d) * .25
def fillupS(d): return sweep(300, 1200, d) * .08 * np.sin(np.pi * T(d) / d)
def bleepsS(d): return game_bleeps(d)

GEN = {
    'whoosh': lambda c: whoosh(.45), 'swoosh': lambda c: swoosh(), 'pop': lambda c: popS(84 + int(6 * rng.random())), 'ding': lambda c: ding(88 + int(rng.integers(0, 3)) * 2),
    'hit': lambda c: hitS(), 'boing': lambda c: boing(), 'err': lambda c: err95(), 'win_pop': lambda c: win_pop(), 'glitch': lambda c: glitchS(.45),
    'crash': lambda c: crash(), 'bsod': lambda c: bsodS(), 'flap': lambda c: flap(.5), 'chirp': lambda c: chirp(2 + int(rng.integers(0, 2))),
    'squawk': lambda c: squawk(), 'peck': lambda c: peck(), 'land': lambda c: landsfx(), 'rise': lambda c: rise(), 'notif': lambda c: notif(),
    'bubble_pop': lambda c: bubble_pop(), 'dock': lambda c: dock(), 'coin': lambda c: coin(), 'agent': lambda c: agent(), 'hum': lambda c: hum(c.get('d', 3)),
    'powerdown': lambda c: powerdown(), 'snore': lambda c: snore(c.get('d', 1.5)), 'slide': lambda c: slide(c.get('d', 1)), 'record_scratch': lambda c: rscratch(),
    'steps': lambda c: steps(c.get('d', .8)), 'typing': lambda c: typing(c.get('d', 1)), 'tick_run': lambda c: tick_run(c.get('d', 1)),
    'counter': lambda c: counter(c.get('d', 1)), 'game_bleeps': lambda c: game_bleeps(c.get('d', 1)), 'creak': lambda c: creak(c.get('d', .8)),
    'sparkle': lambda c: sparkle(), 'chime': lambda c: chime(), 'write': lambda c: write(c.get('d', 1)), 'thud': lambda c: thud(), 'msg': lambda c: msg(),
    'check': lambda c: check(c.get('n', 0)), 'stamp': lambda c: stamp(), 'marker': lambda c: marker(), 'achieve': lambda c: achieve(),
    'key_thock': lambda c: key_thock(), 'click': lambda c: click() * 1.5,
    'tick': lambda c: tickS(), 'swipe': lambda c: swipeS(), 'card': lambda c: cardS(), 'clock': lambda c: clockS(c.get('d', 1)),
    'crack': lambda c: crackS(), 'alert': lambda c: alertS(), 'scroll': lambda c: scrollS(), 'suck': lambda c: suckS(c.get('d', 2)),
    'enter': lambda c: enterS(), 'fall': lambda c: fallS(), 'rep': lambda c: repS(), 'slash': lambda c: slashS(), 'shine': lambda c: shineS(),
    'fill': lambda c: fillS(c.get('d', 1)), 'type': lambda c: typeS(c.get('d', .3)),
    'crt': lambda c: crtS(), 'hdd': lambda c: hddS(c.get('d', 1)), 'dissolve': lambda c: dissolveS(c.get('d', .5)), 'fill_up': lambda c: fillupS(c.get('d', .8)),
    'bleeps': lambda c: bleepsS(c.get('d', 1)),
}
missing = set()
for c in D['sfx']:
    g = GEN.get(c['type'])
    if not g: missing.add(c['type']); continue
    x = g(c)
    add(sfx, pan(x, c.get('p', 0)), c['t'], c.get('g', 1))
print('missing', missing)

music = reverb(music, 1.1, .12)
sfx = reverb(sfx, .9, .12)
def write_wav(name, x):
    x = np.clip(x, -1, 1); d = (x * 32767).astype('<i2')
    with wave.open(os.path.join(HERE, name), 'wb') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(d.tobytes())
music /= np.max(np.abs(music)) * 1.1; sfx /= np.max(np.abs(sfx)) * 1.1
write_wav('bgm.wav', music); write_wav('sfx.wav', sfx)
print('ok', N / SR)

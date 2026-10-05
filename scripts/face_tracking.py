"""Local face preparation on macOS/Windows; unavailable detectors are advisory."""
from __future__ import annotations
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def auto_face(stage, fps, frames):
    rows = []; warnings = []; detector = 'opencv-haar'
    directory = stage / 'talk/clip_000'
    images = sorted(directory.glob('f*.jpg'))
    if not images:
        raise ValueError('Missing actual narration frames for face preparation')
    if sys.platform == 'darwin' and shutil.which('swiftc'):
        try:
            with tempfile.TemporaryDirectory(prefix='adu-vision-') as work:
                executable = Path(work) / 'face'
                subprocess.run(['swiftc', '-O', str(Path(__file__).with_name('face_track.swift')), '-o', str(executable)],
                               check=True, capture_output=True)
                data = subprocess.check_output([str(executable), str(directory), '15'], text=True, encoding='utf-8')
            for line in data.splitlines():
                parts = line.split()
                if len(parts) == 5:
                    rows.append((int(parts[0][2:7]), float(parts[1]), float(parts[2]), float(parts[4])))
            if rows: detector = 'vision'
        except (OSError, subprocess.CalledProcessError, ValueError):
            warnings.append('Vision unavailable; using the cross-platform local detector')
    if not rows:
        try:
            import cv2
            detector_file = Path(cv2.data.haarcascades) / 'haarcascade_frontalface_default.xml'
            cascade = cv2.CascadeClassifier(str(detector_file))
            if cascade.empty(): raise ValueError('OpenCV face detector unavailable')
            for image in images[::15]:
                # imdecode supports Unicode and spaces in Windows file paths.
                import numpy as np
                pixels = cv2.imdecode(np.frombuffer(image.read_bytes(), dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
                if pixels is None: continue
                h, w = pixels.shape
                faces = cascade.detectMultiScale(pixels, scaleFactor=1.1, minNeighbors=5,
                                                minSize=(max(24, w // 20), max(24, h // 30)))
                if len(faces):
                    x, y, fw, fh = max(faces, key=lambda f: f[2] * f[3])
                    rows.append((int(image.stem[2:]), (x + fw / 2) / w, (y + fh / 2) / h, fh / h))
        except (ImportError, OSError, ValueError, AttributeError):
            warnings.append('Local detector unavailable; retain a wide fixed framing and review the presenter')
    if not rows:
        rows = [(1, .5, .5, 1.0), (frames, .5, .5, 1.0)]
        detector = 'wide-fixed-fallback'
        warnings.append('No reliable face found; this is wide framing, not verified tracking')
    else:
        gaps = [rows[0][0] - 1, frames - rows[-1][0]] + [b[0] - a[0] for a, b in zip(rows, rows[1:])]
        if max(gaps) > fps:
            warnings.append('Face detection gaps exceed one second; inspect black intervals, turns and crop joins')
        if rows[0][0] > 1: rows.insert(0, (1, *rows[0][1:]))
        if rows[-1][0] < frames: rows.append((frames, *rows[-1][1:]))
    face = {'f': [r[0] for r in rows]}
    for key, index in [('cx', 1), ('cy', 2), ('h', 3)]:
        values = [r[index] for r in rows]
        face[key] = [round(sum(values[max(0, i - 2):i + 3]) / len(values[max(0, i - 2):i + 3]), 4) for i in range(len(values))]
    (stage / 'face.js').write_text('const FACE=' + json.dumps({'clip_000': face}) + ';\n', encoding='utf-8')
    return dict(mode=detector, samples=len(rows), warnings=warnings, reviewRequired=True,
                review='Review actual eyes, mouth and chin throughout; detection does not certify identity or crop quality')

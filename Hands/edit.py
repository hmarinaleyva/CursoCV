#!/usr/bin/env python3

from HandTrackerRenderer import HandTrackerRenderer
from HandTracker2 import HandTracker

tracker = HandTracker()
renderer = HandTrackerRenderer(tracker=tracker)

while True:
    frame, hands = tracker.next_frame()
    if frame is None: break
    frame = renderer.draw(frame, hands)


    # Salir del programa si alguna de estas teclas son presionadas {ESC, SPACE, q} 
    if renderer.waitKey(delay=1) in [27, 32, ord('q')]:
        break
renderer.exit()
tracker.exit()

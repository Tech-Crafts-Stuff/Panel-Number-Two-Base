# We need a few libraries for this script to work
import neopixel
from machine import Pin
import time, random

# A python class to configure the panel lights. You can change this as you see fit.
class PanelLights:

    # Set some constants containing RGB values for the addressable LEDS
    RED = (64,0,0)
    OFF = (0,0,0)
    BLUE = (0,0,64)
    GREEN = (0,64,0)
    BRIGHTWHITE = (190,75,15)
    WHITE = (143, 55, 11)

    # A couple of lists that mark the position of LEDs that have a red button
    # or mark the position of the small round lights on the panel
    REDLEDPOSITION = [1,2]
    SMALLROUNDLIGHTPOSITION = [0, 7]
    SMALLSEQUENCE = [1, 2, 3, 4]   # <— these will light 1→2→3→4, stay lit, then all off

    def __init__(self, numberOfPixels):
        self.numberOfPixels = numberOfPixels
        self.np = neopixel.NeoPixel(Pin(11), numberOfPixels)
        self.onOrOff = [1] * numberOfPixels
        self.currentColour = self.GREEN

        # --- state for the 1-2-3-4 sequence ---
        self.seq_positions = list(self.SMALLSEQUENCE)
        self.seq_next_index = 0      # Which LED in the sequence to light next
        self.seq_hold_final = False  # Are we holding all lit before turning off?

    def _apply_sequence_pixel(self, j):
        """
        Decide and set the color for sequence LEDs, returning True if this pixel
        was handled (so caller shouldn't touch it).
        """
        if j not in self.seq_positions:
            return False

        pos_index = self.seq_positions.index(j)

        # Already lit in the sequence? keep it on.
        if pos_index < self.seq_next_index:
            self.np[j] = self.WHITE
            return True

        # This is the next one to light now.
        if pos_index == self.seq_next_index:
            self.np[j] = self.WHITE
            return True

        # Not reached yet in the sequence — keep it off for now.
        self.np[j] = self.OFF
        return True

    def _advance_sequence_if_needed(self):
        """Progress sequence or reset after holding the last LED."""
        if self.seq_hold_final:
            # We just held all 4 lit for one extra loop — now turn off and reset
            for p in self.seq_positions:
                self.np[p] = self.OFF
            self.np.write()
            self.seq_next_index = 0
            self.seq_hold_final = False
            return

        self.seq_next_index += 1

        if self.seq_next_index >= len(self.seq_positions):
            # All 4 are now lit — next time we'll clear them
            self.seq_hold_final = True
            self.seq_next_index = 0

    def activatePanel(self):
        # Randomize non-sequence LEDs' on/off state
        for i in range(len(self.onOrOff)):
            self.onOrOff[i] = random.choice([0,1])

        # Set colours for each LED
        for j in range(self.numberOfPixels):
            # Handle the special 1-2-3-4 sequence first
            if self._apply_sequence_pixel(j):
                continue

            # Everything below is your existing logic for the other LEDs
            if self.onOrOff[j] == 0:
                self.np[j] = self.OFF
            else:
                if j in [3,4]:
                    self.np[j] = self.WHITE  # (bugfix) actually set it to white
                elif j in self.REDLEDPOSITION:
                    self.np[j] = self.RED
                elif j in self.SMALLROUNDLIGHTPOSITION:
                    newColour = random.choice([self.BLUE, self.GREEN])
                    while newColour == self.currentColour:
                        newColour = random.choice([self.BLUE, self.GREEN])
                    self.currentColour = newColour
                    self.np[j] = newColour
                else:
                    self.np[j] = self.WHITE

        # Draw this frame
        self.np.write()

        # Advance the sequence (and handle the "all off" step if we just completed)
        self._advance_sequence_if_needed()

        # Sleep between 2–5 seconds (unchanged)
        time.sleep(random.choice([1,2,3,4]))

panel = PanelLights(11)
while True:
    panel.activatePanel()

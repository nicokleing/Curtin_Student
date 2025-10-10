import unittest

from simulation.autoplace import auto_place


class AutoPlaceTest(unittest.TestCase):
    def test_simple_layout_has_no_overlap(self):
        rides = [
            {"type": "pirate", "capacity": 12, "duration": 30},
            {"type": "ferris", "capacity": 10, "duration": 28},
            {"type": "roller", "capacity": 18, "duration": 45},
        ]

        placed, warnings = auto_place(rides, width=120, height=80, min_gap=3)

        self.assertEqual(len(placed), 3)
        self.assertFalse(warnings)

        boxes = []
        for ride in placed:
            x, y, w, h = ride["bbox"]
            self.assertGreaterEqual(x, 0)
            self.assertGreaterEqual(y, 0)
            self.assertLessEqual(x + w, 120)
            self.assertLessEqual(y + h, 80)
            boxes.append((x, y, x + w, y + h))

        for i in range(len(boxes)):
            for j in range(i + 1, len(boxes)):
                ax1, ay1, ax2, ay2 = boxes[i]
                bx1, by1, bx2, by2 = boxes[j]
                overlap = not (ax2 <= bx1 or bx2 <= ax1 or ay2 <= by1 or by2 <= ay1)
                self.assertFalse(overlap, msg=f"rides {i} and {j} overlap")


if __name__ == "__main__":
    unittest.main()

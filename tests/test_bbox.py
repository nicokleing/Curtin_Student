import unittest
from types import SimpleNamespace

from adventure.config.loader import ConfigLoader


class BBoxTests(unittest.TestCase):
    def test_rides_do_not_overlap_in_preset(self):
        loader = ConfigLoader()
        args = SimpleNamespace(
            preset='small',
            mode='simple',
            seed=None,
            steps=10,
            stats=False,
            no_gui=True,
            save_kpis=None,
            kpi_buffer_size=16,
            kpi_warmup=1,
            kpi_interval=0.0,
            kpi_style='default',
            save_run=False,
            log_path=None,
            params_csv=None,
            patrons_override=None,
            map_csv=None,
            rides_csv=None,
            patrons_csv=None,
            config=None,
            wizard=False,
            list_presets=False,
            gui=False,
            no_summary=True,
        )

        config = loader.load_from_args(args)
        rides = config.rides
        boxes = []
        for r in rides:
            x, y, w, h = r.bbox
            boxes.append((x, y, x + w, y + h))

        # check pairwise non-overlap
        for i in range(len(boxes)):
            for j in range(i + 1, len(boxes)):
                ax1, ay1, ax2, ay2 = boxes[i]
                bx1, by1, bx2, by2 = boxes[j]
                overlap = not (ax2 <= bx1 or bx2 <= ax1 or ay2 <= by1 or by2 <= ay1)
                self.assertFalse(overlap, msg=f"Ride {i} overlaps ride {j}")


if __name__ == '__main__':
    unittest.main()

import unittest

import matplotlib.pyplot as plt

from adventure.ui.renderers.stats_renderer import StatsRenderer


class StatsRendererTests(unittest.TestCase):
    def _make_state(self, step, riders=0, queued=0, departed=0, abandoned=0, satisfaction=80, satisfaction_ema=78):
        return {
            'step': step,
            'statistics': {
                'riders_now': riders,
                'queued_now': queued,
                'departed_total': departed,
                'abandoned_now': abandoned,
                'satisfaction_now': satisfaction,
                'satisfaction_ema': satisfaction_ema,
            }
        }

    def test_history_does_not_exceed_max(self):
        fig, axes = plt.subplots(3, 1)
        renderer = StatsRenderer(list(axes))
        max_len = renderer.max_history

        for step in range(max_len + 50):
            state = self._make_state(step, riders=step % 5, queued=step % 7,
                                     departed=step // 3, abandoned=step // 10)
            renderer.render(state, engine=None)

        self.assertLessEqual(len(renderer.history['steps']), max_len)
        self.assertLessEqual(len(renderer.history['queued']), max_len)
        self.assertLessEqual(len(renderer.history['satisfaction_now']), max_len)
        self.assertLessEqual(len(renderer.history['satisfaction_ema']), max_len)
        plt.close(fig)

    def test_text_placeholder_when_history_short(self):
        fig, axes = plt.subplots(3, 1)
        renderer = StatsRenderer(list(axes))
        state = self._make_state(0, riders=1, queued=2)
        renderer.render(state, engine=None)
        # First axis should have text, no lines yet
        self.assertEqual(len(axes[0].lines), 0)
        self.assertTrue(any("Collecting" in txt.get_text() for txt in axes[0].texts))
        plt.close(fig)


if __name__ == '__main__':
    unittest.main()

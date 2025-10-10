"""Render real-time statistics with dynamic charts."""

import time
from collections import deque

import matplotlib.pyplot as plt


STYLE_PRESETS = {
    'default': 'default',
    'dark': 'dark_background',
    'minimal': 'classic',
    'colorblind': 'default'
}


class StatsRenderer:
    """Render real-time statistics using configurable line charts."""

    def __init__(self, axes, max_history=240, warmup=5, style='default', refresh_interval=0.0):
        if isinstance(axes, (list, tuple)):
            self.axes = list(axes)
        elif axes is None:
            self.axes = []
        else:
            self.axes = [axes]

        self.max_history = max(1, int(max_history))
        self.warmup = max(0, int(warmup))
        self.refresh_interval = max(0.0, float(refresh_interval))
        self.style = style or 'default'
        self.history = {
            'steps': deque(maxlen=self.max_history),
            'riders': deque(maxlen=self.max_history),
            'queued': deque(maxlen=self.max_history),
            'departed': deque(maxlen=self.max_history),
            'abandoned': deque(maxlen=self.max_history),
            'satisfaction_now': deque(maxlen=self.max_history),
            'satisfaction_ema': deque(maxlen=self.max_history)
        }
        self._last_draw = 0.0
        self._has_drawn = False
        self._style_applied = False
        self._palette = self._build_palette()
        self._satisfaction_axis = None
        self._apply_style()

    def render(self, state, engine):
        """Render the current statistics with optional throttling."""
        if not self.axes:
            return

        stats = state['statistics']
        current_step = state['step']
        self._update_history(current_step, stats)

        threshold = max(2, self.warmup)
        if len(self.history['steps']) < threshold:
            self._clear_axes()
            self._render_text_stats(stats, current_step, threshold)
            self._last_draw = time.monotonic()
            return

        now = time.monotonic()
        if self.refresh_interval > 0 and self._has_drawn and (now - self._last_draw) < self.refresh_interval:
            return

        self._clear_axes()
        self._render_queue_plot(self.axes[0])
        if len(self.axes) > 1:
            self._render_riders_plot(self.axes[1])
        if len(self.axes) > 2:
            self._render_abandon_plot(self.axes[2])

        self._has_drawn = True
        self._last_draw = now

    def _build_palette(self):
        if self.style == 'colorblind':
            return {
                'queue': '#CC79A7',
                'riders': '#009E73',
                'active': '#0072B2',
                'departed': '#E69F00',
                'abandoned': '#D55E00',
                'sat_good': '#009E73',
                'sat_warm': '#F0E442',
                'sat_cold': '#D55E00',
                'sat_line': '#56B4E9',
                'sat_fill': '#BFD3E6'
            }
        return {
            'queue': 'orange',
            'riders': 'steelblue',
            'active': 'navy',
            'departed': 'green',
            'abandoned': 'purple',
            'sat_good': '#228B22',
            'sat_warm': '#C99700',
            'sat_cold': '#B22222',
            'sat_line': '#1F77B4',
            'sat_fill': '#B0CFF2'
        }

    def _satisfaction_color(self, value):
        if value >= 80:
            return self._palette['sat_good']
        if value >= 60:
            return self._palette['sat_warm']
        return self._palette['sat_cold']

    def _apply_style(self):
        if self._style_applied or self.style == 'default':
            return
        try:
            plt.style.use(STYLE_PRESETS.get(self.style, self.style))
            self._style_applied = True
        except Exception:
            self._style_applied = False

    def _update_history(self, step, stats):
        self.history['steps'].append(step)
        self.history['riders'].append(stats['riders_now'])
        self.history['queued'].append(stats['queued_now'])
        self.history['departed'].append(stats['departed_total'])
        self.history['abandoned'].append(stats['abandoned_now'])
        sat_now = stats.get('satisfaction_now', 100.0)
        sat_ema = stats.get('satisfaction_ema', sat_now)
        self.history['satisfaction_now'].append(sat_now)
        self.history['satisfaction_ema'].append(sat_ema)

    def _clear_axes(self):
        for ax in self.axes:
            ax.clear()
        if self._satisfaction_axis is not None:
            try:
                self._satisfaction_axis.remove()
            except Exception:
                pass
            self._satisfaction_axis = None

    def _render_queue_plot(self, ax):
        steps = list(self.history['steps'])
        queued = list(self.history['queued'])
        riders = list(self.history['riders'])
        ax.plot(steps, queued, color=self._palette['queue'], linewidth=1.6, label='In Queue')
        ax.plot(steps, riders, color=self._palette['riders'], linewidth=1.0, alpha=0.75, label='On Rides')
        ax.set_title('Queues and Riders')
        ax.set_ylabel('Visitors')
        ax.grid(True, alpha=0.25)
        ax.legend(loc='upper left', fontsize=8)
        ax.text(0.02, 0.85,
                f"Queues: {queued[-1]}\nRiders: {riders[-1]}",
                transform=ax.transAxes, fontsize=9,
                bbox=dict(boxstyle="round,pad=0.25", facecolor='white', alpha=0.75))

    def _render_riders_plot(self, ax):
        steps = list(self.history['steps'])
        riders = list(self.history['riders'])
        queued = list(self.history['queued'])
        departed = list(self.history['departed'])
        active_total = [r + q for r, q in zip(riders, queued)]
        ax.plot(steps, active_total, color=self._palette['active'], linewidth=1.6, label='Active Total')
        ax.plot(steps, departed, color=self._palette['departed'], linewidth=1.2, label='Departed')
        ax.set_title('Park Flow')
        ax.set_ylabel('Visitors')
        ax.grid(True, alpha=0.25)
        ax.legend(loc='upper left', fontsize=8)

        sat_now = self.history['satisfaction_now'][-1] if self.history['satisfaction_now'] else 100.0
        sat_ema = self.history['satisfaction_ema'][-1] if self.history['satisfaction_ema'] else sat_now
        sat_color = self._satisfaction_color(sat_ema)
        ax.text(0.02, 0.82,
                f"Active: {active_total[-1]}\nDeparted: {departed[-1]}\nSat: {sat_now:.0f}",
                transform=ax.transAxes, fontsize=9,
                bbox=dict(boxstyle="round,pad=0.25", facecolor='white', alpha=0.75),
                color=sat_color)

        sat_axis = ax.twinx()
        self._satisfaction_axis = sat_axis
        sat_axis.set_ylim(0, 100)
        sat_axis.set_ylabel('Satisfaction (EMA)', color=sat_color)
        ema_values = list(self.history['satisfaction_ema'])
        sat_axis.plot(steps, ema_values, color=self._palette['sat_line'], linewidth=1.8, label='Satisfaction (EMA)')
        sat_axis.fill_between(steps, ema_values, 100, color=self._palette['sat_fill'], alpha=0.08)
        sat_axis.tick_params(axis='y', colors=sat_color, labelsize=8)
        sat_axis.spines['right'].set_color(sat_color)
        sat_axis.axhspan(80, 100, color=self._palette['sat_good'], alpha=0.05)
        sat_axis.axhspan(60, 80, color=self._palette['sat_warm'], alpha=0.04)
        sat_axis.axhspan(0, 60, color=self._palette['sat_cold'], alpha=0.02)

    def _render_abandon_plot(self, ax):
        steps = list(self.history['steps'])
        abandoned = list(self.history['abandoned'])
        ax.plot(steps, abandoned, color=self._palette['abandoned'], linewidth=1.6,
                label='Queue Abandons')
        ax.set_title('Abandonments')
        ax.set_ylabel('Cumulative')
        ax.set_xlabel('Simulation Step')
        ax.grid(True, alpha=0.25)
        if max(abandoned) > 0:
            ax.legend(loc='upper left', fontsize=8)
        ax.text(0.02, 0.85,
                f"Total: {abandoned[-1]}",
                transform=ax.transAxes, fontsize=9,
                bbox=dict(boxstyle="round,pad=0.25", facecolor='white', alpha=0.75))

    def _render_text_stats(self, stats, step, threshold):
        primary = self.axes[0]
        primary.set_xlim(0, 1)
        primary.set_ylim(0, 1)
        primary.axis('off')
        needed = max(0, threshold - len(self.history['steps']))
        sat_now = stats.get('satisfaction_now', 100.0)
        sat_ema = stats.get('satisfaction_ema', sat_now)
        lines = [
            f"Riding: {stats['riders_now']}",
            f"Queued: {stats['queued_now']}",
            f"Departed: {stats['departed_total']}",
            f"Abandoned: {stats['abandoned_now']}",
            f"Satisfaction: {sat_now:.1f}",
            f"Smooth: {sat_ema:.1f}",
            f"Step: {step}",
            "",
            f"Collecting samples ({needed} more)..." if needed else "Collecting samples..."
        ]
        for idx, text in enumerate(lines):
            primary.text(0.1, 0.9 - idx * 0.12, text, fontsize=11,
                         transform=primary.transAxes, va='top')

        for extra_ax in self.axes[1:]:
            extra_ax.axis('off')

    def get_export_data(self):
        """Return statistics for export."""
        return {
            'steps': list(self.history['steps']),
            'riders_timeline': list(self.history['riders']),
            'queued_timeline': list(self.history['queued']),
            'departed_timeline': list(self.history['departed']),
            'abandoned_timeline': list(self.history['abandoned']),
            'satisfaction_now': list(self.history['satisfaction_now']),
            'satisfaction_ema': list(self.history['satisfaction_ema'])
        }

#!/usr/bin/env python3
"""
AutoDiag Pro - Live Data Tab
Table + real-time line chart for up to 4 selected PIDs.
"""

import logging
from collections import deque
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QSplitter,
)
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QFont, QColor

try:
    from PyQt6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis
    CHARTS_AVAILABLE = True
except ImportError:
    CHARTS_AVAILABLE = False

logger = logging.getLogger(__name__)

# How many data points to keep on screen
_CHART_WINDOW = 60

# Colours for up to 4 series
_SERIES_COLOURS = ["#00BFFF", "#FF6B35", "#7FFF00", "#FF1493"]


class LiveDataTab:
    def __init__(self, parent_window):
        self.parent = parent_window
        self.live_data_table = None

        # Chart state
        self._chart      = None
        self._chart_view = None
        self._y_axis     = None
        self._x_axis     = None
        self._series: dict[str, QLineSeries] = {}         # param → series
        self._buffers: dict[str, deque]      = {}         # param → deque of floats
        self._plotted: list[str]             = []         # up to 4 param names being plotted
        self._t = 0                                        # sample counter

    # ------------------------------------------------------------------
    # Tab construction
    # ------------------------------------------------------------------

    def create_tab(self):
        """Build and return the Live Data tab widget."""
        tab = QWidget()
        root_layout = QVBoxLayout(tab)
        root_layout.setSpacing(6)

        # Header
        header = QLabel("📊 Live Data Streaming")
        header.setProperty("class", "tab-title")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Control bar
        control_frame = QFrame()
        control_frame.setProperty("class", "glass-card")
        control_layout = QHBoxLayout(control_frame)
        control_layout.setContentsMargins(8, 4, 8, 4)

        start_btn = QPushButton("▶ Start Stream")
        start_btn.setProperty("class", "success")
        start_btn.clicked.connect(self.parent.start_live_stream)

        stop_btn = QPushButton("⏹ Stop Stream")
        stop_btn.setProperty("class", "danger")
        stop_btn.clicked.connect(self.parent.stop_live_stream)

        plot_hint = QLabel("Click a row to toggle plot (max 4)")
        plot_hint.setStyleSheet("color: #888; font-size: 11px;")

        control_layout.addWidget(start_btn)
        control_layout.addWidget(stop_btn)
        control_layout.addStretch()
        control_layout.addWidget(plot_hint)

        # Main split: table left, chart right
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # --- Table panel ---
        table_panel = QFrame()
        table_panel.setProperty("class", "glass-card")
        table_layout = QVBoxLayout(table_panel)
        table_layout.setContentsMargins(6, 6, 6, 6)

        data_title = QLabel("Live Parameters")
        data_title.setProperty("class", "section-title")

        self.live_data_table = QTableWidget(0, 4)
        self.live_data_table.setHorizontalHeaderLabels(["Parameter", "Value", "Unit", "Plot"])
        self.live_data_table.horizontalHeader().setStretchLastSection(False)
        self.live_data_table.setColumnWidth(0, 220)
        self.live_data_table.setColumnWidth(1, 90)
        self.live_data_table.setColumnWidth(2, 70)
        self.live_data_table.setColumnWidth(3, 50)
        self.live_data_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.live_data_table.cellClicked.connect(self._on_table_cell_clicked)

        self._init_table_headers()

        table_layout.addWidget(data_title)
        table_layout.addWidget(self.live_data_table)
        splitter.addWidget(table_panel)

        # --- Chart panel ---
        if CHARTS_AVAILABLE:
            self._build_chart()
            splitter.addWidget(self._chart_view)
        else:
            no_chart = QLabel("PyQt6-Charts not installed\nInstall: pip install PyQt6-Charts")
            no_chart.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_chart.setStyleSheet("color: #888;")
            splitter.addWidget(no_chart)

        splitter.setSizes([420, 580])

        root_layout.addWidget(header)
        root_layout.addWidget(control_frame)
        root_layout.addWidget(splitter, 1)

        return tab, "📊 Live Data"

    def _build_chart(self):
        """Create the QChart and QChartView."""
        self._chart = QChart()
        self._chart.setTitle("Live PID Graph")
        self._chart.setBackgroundBrush(QColor("#1a1a2e"))
        self._chart.setTitleBrush(QColor("#e0e0e0"))
        self._chart.legend().setVisible(True)
        self._chart.legend().setLabelColor(QColor("#cccccc"))

        self._x_axis = QValueAxis()
        self._x_axis.setRange(0, _CHART_WINDOW)
        self._x_axis.setLabelFormat("%d")
        self._x_axis.setTitleText("Samples")
        self._x_axis.setLabelsColor(QColor("#aaaaaa"))
        self._x_axis.setTitleBrush(QColor("#aaaaaa"))
        self._x_axis.setGridLineColor(QColor("#333355"))

        self._y_axis = QValueAxis()
        self._y_axis.setRange(0, 100)
        self._y_axis.setLabelFormat("%.1f")
        self._y_axis.setTitleText("Value")
        self._y_axis.setLabelsColor(QColor("#aaaaaa"))
        self._y_axis.setTitleBrush(QColor("#aaaaaa"))
        self._y_axis.setGridLineColor(QColor("#333355"))

        self._chart.addAxis(self._x_axis, Qt.AlignmentFlag.AlignBottom)
        self._chart.addAxis(self._y_axis, Qt.AlignmentFlag.AlignLeft)

        self._chart_view = QChartView(self._chart)
        self._chart_view.setRenderHint(self._chart_view.renderHints())

    # ------------------------------------------------------------------
    # Table interaction
    # ------------------------------------------------------------------

    def _on_table_cell_clicked(self, row: int, col: int):
        """Toggle a parameter into/out of the plot set when a row is clicked."""
        if not CHARTS_AVAILABLE:
            return
        item = self.live_data_table.item(row, 0)
        if item is None:
            return
        param = item.text()

        if param in self._plotted:
            self._remove_series(param)
        elif len(self._plotted) < 4:
            self._add_series(param)

        self._update_plot_column()

    def _update_plot_column(self):
        """Sync the 'Plot' column markers in the table."""
        for row in range(self.live_data_table.rowCount()):
            item = self.live_data_table.item(row, 0)
            if item is None:
                continue
            param = item.text()
            marker_item = QTableWidgetItem("●" if param in self._plotted else "")
            colour = self._get_series_colour(param)
            if colour:
                marker_item.setForeground(QColor(colour))
            marker_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.live_data_table.setItem(row, 3, marker_item)

    def _get_series_colour(self, param: str) -> str:
        """Return the hex colour for a plotted param, or empty string."""
        try:
            idx = self._plotted.index(param)
            return _SERIES_COLOURS[idx]
        except ValueError:
            return ""

    # ------------------------------------------------------------------
    # Series management
    # ------------------------------------------------------------------

    def _add_series(self, param: str):
        """Add a new line series for param."""
        if param in self._series:
            return
        colour_idx = len(self._plotted)
        series = QLineSeries()
        series.setName(param)
        pen = series.pen()
        pen.setColor(QColor(_SERIES_COLOURS[colour_idx]))
        pen.setWidth(2)
        series.setPen(pen)

        self._chart.addSeries(series)
        series.attachAxis(self._x_axis)
        series.attachAxis(self._y_axis)

        self._series[param] = series
        self._buffers[param] = deque(maxlen=_CHART_WINDOW)
        self._plotted.append(param)

    def _remove_series(self, param: str):
        """Remove a line series for param."""
        series = self._series.pop(param, None)
        if series:
            self._chart.removeSeries(series)
        self._buffers.pop(param, None)
        if param in self._plotted:
            self._plotted.remove(param)

    # ------------------------------------------------------------------
    # Data updates
    # ------------------------------------------------------------------

    def _init_table_headers(self):
        """Empty table on init — rows added by update_live_data."""
        self.live_data_table.setRowCount(0)

    def update_live_data(self, live_data: list):
        """Refresh table and chart with new live data tuples (param, value, unit)."""
        self.live_data_table.setRowCount(len(live_data))

        for row, (param, value, unit) in enumerate(live_data):
            self.live_data_table.setItem(row, 0, QTableWidgetItem(param))
            self.live_data_table.setItem(row, 1, QTableWidgetItem(str(value)))
            self.live_data_table.setItem(row, 2, QTableWidgetItem(str(unit)))

        self._update_plot_column()

        if not CHARTS_AVAILABLE:
            return

        # Add new data points to plotted series
        self._t += 1
        x = float(self._t)

        value_map = {p: v for p, v, u in live_data}
        y_min, y_max = float("inf"), float("-inf")

        for param in list(self._plotted):
            raw = value_map.get(param)
            if raw is None:
                continue
            try:
                y = float(raw)
            except (ValueError, TypeError):
                continue

            buf = self._buffers[param]
            buf.append(y)

            series = self._series[param]
            series.append(QPointF(x, y))

            # Trim to window size
            if series.count() > _CHART_WINDOW:
                series.removePoints(0, series.count() - _CHART_WINDOW)

            if buf:
                y_min = min(y_min, min(buf))
                y_max = max(y_max, max(buf))

        # Update axes
        if self._plotted:
            self._x_axis.setRange(max(0.0, x - _CHART_WINDOW), x)

            if y_min != float("inf") and y_max != float("-inf"):
                margin = max(1.0, (y_max - y_min) * 0.1)
                self._y_axis.setRange(y_min - margin, y_max + margin)

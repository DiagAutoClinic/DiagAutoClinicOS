import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTreeWidget, QTreeWidgetItem, QLabel, 
                             QPushButton, QTabWidget, QSplitter, QTableWidget, 
                             QTableWidgetItem, QTextEdit, QFrame, QGraphicsView, 
                             QGraphicsScene, QGraphicsRectItem, QGraphicsLineItem, 
                             QGraphicsTextItem, QGridLayout, QScrollArea, QSizePolicy)
from PyQt6.QtCore import Qt, QTimer, QTime
from PyQt6.QtGui import QColor, QPen, QBrush, QFont, QPalette

class KineticSchematicWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Theme: Blueprint
        self.setStyleSheet("""
            QWidget {
                background-color: #0b1021; 
                color: #00ffff; 
                font-family: 'Consolas', 'Courier New', monospace;
            }
            QTreeWidget {
                border: 1px solid #004444;
                background-color: #0f152b;
            }
            QTreeWidget::item:selected {
                background-color: #004444;
            }
            QFrame {
                border: 1px solid #004444;
            }
            QLabel {
                color: #00ffff;
            }
            QPushButton {
                border: 1px solid #00ffff;
                background-color: #0f152b;
                padding: 5px;
                color: #00ffff;
            }
            QPushButton:hover {
                background-color: #004444;
            }
            QTextEdit {
                background-color: #0f152b;
                border: 1px solid #004444;
                color: #00ff00;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(5, 5, 5, 5)

        # Top Header
        header = QLabel("[VIN: JT11GD...] [SYS: 1GD-FTV ENGINE] | LAYERS: [MECH] [ELEC] [LOGIC]")
        header.setStyleSheet("background-color: #002222; padding: 5px; font-weight: bold;")
        layout.addWidget(header)

        # Main Splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        # Left: System Navigator
        nav_tree = QTreeWidget()
        nav_tree.setHeaderLabel("SYSTEM NAVIGATOR")
        root = QTreeWidgetItem(nav_tree, ["> Powertrain"])
        fuel = QTreeWidgetItem(root, ["v Fuel System"])
        QTreeWidgetItem(fuel, ["  [ ] Supply Pump"])
        rail = QTreeWidgetItem(fuel, ["  [*] Rail Sensor"])
        rail.setForeground(0, QBrush(QColor("#ff3333"))) # Red alert
        QTreeWidgetItem(fuel, ["  [ ] Injectors"])
        QTreeWidgetItem(root, ["> Transmission"])
        chassis = QTreeWidgetItem(nav_tree, ["> Chassis"])
        nav_tree.expandAll()
        splitter.addWidget(nav_tree)
        splitter.setStretchFactor(0, 1)

        # Center: Schematic Viewport
        scene = QGraphicsScene()
        scene.setBackgroundBrush(QBrush(QColor("#0b1021")))
        
        # Draw some schematic lines
        pen = QPen(QColor("#00ffff"))
        pen.setWidth(2)
        
        # ECU Node
        ecu = scene.addRect(0, 0, 100, 60, pen)
        text = scene.addText("ECU")
        text.setDefaultTextColor(QColor("#00ffff"))
        text.setPos(30, 20)
        
        # Rail Sensor Node
        sensor = scene.addRect(200, 100, 80, 40, QPen(QColor("#ff3333"))) # Red for fault
        text_s = scene.addText("RAIL P.")
        text_s.setDefaultTextColor(QColor("#ff3333"))
        text_s.setPos(210, 110)
        
        # Connection
        line = scene.addLine(100, 30, 240, 100, pen)
        
        # Alert Text in scene
        alert = scene.addText("! SIGNAL RANGE ERROR")
        alert.setDefaultTextColor(QColor("#ff3333"))
        alert.setPos(200, 150)
        
        view = QGraphicsView(scene)
        view.setStyleSheet("border: 1px solid #00ffff;")
        splitter.addWidget(view)
        splitter.setStretchFactor(1, 4)

        # Bottom Deck
        bottom_frame = QFrame()
        bottom_layout = QHBoxLayout(bottom_frame)
        bottom_layout.setContentsMargins(0,0,0,0)
        
        # Event Tape
        tape = QTextEdit()
        tape.setReadOnly(True)
        tape.setText("10:14 DTC P0087 Set\n10:15 Pump Actuated\n10:16 User confirmed connection")
        tape.setMaximumWidth(200)
        bottom_layout.addWidget(tape)
        
        # Scope Placeholder
        scope = QLabel("[ LIVE SCOPE VISUALIZATION ]\n(Imagine a waveform here)")
        scope.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scope.setStyleSheet("border: 1px dashed #005555; color: #005555;")
        bottom_layout.addWidget(scope)
        
        # Action Deck
        actions = QFrame()
        actions_layout = QVBoxLayout(actions)
        actions_layout.addWidget(QLabel("ACTION DECK (Context: Rail)"))
        actions_layout.addWidget(QPushButton("[ ] Reset Relief Valve"))
        btn_cutoff = QPushButton("[X] Cut-off Cylinder 1")
        btn_cutoff.setStyleSheet("background-color: #330000; color: #ff5555; border: 1px solid #ff0000;")
        actions_layout.addWidget(btn_cutoff)
        actions_layout.addWidget(QPushButton("[ ] Leak Test"))
        bottom_layout.addWidget(actions)
        
        layout.addWidget(bottom_frame)
        layout.setStretchFactor(splitter, 4)
        layout.setStretchFactor(bottom_frame, 1)


class CommandCenterWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Theme: Dark Cockpit
        self.setStyleSheet("""
            QWidget {
                background-color: #000000; 
                color: #e0e0e0; 
                font-family: 'Segoe UI', sans-serif;
            }
            QLabel {
                font-size: 14px;
            }
            QPushButton {
                background-color: #222;
                border: 2px solid #444;
                color: #ccc;
                padding: 10px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #444;
                border-color: #888;
            }
            QPushButton:checked {
                background-color: #d68a00; /* Amber */
                color: #000;
            }
            QFrame {
                border: none;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Top Nav
        top_nav = QHBoxLayout()
        top_nav.addWidget(QLabel("[AutoDiag]"))
        top_nav.addWidget(QPushButton("1. OVERVIEW"))
        top_nav.addWidget(QPushButton("2. INTERROGATE"))
        monitor_btn = QPushButton("3. MONITOR")
        monitor_btn.setStyleSheet("background-color: #004400; color: #fff; border-color: #008800;") # Active Green
        top_nav.addWidget(monitor_btn)
        top_nav.addWidget(QPushButton("4. EXECUTE"))
        top_nav.addStretch()
        layout.addLayout(top_nav)

        # Main Area
        main_layout = QHBoxLayout()
        
        # Left Pillar
        pillar = QFrame()
        pillar.setFixedWidth(200)
        pillar.setStyleSheet("background-color: #111; border-right: 2px solid #333;")
        p_layout = QVBoxLayout(pillar)
        
        def add_stat(label, val, color="#fff"):
            lbl = QLabel(f"{label}\n{val}")
            lbl.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {color}; border-bottom: 1px solid #333; padding-bottom: 5px;")
            p_layout.addWidget(lbl)
            
        add_stat("BATT", "13.8 V", "#00ff00")
        add_stat("IGN", "ON", "#00ff00")
        add_stat("VCI", "USB", "#0088ff")
        p_layout.addSpacing(20)
        add_stat("GLOBAL DTC", "3 Faults", "#ffaa00")
        
        p_layout.addWidget(QLabel("Engine: 2\nABS: 0\nBCM: 1"))
        p_layout.addStretch()
        main_layout.addWidget(pillar)
        
        # Mission Bay (Center)
        mission_bay = QFrame()
        mb_layout = QVBoxLayout(mission_bay)
        mb_layout.addWidget(QLabel("LIVE DATA GROUP: AIR/FUEL"))
        
        # Data Grid
        data_grid = QGridLayout()
        data_grid.addWidget(QLabel("MAF Sensor"), 0, 0)
        data_grid.addWidget(QLabel("4.5 g/s"), 0, 1)
        
        data_grid.addWidget(QLabel("O2 Sensor B1"), 1, 0)
        data_grid.addWidget(QLabel("0.6 V"), 1, 1)
        
        stft = QLabel("+3.5 %")
        stft.setStyleSheet("color: #00ff00; font-weight: bold;")
        data_grid.addWidget(QLabel("STFT B1"), 2, 0)
        data_grid.addWidget(stft, 2, 1)
        
        mb_layout.addLayout(data_grid)
        
        # DTC Detail overlay simulation
        dtc_frame = QFrame()
        dtc_frame.setStyleSheet("background-color: #221111; border: 1px solid #880000; padding: 10px; margin-top: 20px;")
        dtc_layout = QVBoxLayout(dtc_frame)
        dtc_layout.addWidget(QLabel("DTC DETAIL: P0171 - System Too Lean (Bank 1)"))
        dtc_layout.addWidget(QLabel("> Status: Confirmed"))
        dtc_layout.addWidget(QLabel("> ECU: 0x10 (Engine)"))
        mb_layout.addWidget(dtc_frame)
        
        mb_layout.addStretch()
        main_layout.addWidget(mission_bay)
        
        # Right Command Rail
        rail = QFrame()
        rail.setFixedWidth(150)
        r_layout = QVBoxLayout(rail)
        r_layout.addWidget(QPushButton("SNAPSHOT"))
        r_layout.addWidget(QPushButton("GRAPH"))
        r_layout.addWidget(QPushButton("FREEZE"))
        r_layout.addSpacing(20)
        r_layout.addWidget(QPushButton("SELECT"))
        r_layout.addWidget(QPushButton("PIDS"))
        r_layout.addStretch()
        r_layout.addWidget(QPushButton("EXIT"))
        main_layout.addWidget(rail)
        
        layout.addLayout(main_layout)
        
        # Footer
        footer = QLabel("LOG: TX 03 ... RX 43 02 01 71 ... [OK]")
        footer.setStyleSheet("color: #666; font-size: 10px;")
        layout.addWidget(footer)


class IndustrialLogicWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Theme: SCADA / Industrial
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0; 
                color: #000000; 
                font-family: 'Tahoma', sans-serif;
                font-size: 11px;
            }
            QTreeWidget, QTableWidget, QTextEdit {
                background-color: #ffffff;
                border: 1px solid #a0a0a0;
            }
            QHeaderView::section {
                background-color: #e0e0e0;
                padding: 4px;
                border: 1px solid #a0a0a0;
            }
            QPushButton {
                background-color: #e0e0e0;
                border: 1px solid #808080;
                padding: 4px 8px;
            }
            QPushButton:hover {
                background-color: #d0d0d0;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(2)
        layout.setContentsMargins(2, 2, 2, 2)

        # Toolbar
        toolbar = QHBoxLayout()
        toolbar.addWidget(QPushButton("CONNECT"))
        toolbar.addWidget(QPushButton("START TRACE"))
        toolbar.addWidget(QPushButton("STOP"))
        force_btn = QPushButton("FORCE ENABLE")
        force_btn.setStyleSheet("color: red; font-weight: bold;")
        toolbar.addWidget(force_btn)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        # Main Splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        # Left: Project Tree
        tree = QTreeWidget()
        tree.setHeaderLabel("PROJECT TREE")
        root = QTreeWidgetItem(tree, ["[-] CAN-C (500k)"])
        ecm = QTreeWidgetItem(root, [" [-] ECM (0x7E0)"])
        QTreeWidgetItem(ecm, ["  [+] Memory"])
        io = QTreeWidgetItem(ecm, ["  [-] I/O"])
        QTreeWidgetItem(io, ["    - DI_Ignition"])
        pedal = QTreeWidgetItem(io, ["    - AI_Pedal_Pos"])
        pedal.setSelected(True)
        QTreeWidgetItem(io, ["    - DO_Injector"])
        QTreeWidgetItem(root, [" [+] TCM (0x7E1)"])
        tree.expandAll()
        splitter.addWidget(tree)

        # Center: Canvas (Simulated)
        canvas_frame = QFrame()
        canvas_frame.setStyleSheet("background-color: #ffffff; border: 1px solid #a0a0a0;")
        cf_layout = QVBoxLayout(canvas_frame)
        
        # A simple visual representation of logic
        logic_scene = QGraphicsScene()
        logic_view = QGraphicsView(logic_scene)
        logic_view.setStyleSheet("border: none;")
        
        # Input Block
        logic_scene.addRect(10, 50, 80, 40, QPen(Qt.GlobalColor.black))
        t1 = logic_scene.addText("Pedal %")
        t1.setPos(20, 55)
        
        # Value
        t2 = logic_scene.addText("> 25%")
        t2.setPos(100, 60)
        
        # Logic Block
        logic_scene.addRect(150, 40, 60, 60, QPen(Qt.GlobalColor.black))
        t3 = logic_scene.addText("MAP")
        t3.setPos(160, 60)
        
        # Output Block
        logic_scene.addRect(250, 50, 80, 40, QPen(Qt.GlobalColor.black))
        t4 = logic_scene.addText("Throttle")
        t4.setPos(260, 55)
        
        # Connecting lines
        logic_scene.addLine(90, 70, 150, 70)
        logic_scene.addLine(210, 70, 250, 70)
        
        cf_layout.addWidget(QLabel("MAIN CANVAS [Logic View]"))
        cf_layout.addWidget(logic_view)
        splitter.addWidget(canvas_frame)

        # Right: Signal Watch
        watch_table = QTableWidget(5, 2)
        watch_table.setHorizontalHeaderLabels(["Name", "Val"])
        watch_table.verticalHeader().setVisible(False)
        
        def add_row(row, name, val):
            watch_table.setItem(row, 0, QTableWidgetItem(name))
            watch_table.setItem(row, 1, QTableWidgetItem(val))
            
        add_row(0, "RPM", "850")
        add_row(1, "V_BATT", "14.1")
        add_row(2, "PEDAL_P", "25%")
        add_row(3, "THR_ANG", "12%")
        add_row(4, "T_COOL", "98C")
        
        splitter.addWidget(watch_table)
        
        # Sizing
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        splitter.setStretchFactor(2, 1)

        # Bottom: Terminal
        term_frame = QFrame()
        tf_layout = QVBoxLayout(term_frame)
        tf_layout.addWidget(QLabel("TERMINAL / ALARMS"))
        term = QTextEdit()
        term.setReadOnly(True)
        term.setText("[10:22:01.450] [CAN-C] ID:120 LEN:8 DATA: 00 A1 FF ...\n[10:22:01.455] [ALARM] DTC P2138 Active - Pedal Pos Correlation")
        term.setStyleSheet("font-family: 'Consolas'; font-size: 10px;")
        term.setMaximumHeight(100)
        tf_layout.addWidget(term)
        
        layout.addWidget(term_frame)


class MockupViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DACOS AutoDiag Layout Mockups")
        self.resize(1200, 800)
        
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        self.tabs.addTab(KineticSchematicWidget(), "1. Kinetic Schematic")
        self.tabs.addTab(CommandCenterWidget(), "2. Command Center")
        self.tabs.addTab(IndustrialLogicWidget(), "3. Industrial Logic")
        
        # Style the main tab widget to be neutral
        self.setStyleSheet("""
            QTabWidget::pane { border: 0; }
            QTabBar::tab { font-size: 12px; padding: 10px; }
            QTabBar::tab:selected { font-weight: bold; }
        """)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MockupViewer()
    window.show()
    sys.exit(app.exec())

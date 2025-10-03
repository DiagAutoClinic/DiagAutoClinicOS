import sqlite3
import os

class DTCDatabase:
    def __init__(self, db_path="dtc_database.db"):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._create_tables()
        self._populate_data()

    def _create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS dtc_codes (
                code TEXT PRIMARY KEY,
                description TEXT,
                severity TEXT
            )
        ''')
        self.conn.commit()

    def _populate_data(self):
        sample_dtcs = [
            ('P0300', 'Random/Multiple Cylinder Misfire Detected', 'High'),
            ('P0301', 'Cylinder 1 Misfire Detected', 'High'),
            ('P0420', 'Catalyst System Efficiency Below Threshold', 'Medium'),
            ('P0171', 'System Too Lean (Bank 1)', 'Medium'),
            ('P0700', 'Transmission Control System Malfunction', 'High'),
            ('U0100', 'Lost Communication with ECM/PCM A', 'Critical'),
            ('B0001', 'Front Impact Sensor Circuit Malfunction', 'Critical'),
            ('C1201', 'ABS System Malfunction', 'High'),
        ]
        self.cursor.executemany('INSERT OR IGNORE INTO dtc_codes VALUES (?, ?, ?)', sample_dtcs)
        self.conn.commit()

    def get_dtc_info(self, code):
        self.cursor.execute('SELECT description, severity FROM dtc_codes WHERE code = ?', (code,))
        result = self.cursor.fetchone()
        if result:
            return {'description': result[0], 'severity': result[1]}
        return {'description': 'Unknown DTC Code', 'severity': 'Unknown'}

    def close(self):
        self.conn.close()

# Test
if __name__ == "__main__":
    db = DTCDatabase()
    print(db.get_dtc_info('P0300'))
    db.close()

# DACOS VIN Truth Engine API Installation Guide

## Overview

The DACOS VIN Truth Engine is a cryptographic VIN (Vehicle Identification Number) decoding and verification system that provides epistemological analysis with full provenance tracking. This API serves as the core intelligence layer for automotive diagnostics.

## Features

- **7-Layer Truth Engine**: Cryptographic verification through multiple independent sources
- **Epistemological Analysis**: Confidence scoring with provenance tracking
- **Forensic Audit Trail**: Immutable operation logging with cryptographic chaining
- **Multi-Signature Verification**: Cross-validation from multiple truth sources
- **REST API**: FastAPI-based endpoints for integration

## System Requirements

### Minimum Requirements
- Python 3.8+
- 4GB RAM
- 1GB disk space for storage and audit trails

### Recommended Requirements
- Python 3.10+
- 8GB RAM
- SSD storage for performance
- Network connectivity for market context validation

## Installation

### 1. Install Core Dependencies

First, ensure you have the base DiagAutoClinicOS requirements:

```bash
pip install -r requirements.txt
```

### 2. Install API Dependencies

The VIN Truth Engine API requires additional packages:

```bash
pip install fastapi uvicorn
```

### 3. Install Development Dependencies (Optional)

For testing and development:

```bash
pip install -r requirements-dev.txt
```

## Configuration

### Environment Variables

Set the master key for cryptographic operations:

```bash
export DACOS_VIN_MASTER_KEY="your-32-byte-hex-key-here"
```

If not set, a secure key will be auto-generated and stored.

### Storage Configuration

The engine creates a `vin_truth_storage` directory in the current working directory for:
- Audit trail files
- Master key storage
- VIN rules database

## Running the API

### Development Mode

```bash
python core/dacos_vin_truth_engin.py
```

### Production Mode

```bash
uvicorn core.dacos_vin_truth_engin:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

### POST /api/v1/decode

Decode and verify a VIN with full epistemological analysis.

**Request:**
```json
{
  "vin": "1HGCM82633A123456",
  "context": {
    "market": "US",
    "session_id": "optional_session_id"
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "vin": "1HGCM82633A123456",
    "identity_hash": "...",
    "decoded": {
      "manufacturer": {"value": "Honda", "confidence": 0.95},
      "model": {"value": "Accord", "confidence": 0.87},
      "engine": {"value": "2.4L I4", "confidence": 0.82},
      "market": {"value": "US", "confidence": 0.98},
      "overall_confidence": 0.91
    },
    "integrity": {
      "result_hash": "...",
      "signature": "...",
      "integrity_proof": "..."
    },
    "epistemology": {
      "verification_level": "HIGH_CONFIDENCE",
      "recommended_use": ["SAFE_FOR_DIAGNOSTICS", "SAFE_FOR_PARTS_ORDERING"],
      "warnings": []
    }
  }
}
```

### GET /api/v1/verify/{integrity_hash}

Verify the integrity of a previous decoding result.

**Response:**
```json
{
  "verification": "VALID",
  "timestamp": "2025-12-30T05:30:00Z",
  "details": "Result integrity confirmed"
}
```

## Testing

### Automated Testing

Run the test suite:

```bash
pytest tests/test_vin_truth_engine.py -v
```

### Manual Testing

1. Start the API server
2. Use curl or a REST client to test endpoints
3. Check the interactive API documentation at `http://localhost:8000/docs`

### Sample Test Commands

```bash
# Test VIN decoding
curl -X POST "http://localhost:8000/api/v1/decode" \
  -H "Content-Type: application/json" \
  -d '{"vin":"1HGCM82633A123456"}'

# Test integrity verification
curl -X GET "http://localhost:8000/api/v1/verify/sample_hash"
```

## Integration

### AutoDiag Integration

The engine automatically attempts to connect to AutoDiag suite for enhanced diagnostics.

### Charlemaine AI Integration

Provides VIN-based knowledge to the Charlemaine AI agent for contextual diagnostics.

### Custom Integration

```python
from core.dacos_vin_truth_engin import DACOSVinTruthEngine
import os

# Initialize engine
master_key = os.environ.get('DACOS_VIN_MASTER_KEY')
if not master_key:
    master_key = os.urandom(32)

engine = DACOSVinTruthEngine(master_key, Path('./vin_storage'))

# Decode VIN
result = engine.decode("1HGCM82633A123456")
print(f"Manufacturer: {result['decoded']['manufacturer']['value']}")
```

## Security Considerations

- **Master Key**: Store securely, never commit to version control
- **Audit Trails**: Regularly backup audit files for forensic analysis
- **Network Security**: Use HTTPS in production environments
- **Access Control**: Implement authentication for production deployments

## Troubleshooting

### Common Issues

1. **Missing Dependencies**
   ```
   ModuleNotFoundError: No module named 'fastapi'
   ```
   Solution: `pip install fastapi uvicorn`

2. **Unicode Encoding Errors**
   ```
   UnicodeEncodeError: 'charmap' codec can't encode character
   ```
   Solution: Use UTF-8 encoding or avoid Unicode symbols in print statements

3. **Rules File Not Found**
   ```
   FileNotFoundError: dacos_vin_rules_v0.0.4.json
   ```
   Solution: The engine creates a dummy rules file automatically for testing

4. **Port Already in Use**
   ```
   [Errno 48] Address already in use
   ```
   Solution: Change port with `--port 8001` or stop other services

### Performance Tuning

- Increase workers for high load: `--workers 8`
- Use gunicorn for production: `gunicorn core.dacos_vin_truth_engin:app -w 4 -k uvicorn.workers.UvicornWorker`

## Support

For issues and questions:
- Check the audit logs in `vin_truth_storage/`
- Review the epistemological warnings in API responses
- Ensure all dependencies are correctly installed

## Version History

- v0.0.1: Initial release with basic VIN decoding
- v0.0.2: Added cryptographic verification
- v0.0.3: Multi-signature confidence engine
- v0.0.4: REST API and integration bridges
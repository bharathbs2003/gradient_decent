# API Documentation

## Overview

The Multilingual AI Video Dubbing Platform provides a comprehensive REST API for creating high-fidelity multilingual dubbed videos with synchronized, realistic facial animations.

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

The API uses JWT Bearer token authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## Core Endpoints

### Authentication

#### POST /auth/login
Login with email/username and password.

**Request:**
```json
{
  "username": "user@example.com",
  "password": "your-password"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

#### POST /auth/register
Register a new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "username": "username",
  "full_name": "Full Name",
  "password": "secure-password"
}
```

### Dubbing Operations

#### POST /dubbing/process
Create a new dubbing job for multilingual video processing.

**Request:** (multipart/form-data)
- `video_file`: Video file (MP4, MOV, AVI, MKV)
- `target_languages`: JSON array of language codes
- `source_language`: Source language (optional, auto-detect if not provided)
- `enable_voice_cloning`: Boolean (default: true)
- `enable_emotion_preservation`: Boolean (default: true)
- `quality_mode`: "structural" or "end_to_end" (default: "structural")
- `require_human_review`: Boolean (default: false)

**Response:**
```json
{
  "id": "job-uuid",
  "status": "pending",
  "progress": 0.0,
  "created_at": "2024-01-01T00:00:00Z",
  "target_languages": ["es", "fr", "de"],
  "estimated_completion": "2024-01-01T01:00:00Z"
}
```

#### GET /dubbing/jobs/{job_id}
Get dubbing job status and results.

**Response:**
```json
{
  "id": "job-uuid",
  "status": "completed",
  "progress": 1.0,
  "created_at": "2024-01-01T00:00:00Z",
  "completed_at": "2024-01-01T00:45:00Z",
  "target_languages": ["es", "fr", "de"],
  "output_data": {
    "videos": {
      "es": {"output_video_path": "/path/to/spanish.mp4"},
      "fr": {"output_video_path": "/path/to/french.mp4"},
      "de": {"output_video_path": "/path/to/german.mp4"}
    }
  }
}
```

#### GET /dubbing/jobs/{job_id}/progress
Get detailed progress information for a dubbing job.

**Response:**
```json
{
  "job_id": "job-uuid",
  "overall_progress": 0.6,
  "current_stage": "Face Animation",
  "stages": [
    {"name": "Ethics Check", "progress": 1.0},
    {"name": "Speech Recognition", "progress": 1.0},
    {"name": "Translation", "progress": 1.0},
    {"name": "Voice Synthesis", "progress": 1.0},
    {"name": "Face Animation", "progress": 0.3},
    {"name": "Quality Check", "progress": 0.0}
  ],
  "estimated_time_remaining": 300,
  "quality_metrics": {
    "es": {"lse_c": 0.87, "fid": 12.3}
  }
}
```

#### GET /dubbing/preview/{job_id}
Get real-time preview of dubbed content.

**Query Parameters:**
- `language`: Target language code
- `segment_id`: Specific segment ID (optional)

**Response:**
```json
{
  "preview_url": "https://preview.example.com/job-uuid/es",
  "expires_in": 3600
}
```

#### POST /dubbing/quality-check/{job_id}
Run quality checks on dubbed content.

**Request:**
```json
{
  "check_lip_sync": true,
  "check_visual_fidelity": true,
  "check_emotion_preservation": true,
  "check_translation_quality": true,
  "target_language": "es"
}
```

**Response:**
```json
{
  "job_id": "job-uuid",
  "language": "es",
  "metrics": {
    "lse_c_score": 0.87,
    "fid_score": 12.3,
    "au_correlation": 0.78,
    "bleu_score": 38.5,
    "overall_score": 0.85
  },
  "passed": true,
  "issues": [],
  "recommendations": []
}
```

#### GET /dubbing/supported-languages
Get list of supported languages with capabilities.

**Response:**
```json
[
  {
    "code": "en",
    "name": "English",
    "native_name": "English",
    "supports_asr": true,
    "supports_tts": true,
    "supports_translation": true,
    "voice_count": 15
  }
]
```

### Project Management

#### GET /projects
List user's projects.

**Query Parameters:**
- `skip`: Number of items to skip (default: 0)
- `limit`: Number of items to return (default: 100)

#### POST /projects
Create a new project.

#### GET /projects/{project_id}
Get project details.

#### PUT /projects/{project_id}
Update project.

#### DELETE /projects/{project_id}
Delete project.

### Ethics & Compliance

#### GET /ethics/consent
Get consent status for a project.

#### POST /ethics/consent
Create or update consent record.

#### GET /ethics/watermark/{project_id}
Get watermarking information.

#### GET /ethics/provenance/{project_id}
Get provenance tracking information.

## Error Responses

All endpoints return consistent error responses:

```json
{
  "error": "Error message",
  "code": "ERROR_CODE",
  "details": "Additional details (optional)"
}
```

### HTTP Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Validation Error
- `429` - Rate Limit Exceeded
- `500` - Internal Server Error
- `503` - Service Unavailable

## Rate Limits

- General API: 100 requests per minute
- File uploads: 5 requests per minute
- Preview generation: 20 requests per minute

## Quality Metrics

The platform tracks several quality metrics as defined in the PRD:

- **LSE-C (Lip Sync)**: Target ≥ 0.85
- **FID (Visual Fidelity)**: Target ≤ 15.0
- **AU Correlation (Emotion)**: Target ≥ 0.75
- **BLEU (Translation)**: Target ≥ 35.0

## Supported File Formats

### Video Input
- MP4 (recommended)
- MOV
- AVI
- MKV
- Maximum size: 500MB

### Audio Output
- WAV (default)
- MP3
- AAC

### Video Output
- MP4 (H.264)
- Resolutions: 720p, 1080p, 4K (batch processing)

## WebSocket Events

For real-time updates, connect to the WebSocket endpoint:

```
ws://localhost:8000/ws/jobs/{job_id}
```

Events:
- `progress_update`: Job progress changed
- `stage_complete`: Processing stage completed
- `job_complete`: Job finished
- `job_failed`: Job failed
- `quality_check`: Quality metrics available

## SDKs and Libraries

Official SDKs are available for:
- Python
- JavaScript/TypeScript
- cURL examples

See the `/docs/sdks/` directory for implementation examples.
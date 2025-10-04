"""
Ethics service for consent management, watermarking, and provenance tracking
"""

import hashlib
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional, List
import structlog

from sqlalchemy.orm import Session
from app.models import ConsentRecord, WatermarkRecord, ProvenanceRecord, Project
from app.core.config import get_settings

logger = structlog.get_logger()
settings = get_settings()


class EthicsService:
    """Service for ethical AI compliance"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def check_consent_status(self, project_id: str) -> Dict[str, Any]:
        """Check consent status for a project"""
        logger.info("Checking consent status", project_id=project_id)
        
        consent_records = self.db.query(ConsentRecord).filter(
            ConsentRecord.project_id == project_id,
            ConsentRecord.is_granted == True
        ).all()
        
        active_consents = [
            record for record in consent_records
            if record.is_active
        ]
        
        return {
            "has_consent": len(active_consents) > 0,
            "consent_count": len(active_consents),
            "consent_types": [record.consent_type for record in active_consents]
        }
    
    async def create_consent_record(
        self,
        user_id: str,
        project_id: str,
        consent_type: str,
        subject_name: str,
        subject_identifier: str,
        permitted_uses: List[str],
        restrictions: Optional[List[str]] = None,
        expiry_date: Optional[datetime] = None
    ) -> ConsentRecord:
        """Create a new consent record"""
        logger.info(
            "Creating consent record",
            project_id=project_id,
            consent_type=consent_type,
            subject_name=subject_name
        )
        
        consent_record = ConsentRecord(
            user_id=user_id,
            project_id=project_id,
            consent_type=consent_type,
            subject_name=subject_name,
            subject_identifier=subject_identifier,
            permitted_uses=permitted_uses,
            restrictions=restrictions or [],
            expiry_date=expiry_date
        )
        
        self.db.add(consent_record)
        self.db.commit()
        self.db.refresh(consent_record)
        
        logger.info("Consent record created", consent_id=str(consent_record.id))
        
        return consent_record
    
    async def grant_consent(
        self,
        consent_id: str,
        document_path: Optional[str] = None
    ):
        """Grant consent for a consent record"""
        consent_record = self.db.query(ConsentRecord).filter(
            ConsentRecord.id == consent_id
        ).first()
        
        if not consent_record:
            raise ValueError("Consent record not found")
        
        consent_record.grant_consent(document_path)
        self.db.commit()
        
        logger.info("Consent granted", consent_id=consent_id)
    
    async def revoke_consent(self, consent_id: str):
        """Revoke consent"""
        consent_record = self.db.query(ConsentRecord).filter(
            ConsentRecord.id == consent_id
        ).first()
        
        if not consent_record:
            raise ValueError("Consent record not found")
        
        consent_record.revoke_consent()
        self.db.commit()
        
        logger.info("Consent revoked", consent_id=consent_id)
    
    async def apply_watermark(
        self,
        project_id: str,
        content_path: str,
        watermark_type: str = "invisible",
        watermark_method: str = "LSB",
        strength: Optional[float] = None
    ) -> str:
        """Apply watermark to content"""
        logger.info(
            "Applying watermark",
            project_id=project_id,
            content_path=content_path,
            watermark_type=watermark_type
        )
        
        if not os.path.exists(content_path):
            raise FileNotFoundError(f"Content file not found: {content_path}")
        
        # Generate watermark payload
        payload = {
            "project_id": project_id,
            "timestamp": datetime.utcnow().isoformat(),
            "platform": "Multilingual AI Dubbing Platform",
            "version": "1.0.0",
            "ai_generated": True
        }
        
        # Calculate content hash
        content_hash = await self._calculate_file_hash(content_path)
        
        # Apply watermark (simplified implementation)
        watermarked_path = await self._apply_watermark_to_file(
            content_path,
            payload,
            watermark_type,
            watermark_method,
            strength or settings.WATERMARK_STRENGTH
        )
        
        # Create watermark record
        watermark_record = WatermarkRecord(
            project_id=project_id,
            watermark_type=watermark_type,
            watermark_method=watermark_method,
            watermark_strength=strength or settings.WATERMARK_STRENGTH,
            content_type=self._get_content_type(content_path),
            content_path=watermarked_path,
            content_hash=content_hash,
            payload_data=payload,
            payload_hash=hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest(),
            detection_key=self._generate_detection_key(payload),
            is_detectable=True,
            detection_confidence=0.95
        )
        
        self.db.add(watermark_record)
        self.db.commit()
        
        logger.info(
            "Watermark applied",
            watermark_id=str(watermark_record.id),
            watermarked_path=watermarked_path
        )
        
        return watermarked_path
    
    async def detect_watermark(self, content_path: str) -> Dict[str, Any]:
        """Detect watermark in content"""
        logger.info("Detecting watermark", content_path=content_path)
        
        # This would use watermark detection algorithms
        # For now, return mock detection result
        
        return {
            "has_watermark": True,
            "confidence": 0.92,
            "payload": {
                "platform": "Multilingual AI Dubbing Platform",
                "ai_generated": True,
                "timestamp": "2024-01-01T00:00:00"
            }
        }
    
    async def create_provenance_record(
        self,
        project_id: str,
        content_path: str,
        processing_chain: List[Dict[str, Any]],
        source_content_hash: Optional[str] = None,
        generation_parameters: Optional[Dict[str, Any]] = None
    ) -> ProvenanceRecord:
        """Create provenance record for content traceability"""
        logger.info(
            "Creating provenance record",
            project_id=project_id,
            content_path=content_path
        )
        
        content_hash = await self._calculate_file_hash(content_path)
        
        # Create C2PA manifest (simplified)
        c2pa_manifest = {
            "claim_generator": "Multilingual AI Dubbing Platform v1.0.0",
            "claim_generator_info": {
                "name": "AI Dubbing Platform",
                "version": "1.0.0"
            },
            "assertions": [
                {
                    "label": "c2pa.actions",
                    "data": {
                        "actions": [
                            {
                                "action": "c2pa.ai_generative_training",
                                "when": datetime.utcnow().isoformat(),
                                "softwareAgent": "Multilingual AI Dubbing Platform"
                            }
                        ]
                    }
                }
            ],
            "signature_info": {
                "issuer": "AI Dubbing Platform",
                "time": datetime.utcnow().isoformat()
            }
        }
        
        provenance_record = ProvenanceRecord(
            project_id=project_id,
            content_type=self._get_content_type(content_path),
            content_path=content_path,
            content_hash=content_hash,
            processing_chain=processing_chain,
            source_content_hash=source_content_hash,
            generation_timestamp=datetime.utcnow(),
            generation_parameters=generation_parameters or {},
            c2pa_manifest=c2pa_manifest,
            c2pa_signature=self._generate_c2pa_signature(c2pa_manifest)
        )
        
        self.db.add(provenance_record)
        self.db.commit()
        self.db.refresh(provenance_record)
        
        logger.info(
            "Provenance record created",
            provenance_id=str(provenance_record.id)
        )
        
        return provenance_record
    
    async def update_provenance_record(
        self,
        project_id: str,
        processing_step: Dict[str, Any]
    ):
        """Update provenance record with new processing step"""
        provenance_record = self.db.query(ProvenanceRecord).filter(
            ProvenanceRecord.project_id == project_id
        ).order_by(ProvenanceRecord.created_at.desc()).first()
        
        if provenance_record:
            provenance_record.add_processing_step(
                step_name=processing_step["step"],
                model_name=processing_step.get("model", "unknown"),
                parameters=processing_step,
                timestamp=datetime.fromisoformat(processing_step["timestamp"])
            )
            self.db.commit()
    
    async def add_human_review(
        self,
        project_id: str,
        reviewer: str,
        notes: Optional[str] = None
    ):
        """Add human review to provenance record"""
        provenance_record = self.db.query(ProvenanceRecord).filter(
            ProvenanceRecord.project_id == project_id
        ).order_by(ProvenanceRecord.created_at.desc()).first()
        
        if provenance_record:
            provenance_record.add_human_review(reviewer, notes)
            self.db.commit()
    
    async def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of file"""
        hash_sha256 = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        
        return hash_sha256.hexdigest()
    
    async def _apply_watermark_to_file(
        self,
        content_path: str,
        payload: Dict[str, Any],
        watermark_type: str,
        method: str,
        strength: float
    ) -> str:
        """Apply watermark to file (simplified implementation)"""
        # This would use actual watermarking algorithms
        # For now, just copy the file with a watermarked suffix
        
        base_name, ext = os.path.splitext(content_path)
        watermarked_path = f"{base_name}_watermarked{ext}"
        
        # Copy file (in practice, apply actual watermarking)
        import shutil
        shutil.copy2(content_path, watermarked_path)
        
        return watermarked_path
    
    def _get_content_type(self, file_path: str) -> str:
        """Determine content type from file extension"""
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext in ['.mp4', '.avi', '.mov', '.mkv']:
            return 'video'
        elif ext in ['.wav', '.mp3', '.aac', '.flac']:
            return 'audio'
        elif ext in ['.jpg', '.jpeg', '.png', '.bmp']:
            return 'image'
        else:
            return 'unknown'
    
    def _generate_detection_key(self, payload: Dict[str, Any]) -> str:
        """Generate detection key for watermark"""
        payload_str = json.dumps(payload, sort_keys=True)
        return hashlib.md5(payload_str.encode()).hexdigest()
    
    def _generate_c2pa_signature(self, manifest: Dict[str, Any]) -> str:
        """Generate C2PA digital signature (simplified)"""
        manifest_str = json.dumps(manifest, sort_keys=True)
        return hashlib.sha256(manifest_str.encode()).hexdigest()
    
    async def get_ethics_dashboard(self, project_id: str) -> Dict[str, Any]:
        """Get ethics dashboard data for a project"""
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError("Project not found")
        
        # Get consent records
        consent_records = self.db.query(ConsentRecord).filter(
            ConsentRecord.project_id == project_id
        ).all()
        
        # Get watermark records
        watermark_records = self.db.query(WatermarkRecord).filter(
            WatermarkRecord.project_id == project_id
        ).all()
        
        # Get provenance records
        provenance_records = self.db.query(ProvenanceRecord).filter(
            ProvenanceRecord.project_id == project_id
        ).all()
        
        return {
            "project_id": project_id,
            "consent_status": {
                "total_records": len(consent_records),
                "active_consents": len([r for r in consent_records if r.is_active]),
                "consent_types": list(set([r.consent_type for r in consent_records]))
            },
            "watermarking_status": {
                "total_watermarks": len(watermark_records),
                "watermark_types": list(set([r.watermark_type for r in watermark_records])),
                "average_strength": sum([r.watermark_strength for r in watermark_records]) / len(watermark_records) if watermark_records else 0
            },
            "provenance_status": {
                "total_records": len(provenance_records),
                "c2pa_compliant": len([r for r in provenance_records if r.is_c2pa_compliant]),
                "human_reviewed": len([r for r in provenance_records if r.human_review])
            },
            "compliance_score": self._calculate_compliance_score(
                consent_records, watermark_records, provenance_records, project
            )
        }
    
    def _calculate_compliance_score(
        self,
        consent_records: List[ConsentRecord],
        watermark_records: List[WatermarkRecord],
        provenance_records: List[ProvenanceRecord],
        project: Project
    ) -> float:
        """Calculate overall compliance score"""
        score = 0.0
        max_score = 100.0
        
        # Consent compliance (30 points)
        if project.require_consent:
            active_consents = [r for r in consent_records if r.is_active]
            if active_consents:
                score += 30.0
        else:
            score += 30.0  # No consent required
        
        # Watermarking compliance (30 points)
        if project.enable_watermarking:
            if watermark_records:
                avg_quality = sum([
                    (r.psnr or 0) / 40 + (r.ssim or 0)  # Normalize quality metrics
                    for r in watermark_records
                ]) / len(watermark_records)
                score += min(30.0, avg_quality * 30)
        else:
            score += 30.0  # No watermarking required
        
        # Provenance compliance (40 points)
        if project.enable_provenance:
            if provenance_records:
                c2pa_compliant = len([r for r in provenance_records if r.is_c2pa_compliant])
                human_reviewed = len([r for r in provenance_records if r.human_review])
                
                score += (c2pa_compliant / len(provenance_records)) * 20  # C2PA compliance
                score += (human_reviewed / len(provenance_records)) * 20  # Human review
        else:
            score += 40.0  # No provenance required
        
        return min(100.0, score)
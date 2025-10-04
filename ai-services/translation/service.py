"""
Translation Service using SeamlessM4T and other multilingual models
"""

import asyncio
from typing import Dict, Any, List, Optional

import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
from pydantic import BaseModel
import sacrebleu

from ..common.base_service import BaseAIService
from ..common.config import TranslationConfig


class TranslationRequest(BaseModel):
    """Translation request"""
    text: str
    source_language: str
    target_language: str
    context: Optional[str] = None
    max_length: Optional[int] = None


class TranslationResult(BaseModel):
    """Translation result"""
    translated_text: str
    source_language: str
    target_language: str
    confidence_score: float
    bleu_score: Optional[float] = None
    processing_time: float


class TranslationService(BaseAIService):
    """Translation service using multilingual models"""
    
    def __init__(self):
        config = TranslationConfig()
        super().__init__(config)
        self.tokenizer = None
        self.model = None
        self.pipeline = None
    
    async def load_model(self):
        """Load translation model"""
        self.logger.info("Loading translation model", model=self.config.translation_model)
        
        try:
            if self.config.translation_model == "seamlessM4T":
                # Load SeamlessM4T model
                model_name = "facebook/seamless-m4t-medium"
                
                self.tokenizer = AutoTokenizer.from_pretrained(
                    model_name,
                    cache_dir=self.config.model_cache_dir
                )
                
                self.model = AutoModelForSeq2SeqLM.from_pretrained(
                    model_name,
                    cache_dir=self.config.model_cache_dir,
                    torch_dtype=torch.float16 if self.device.type == "cuda" else torch.float32
                ).to(self.device)
                
                # Create pipeline for easier inference
                self.pipeline = pipeline(
                    "translation",
                    model=self.model,
                    tokenizer=self.tokenizer,
                    device=0 if self.device.type == "cuda" else -1
                )
                
            else:
                # Fallback to other models
                model_name = "facebook/m2m100_1.2B"
                
                self.tokenizer = AutoTokenizer.from_pretrained(
                    model_name,
                    cache_dir=self.config.model_cache_dir
                )
                
                self.model = AutoModelForSeq2SeqLM.from_pretrained(
                    model_name,
                    cache_dir=self.config.model_cache_dir
                ).to(self.device)
            
            self.logger.info(
                "Translation model loaded successfully",
                model=self.config.translation_model,
                device=str(self.device)
            )
            
        except Exception as e:
            self.logger.error("Failed to load translation model", error=str(e))
            raise
    
    async def process(self, input_data: Dict[str, Any]) -> TranslationResult:
        """Process translation request"""
        request = TranslationRequest(**input_data)
        
        self.logger.info(
            "Processing translation request",
            source_lang=request.source_language,
            target_lang=request.target_language,
            text_length=len(request.text)
        )
        
        # Validate languages
        if request.source_language not in self.config.supported_languages:
            raise ValueError(f"Unsupported source language: {request.source_language}")
        
        if request.target_language not in self.config.supported_languages:
            raise ValueError(f"Unsupported target language: {request.target_language}")
        
        # Perform translation
        translated_text, confidence = await self._translate_text(
            request.text,
            request.source_language,
            request.target_language,
            max_length=request.max_length or self.config.max_length
        )
        
        return TranslationResult(
            translated_text=translated_text,
            source_language=request.source_language,
            target_language=request.target_language,
            confidence_score=confidence,
            processing_time=0.0  # Will be set by base service
        )
    
    async def _translate_text(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        max_length: int = 512
    ) -> tuple[str, float]:
        """Translate text using the loaded model"""
        try:
            if self.pipeline:
                # Use pipeline for translation
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None,
                    lambda: self.pipeline(
                        text,
                        src_lang=source_lang,
                        tgt_lang=target_lang,
                        max_length=max_length
                    )
                )
                
                translated_text = result[0]["translation_text"]
                confidence = result[0].get("score", 0.8)  # Default confidence
                
            else:
                # Manual tokenization and generation
                # Set source language
                self.tokenizer.src_lang = source_lang
                
                # Tokenize input
                inputs = self.tokenizer(
                    text,
                    return_tensors="pt",
                    max_length=max_length,
                    truncation=True,
                    padding=True
                ).to(self.device)
                
                # Generate translation
                with torch.no_grad():
                    generated_tokens = self.model.generate(
                        **inputs,
                        forced_bos_token_id=self.tokenizer.get_lang_id(target_lang),
                        max_length=max_length,
                        num_beams=4,
                        early_stopping=True,
                        return_dict_in_generate=True,
                        output_scores=True
                    )
                
                # Decode translation
                translated_text = self.tokenizer.batch_decode(
                    generated_tokens.sequences,
                    skip_special_tokens=True
                )[0]
                
                # Calculate confidence from scores
                scores = generated_tokens.scores
                if scores:
                    avg_score = torch.stack(scores).mean().item()
                    confidence = torch.sigmoid(torch.tensor(avg_score)).item()
                else:
                    confidence = 0.8
            
            return translated_text.strip(), confidence
            
        except Exception as e:
            self.logger.error("Translation failed", error=str(e))
            raise
    
    async def calculate_bleu_score(
        self,
        translated_text: str,
        reference_text: str
    ) -> float:
        """Calculate BLEU score for translation quality"""
        try:
            bleu = sacrebleu.sentence_bleu(
                translated_text,
                [reference_text]
            )
            return bleu.score
        except Exception as e:
            self.logger.warning("BLEU calculation failed", error=str(e))
            return 0.0
    
    async def batch_translate(
        self,
        texts: List[str],
        source_lang: str,
        target_lang: str
    ) -> List[TranslationResult]:
        """Batch translation for multiple texts"""
        results = []
        
        # Process in batches to avoid memory issues
        batch_size = self.config.max_batch_size
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            batch_results = await asyncio.gather(*[
                self.process({
                    "text": text,
                    "source_language": source_lang,
                    "target_language": target_lang
                })
                for text in batch
            ])
            
            results.extend(batch_results)
        
        return results
    
    def create_app(self):
        """Create FastAPI app with additional translation endpoints"""
        app = super().create_app()
        
        @app.post("/translate", response_model=TranslationResult)
        async def translate(request: TranslationRequest):
            """Translate text"""
            return await self.process(request.dict())
        
        @app.post("/batch-translate")
        async def batch_translate_endpoint(
            texts: List[str],
            source_language: str,
            target_language: str
        ):
            """Batch translate multiple texts"""
            results = await self.batch_translate(texts, source_language, target_language)
            return {"results": results}
        
        @app.post("/calculate-bleu")
        async def calculate_bleu(
            translated_text: str,
            reference_text: str
        ):
            """Calculate BLEU score"""
            score = await self.calculate_bleu_score(translated_text, reference_text)
            return {"bleu_score": score}
        
        @app.get("/supported-languages")
        async def get_supported_languages():
            """Get list of supported languages"""
            return {
                "languages": [
                    {"code": lang, "name": self._get_language_name(lang)}
                    for lang in self.config.supported_languages
                ]
            }
        
        return app
    
    def _get_language_name(self, code: str) -> str:
        """Get language name from code"""
        language_names = {
            "en": "English", "es": "Spanish", "fr": "French", "de": "German",
            "it": "Italian", "pt": "Portuguese", "ru": "Russian", "zh": "Chinese",
            "ja": "Japanese", "ko": "Korean", "ar": "Arabic", "hi": "Hindi",
            "th": "Thai", "vi": "Vietnamese", "tr": "Turkish", "pl": "Polish",
            "nl": "Dutch", "sv": "Swedish", "da": "Danish", "no": "Norwegian",
            "fi": "Finnish", "el": "Greek", "he": "Hebrew", "cs": "Czech",
            "hu": "Hungarian", "ro": "Romanian", "bg": "Bulgarian", "hr": "Croatian",
            "sk": "Slovak", "sl": "Slovenian", "et": "Estonian", "lv": "Latvian",
            "lt": "Lithuanian", "mt": "Maltese", "ga": "Irish", "cy": "Welsh",
            "eu": "Basque", "ca": "Catalan", "gl": "Galician", "is": "Icelandic",
            "mk": "Macedonian", "sq": "Albanian", "sr": "Serbian", "bs": "Bosnian",
            "me": "Montenegrin", "az": "Azerbaijani", "kk": "Kazakh", "ky": "Kyrgyz",
            "uz": "Uzbek", "tg": "Tajik"
        }
        return language_names.get(code, code.upper())


def main():
    """Run translation service"""
    service = TranslationService()
    service.run()


if __name__ == "__main__":
    main()
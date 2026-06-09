# backend/app/services/database.py
from sqlalchemy.orm import Session
from app import models
from typing import List, Optional, Tuple
from datetime import datetime


class DatabaseService:
    def __init__(self, db: Session):
        self.db = db
    
    def store_translation(
    self,
    input_text: str,
    output_text: str,
    sentiment: str,
    confidence: float,
    detected_slang_terms: list,
    unknown_terms: list,
    model_version: str
    ) -> int:
        print(f"DEBUG: store_translation called")
        print(f"  - input_text: {input_text[:50]}...")
        print(f"  - sentiment: {sentiment}")
        print(f"  - confidence: {confidence}")
        print(f"  - model_version: {model_version}")
        
        try:
            translation = models.Translation(
                input_text=input_text,
                output_text=output_text,
                sentiment=sentiment,
                confidence=confidence,
                detected_slang_terms=detected_slang_terms,
                unknown_terms=unknown_terms,
                model_version=model_version
            )
            print(f"DEBUG: Translation object created, about to add to DB")
            
            self.db.add(translation)
            print(f"DEBUG: Added to session, about to commit")
            
            self.db.commit()
            print(f"DEBUG: Commit successful")
            
            self.db.refresh(translation)
            print(f"DEBUG: Translation saved with ID: {translation.id}")
            
            return translation.id
        
        except Exception as e:
            print(f"DEBUG: ERROR saving translation: {e}")
            self.db.rollback()
            raise
    
    def _upsert_unknown_terms(self, terms: List[str], example_text: str) -> None:
        """Insert new unknown terms or increment frequency for existing ones"""
        for term in terms:
            existing = self.db.query(models.UnknownTerm).filter(
                models.UnknownTerm.term == term
            ).first()
            
            if existing:
                existing.frequency += 1
            else:
                self.db.add(models.UnknownTerm(
                    term=term,
                    example_text=example_text[:500],  # Truncate long text
                    frequency=1,
                    status="open"
                ))
        self.db.commit()
    
    def store_feedback(
        self,
        translation_id: Optional[int],
        input_text: str,
        original_translation: str,
        corrected_translation: str,
        notes: Optional[str] = None
    ) -> int:
        """Store user feedback"""
        feedback = models.Feedback(
            translation_id=translation_id,
            input_text=input_text,
            original_translation=original_translation,
            corrected_translation=corrected_translation,
            notes=notes
        )
        self.db.add(feedback)
        self.db.commit()
        self.db.refresh(feedback)
        return feedback.id
    
    def get_unresolved_unknown_terms(
        self,
        status: Optional[str] = None,
        page: int = 0,
        limit: int = 20
    ) -> Tuple[List[models.UnknownTerm], int]:
        """Get paginated unknown terms, ordered by frequency desc"""
        query = self.db.query(models.UnknownTerm)
        
        if status:
            query = query.filter(models.UnknownTerm.status == status)
        else:
            # Default to open and reviewing terms
            query = query.filter(
                (models.UnknownTerm.status == "open") | 
                (models.UnknownTerm.status == "reviewing")
            )
        
        # Order by frequency descending (most frequent first)
        query = query.order_by(models.UnknownTerm.frequency.desc())
        
        total = query.count()
        items = query.offset(page * limit).limit(limit).all()
        
        return items, total
    
    def resolve_unknown_term(self, term_id: int, proposed_meaning: str) -> bool:
        """Mark unknown term as resolved with proposed meaning"""
        term = self.db.query(models.UnknownTerm).filter(
            models.UnknownTerm.id == term_id
        ).first()
        
        if not term:
            return False
        
        term.proposed_meaning = proposed_meaning
        term.status = "resolved"
        term.resolved_at = datetime.now()
        term.resolved_by = "system"  # Or set this to the actual user who resolved it
        self.db.commit()
        return True

    def ignore_unknown_term(self, term_id: int) -> bool:
        """Mark unknown term as ignored."""
        term = self.db.query(models.UnknownTerm).filter(
            models.UnknownTerm.id == term_id
        ).first()

        if not term:
            return False

        term.status = "ignored"
        self.db.commit()
        return True
    
    def get_stats(self) -> dict:
        """Get aggregated statistics from all tables"""
        from sqlalchemy import func
        
        print("DEBUG: get_stats called")
        
        total_translations = self.db.query(func.count(models.Translation.id)).scalar() or 0
        print(f"DEBUG: total_translations = {total_translations}")
        
        total_feedback = self.db.query(func.count(models.Feedback.id)).scalar() or 0
        open_unknowns = self.db.query(func.count(models.UnknownTerm.id)).filter(
            models.UnknownTerm.status == "open"
        ).scalar() or 0
        reviewing_unknowns = self.db.query(func.count(models.UnknownTerm.id)).filter(
            models.UnknownTerm.status == "reviewing"
        ).scalar() or 0
        resolved_unknowns = self.db.query(func.count(models.UnknownTerm.id)).filter(
            models.UnknownTerm.status == "resolved"
        ).scalar() or 0
        
        result = {
            "total_translations": total_translations,
            "total_feedback_items": total_feedback,
            "open_unknown_terms": open_unknowns,
            "reviewing_unknown_terms": reviewing_unknowns,
            "resolved_unknown_terms": resolved_unknowns,
            "total_unknown_terms": open_unknowns + reviewing_unknowns + resolved_unknowns
        }
        
        print(f"DEBUG: stats result = {result}")
        return result
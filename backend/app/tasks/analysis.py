from app.tasks.worker import celery_app


@celery_app.task(bind=True)
def analyze_email_task(self, evidence_id: str, case_id: str):
    """Placeholder analysis pipeline task.

    Will be expanded through ingestion → parser → forensics → intelligence
    → ML → risk → graph → correlation → ledger → report.
    """
    self.update_state(
        state="PROGRESS",
        meta={"stage": "INGESTED", "message": "Analysis queued"},
    )
    return {
        "evidence_id": evidence_id,
        "case_id": case_id,
        "status": "completed",
        "stage": "INGESTED",
    }

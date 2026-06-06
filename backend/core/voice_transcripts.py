import uuid
from datetime import datetime
from typing import Dict
from typing import List

from core.runtime_store import load_document
from core.runtime_store import save_document


VOICE_TRANSCRIPT_DOCUMENT = "voice_transcripts"
MAX_VOICE_TURNS = 2000


def load_voice_transcripts(
    limit: int = 100
) -> List[Dict]:
    turns = load_document(
        VOICE_TRANSCRIPT_DOCUMENT,
        []
    )
    if not isinstance(
        turns,
        list
    ):
        return []
    return turns[
        -max(
            1,
            min(
                int(
                    limit
                ),
                500
            )
        ):
    ]


def save_voice_turn(
    role: str,
    text: str,
    session_id: str = ""
) -> Dict:
    turns = load_document(
        VOICE_TRANSCRIPT_DOCUMENT,
        []
    )
    if not isinstance(
        turns,
        list
    ):
        turns = []
    turn = {
        "id": str(
            uuid.uuid4()
        ),
        "session_id": str(
            session_id
        )[:120],
        "role": str(
            role
        )[:40],
        "text": str(
            text
        )[:12000],
        "timestamp": datetime.now().isoformat(
            timespec="seconds"
        )
    }
    turns.append(
        turn
    )
    save_document(
        VOICE_TRANSCRIPT_DOCUMENT,
        turns[-MAX_VOICE_TURNS:]
    )
    return turn

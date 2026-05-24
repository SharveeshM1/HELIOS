from datetime import datetime
import uuid
from typing import Dict
from typing import List
from typing import Optional

# =========================================
# HELIOS AGENT BUS
# =========================================

class AgentBus:

    def __init__(

        self,

        max_memory: int = 500

    ):

        self.shared_memory: List[Dict] = []

        self.max_memory = max_memory

    # =====================================
    # INTERNAL MEMORY LIMITER
    # =====================================

    def _trim_memory(self):

        if len(self.shared_memory) > self.max_memory:

            overflow = (
                len(self.shared_memory)
                - self.max_memory
            )

            self.shared_memory = (
                self.shared_memory[overflow:]
            )

    # =====================================
    # SEND MESSAGE
    # =====================================

    def send_message(

        self,
        sender: str,
        receiver: str,
        content: str,
        metadata: Optional[Dict] = None

    ) -> Dict:

        message = {

            "id":
            str(uuid.uuid4()),

            "sender":
            str(sender),

            "receiver":
            str(receiver),

            "content":
            str(content),

            "timestamp":
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),

            "status":
            "delivered",

            "metadata":
            metadata or {}
        }

        self.shared_memory.append(
            message
        )

        # =================================
        # MEMORY MANAGEMENT
        # =================================

        self._trim_memory()

        return message

    # =====================================
    # GET ALL MESSAGES
    # =====================================

    def get_messages(

        self,

        limit: Optional[int] = None

    ) -> List[Dict]:

        if limit is None:

            return self.shared_memory

        return self.shared_memory[-limit:]

    # =====================================
    # FILTER BY AGENT
    # =====================================

    def get_agent_messages(

        self,
        agent_name: str,
        limit: Optional[int] = None

    ) -> List[Dict]:

        filtered = []

        for msg in self.shared_memory:

            if (

                msg["sender"] == agent_name
                or
                msg["receiver"] == agent_name

            ):

                filtered.append(msg)

        if limit is not None:

            return filtered[-limit:]

        return filtered

    # =====================================
    # GET CONVERSATION PAIR
    # =====================================

    def get_conversation(

        self,
        sender: str,
        receiver: str

    ) -> List[Dict]:

        results = []

        for msg in self.shared_memory:

            if (

                (
                    msg["sender"] == sender
                    and
                    msg["receiver"] == receiver
                )

                or

                (
                    msg["sender"] == receiver
                    and
                    msg["receiver"] == sender
                )

            ):

                results.append(msg)

        return results

    # =====================================
    # GET LATEST MESSAGE
    # =====================================

    def latest_message(self):

        if not self.shared_memory:

            return None

        return self.shared_memory[-1]

    # =====================================
    # CLEAR MEMORY
    # =====================================

    def clear(self):

        self.shared_memory = []

    # =====================================
    # BUS STATS
    # =====================================

    def get_stats(self) -> Dict:

        unique_agents = set()

        for msg in self.shared_memory:

            unique_agents.add(
                msg["sender"]
            )

            unique_agents.add(
                msg["receiver"]
            )

        return {

            "messages":
            len(self.shared_memory),

            "active":
            True,

            "agents":
            len(unique_agents),

            "memory_limit":
            self.max_memory
        }

    # =====================================
    # EXPORT MEMORY
    # =====================================

    def export_memory(self):

        return {

            "messages":
            self.shared_memory,

            "stats":
            self.get_stats()
        }

# =========================================
# GLOBAL SHARED BUS
# =========================================

shared_bus = AgentBus()
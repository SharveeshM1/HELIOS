from datetime import datetime

activity_log = []

# =========================================
# STORE ACTIVITY
# =========================================

def store_activity(

    agent,
    action=None,
    tool=None,
    objective=None,
    result=None

):

    chosen_action = action or tool or objective

    activity_log.append({

        "timestamp":
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),

        "agent":
        agent,

        "action":
        chosen_action,

        "result":
        str(result)
    })

# =========================================
# GET ACTIVITIES
# =========================================

def get_recent_activities(

    limit=5

):

    return activity_log[-limit:]
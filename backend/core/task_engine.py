import uuid
import time
import threading

from datetime import datetime

from core.shared_bus import (
    shared_bus
)

# =====================================
# TASK STATES
# =====================================

TASK_PENDING = "pending"

TASK_RUNNING = "running"

TASK_COMPLETED = "completed"

TASK_FAILED = "failed"

# =====================================
# TASK LOCK
# =====================================

task_lock = threading.Lock()

# =====================================
# TASK REGISTRY
# =====================================

ACTIVE_TASKS = []

# =====================================
# SAFE TELEMETRY
# =====================================

def send_task_telemetry(

    sender,
    content

):

    try:

        with task_lock:

            shared_bus.send_message(

                sender,

                "Task Engine",

                content
            )

    except Exception:

        pass

# =====================================
# CREATE TASK
# =====================================

def create_task(

    title,
    description,
    agent,
    priority="normal"

):

    task = {

        "id":
        str(uuid.uuid4()),

        "title":
        str(title).strip(),

        "description":
        str(description).strip(),

        "agent":
        str(agent).strip(),

        "priority":
        priority,

        "status":
        TASK_PENDING,

        "progress":
        0,

        "logs":
        [],

        "metrics":{

            "execution_time":0,

            "cpu_load":"stable",

            "memory_state":"healthy"
        },

        "created_at":
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),

        "started_at":
        None,

        "completed_at":
        None
    }

    ACTIVE_TASKS.append(task)

    add_task_log(

        task,

        "Task initialized."
    )

    send_task_telemetry(

        "Task Engine",

        f"""

Task created.

Title:
{task['title']}

Agent:
{task['agent']}

Priority:
{task['priority']}

        """
    )

    return task

# =====================================
# ADD TASK LOG
# =====================================

def add_task_log(

    task,
    message

):

    task["logs"].append({

        "timestamp":
        datetime.now().strftime(
            "%H:%M:%S"
        ),

        "message":
        str(message)
    })

# =====================================
# UPDATE PROGRESS
# =====================================

def update_progress(

    task,
    progress,
    log_message=None

):

    task["progress"] = max(
        0,
        min(100, progress)
    )

    if log_message:

        add_task_log(

            task,

            log_message
        )

# =====================================
# EXECUTE TASK
# =====================================

def execute_task(

    task,
    execution_callback=None

):

    started = time.time()

    try:

        # =================================
        # START
        # =================================

        task["status"] = TASK_RUNNING

        task["started_at"] = (

            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )

        send_task_telemetry(

            task["agent"],

            f"""

Task execution started.

Task:
{task['title']}

Task ID:
{task['id']}

            """
        )

        # =================================
        # PHASE 1
        # =================================

        update_progress(

            task,

            10,

            "Initializing execution engine..."
        )

        time.sleep(0.25)

        # =================================
        # PHASE 2
        # =================================

        update_progress(

            task,

            25,

            "Loading cognition systems..."
        )

        time.sleep(0.25)

        # =================================
        # PHASE 3
        # =================================

        update_progress(

            task,

            45,

            f"Routing workflow to {task['agent']}..."
        )

        time.sleep(0.35)

        # =================================
        # CALLBACK EXECUTION
        # =================================

        callback_output = None

        if execution_callback:

            try:

                callback_output = execution_callback()

                task["result"] = (
                    callback_output
                )

                add_task_log(

                    task,

                    "Execution callback completed."
                )

            except Exception as e:

                task["result"] = str(e)

                raise Exception(

                    f"Callback failed: {str(e)}"
                )

        # =================================
        # PHASE 4
        # =================================

        update_progress(

            task,

            75,

            "Executing autonomous workflow..."
        )

        time.sleep(0.35)

        # =================================
        # PHASE 5
        # =================================

        update_progress(

            task,

            92,

            "Finalizing orchestration pipeline..."
        )

        time.sleep(0.25)

        # =================================
        # COMPLETE
        # =================================

        task["progress"] = 100

        task["status"] = TASK_COMPLETED

        task["completed_at"] = (

            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )

        execution_time = round(

            time.time() - started,

            2
        )

        task["metrics"][
            "execution_time"
        ] = execution_time

        add_task_log(

            task,

            "Task execution completed."
        )

        send_task_telemetry(

            task["agent"],

            f"""

Task execution stabilized.

Task:
{task['title']}

Execution Time:
{execution_time}s

Status:
completed

            """
        )

    except Exception as e:

        task["status"] = TASK_FAILED

        task["completed_at"] = (

            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )

        add_task_log(

            task,

            f"Execution failure: {str(e)}"
        )

        send_task_telemetry(

            task["agent"],

            f"""

Task execution failed.

Task:
{task['title']}

Error:
{str(e)}

            """
        )

    return task

# =====================================
# GET TASK
# =====================================

def get_task(

    task_id

):

    for task in ACTIVE_TASKS:

        if task["id"] == task_id:

            return task

    return None

# =====================================
# GET ALL TASKS
# =====================================

def get_all_tasks():

    return ACTIVE_TASKS

# =====================================
# CLEAR TASKS
# =====================================

def clear_tasks():

    ACTIVE_TASKS.clear()

# =====================================
# TASK SUMMARY
# =====================================

def summarize_task(

    task

):

    return {

        "id":
        task["id"],

        "title":
        task["title"],

        "agent":
        task["agent"],

        "priority":
        task["priority"],

        "status":
        task["status"],

        "progress":
        task["progress"],

        "execution_time":
        task["metrics"][
            "execution_time"
        ]
    }

# =====================================
# TASK ANALYTICS
# =====================================

def task_analytics():

    completed = len([

        t for t in ACTIVE_TASKS

        if t["status"] == TASK_COMPLETED

    ])

    failed = len([

        t for t in ACTIVE_TASKS

        if t["status"] == TASK_FAILED

    ])

    running = len([

        t for t in ACTIVE_TASKS

        if t["status"] == TASK_RUNNING

    ])

    pending = len([

        t for t in ACTIVE_TASKS

        if t["status"] == TASK_PENDING

    ])

    return {

        "total_tasks":
        len(ACTIVE_TASKS),

        "completed":
        completed,

        "failed":
        failed,

        "running":
        running,

        "pending":
        pending
    }
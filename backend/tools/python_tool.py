import traceback

# =========================================
# EXECUTE PYTHON
# =========================================

def execute_python(

    code: str

):

    local_scope = {}

    try:

        exec(

            code,

            {},

            local_scope
        )

        return {

            "success": True,

            "locals": local_scope
        }

    except Exception:

        return {

            "success": False,

            "error": traceback.format_exc()
        }
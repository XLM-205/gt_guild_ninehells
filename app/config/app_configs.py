# Main server configurations that can changed during runtime. Default values are defined as (Dft: T / F)
app_configs = {
    "PRE_INIT": [],        # Stuff to do before initialization
    "POST_INIT": [],       # Stuff to do after initialization
    "USE_LOGGER": False,   # If True, use the logger service
    "USE_HOOK": True,      # If True, use webhooks (Discord)
    "VERBOSE": False       # If True, print useful console messages
}
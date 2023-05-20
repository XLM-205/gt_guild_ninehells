# Default values used within the server. Changing them during runtime is NOT RECOMMENDED
app_defaults = {
    "SECURITY": {
        "INJ_GUARD": {
            "CASES": ["--", "\')", ");"],         # If any is found in the query, reject
            "GROUPS": [["\'", ")"], [")", ";"]],  # If found in the order, reject
            "REPLACES": [["\'", "´"], ]           # If [0] is found, replace to [1]
        },
        "LOGIN": {
            "MAX_TRIES": 5,  # Maximum amount of wrong guesses before locking the login
            "LOCKOUT": 3600
        }
    },
    "FALLBACK": {
        "PORT": 5000,      # Default port
        "DB_URL": None
    },   # Default Database URL
    "REQUEST": {
        "TIMEOUT": 3  # Time, in seconds, before a GET request is ignored
    },
    "LOGGER": {
        "PROVIDER": "https://rdm-gen-logserver.herokuapp.com/",  # Logger url
        "REQUIRE_LOGIN": True
    },                                  # The logger require a valid login?
    "INTERNAL": {
        "VERSION": "0.9.3",  # Server's Version
        "ACCESS_POINT": "http://gt-ninehells-guild.herokuapp.com/",  # Website's url
        "WEB_NAME": "GT Guild Webpage"  # Website's name internally and on entries
    }
}

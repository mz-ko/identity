# Email Settings
EMAIL_CONSOLE_DOMAIN = ""
EMAIL_SERVICE_NAME = "Cloudforet"

# Enums: ACCESS_TOKEN (default) | PASSWORD
RESET_PASSWORD_TYPE = "ACCESS_TOKEN"

# Database Settings
DATABASE_AUTO_CREATE_INDEX = True
DATABASES = {
    "default": {
        # 'db': '',
        # 'host': '',
        # 'port': 0,
        # 'username': '',
        # 'password': '',
        # 'ssl': False,
        # 'ssl_ca_certs': ''
    }
}

# Cache Settings
CACHES = {
    "default": {},
    "local": {
        "backend": "spaceone.core.cache.local_cache.LocalCache",
        "max_size": 128,
        "ttl": 300,
    },
}

# Identity Settings
IDENTITY = {
    "token": {
        "verify_code_timeout": 3600,  # 1hour
        "temporary_token_timeout": 86400,  # 24 hours
        "invite_token_timeout": 604800,  # 7 days
        "token_timeout": 1800,  # 30 minutes
        "token_max_timeout": 604800,  # 7 days
        "refresh_timeout": 10800,  # 3 hours
    },
    "mfa": {"verify_code_timeout": 300},
}

# Handler Settings
HANDLERS = {
    # "authentication": [{
    #     "backend": "spaceone.core.handler.authentication_handler:SpaceONEAuthenticationHandler"
    # }],
    # "authorization": [{
    #     "backend": "spaceone.core.handler.authorization_handler:SpaceONEAuthorizationHandler"
    # }],
    # "mutation": [{
    #     "backend": "spaceone.core.handler.mutation_handler:SpaceONEMutationHandler"
    # }],
    # "event": []
}

# Log Settings
LOG = {
    "filters": {
        "masking": {
            "rules": {
                "Domain.create": ["admin"],
                "UserProfile.update": ["password"],
                "User.create": ["password"],
                "User.update": ["password"],
                "WorkspaceUser.create": ["password"],
                "Token.issue": ["credentials"],
                "Token.grant": ["token"],
            }
        }
    }
}

# Connector Settings
CONNECTORS = {
    "SpaceConnector": {
        "backend": "spaceone.core.connector.space_connector:SpaceConnector",
        "endpoints": {
            "identity": "grpc://localhost:50051",
            "plugin": "grpc://plugin:50051",
            "secret": "grpc://secret:50051",
            "repository": "grpc://repository:50051",
        },
    },
    "SMTPConnector": {
        # "host": "smtp.mail.com",
        # "port": "1234",
        # "user": "cloudforet",
        # "password": "1234",
        # "from_email": "support@cloudforet.com",
    },
}

# Endpoint Settings
ENDPOINTS = [
    # {
    #     "service": "identity",
    #     "name": "Identity Service",
    #     "endpoint": "grpc://<endpoint>>:<port>"
    # },
    # {
    #     "service": "inventory",
    #     "name": "Inventory Service",
    #     "endpoint": "grpc+ssl://<endpoint>>:<port>"
    # }
]

# System Token Settings
TOKEN = ""

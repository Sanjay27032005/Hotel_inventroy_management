from app.core.database import Base  # noqa: F401

# Import every model module so they register on Base.metadata
from app.models import core  # noqa: F401,E402
from app.models import customer  # noqa: F401,E402
from app.models import location  # noqa: F401,E402
from app.models import accommodation  # noqa: F401,E402
from app.models import restaurant  # noqa: F401,E402
from app.models import events  # noqa: F401,E402
from app.models import pool  # noqa: F401,E402
from app.models import spa  # noqa: F401,E402
from app.models import club  # noqa: F401,E402
from app.models import laundry  # noqa: F401,E402
from app.models import booking_billing  # noqa: F401,E402
from app.models import content  # noqa: F401,E402

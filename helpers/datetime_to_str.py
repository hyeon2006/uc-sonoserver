from datetime import datetime, timezone, timedelta

def datetime_to_str(datetime_: datetime) -> str:
    delta = datetime.now(timezone.utc) - datetime_

    if delta >= timedelta(days=1):
        return f"{delta.days}d"
    elif delta >= timedelta(hours=1):
        return f"{delta.seconds // 3600}h"
    elif delta >= timedelta(minutes=1):
        return f"{delta.seconds // 60}m"
    elif delta >= timedelta(seconds=1):
        return f"{delta.seconds}s"
    
    return "0s"
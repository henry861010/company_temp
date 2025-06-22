import resource

def evaluate_memory(s: str = ""):
    usage = resource.getrusage(resource.RUSAGE_SELF)
    max_rss_kb = usage.ru_maxrss  # On macOS & Linux (Python ≥3.9), this is in KB
    max_rss_mb = max_rss_kb / 1024 / 1024
    max_rss_gb = max_rss_mb / 1024
    if max_rss_gb >= 1:
        print(f"Max memory usage: {max_rss_gb:.2f} GB")
    else:
        print(f"Max memory usage: {max_rss_mb:.2f} MB")
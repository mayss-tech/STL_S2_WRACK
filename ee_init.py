import ee

def init_gee():
    try:
        ee.Initialize()
        return True
    except Exception:
        ee.Authenticate()
        ee.Initialize()
        return True
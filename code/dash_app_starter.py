app = None
kwargs = None
def s(app, kwargs):
    global app
    global kwargs
    app = app
    kwargs = kwargs
    return None
    
app.run(**kwargs)
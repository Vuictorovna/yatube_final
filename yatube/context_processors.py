import datetime as dt


def year(request):
    y = dt.datetime.now()
    return {"year": y.year}

from app import db
from app.models import Urls
from datetime import datetime, timedelta, date

all_urls = [i for i in Urls.query.all()]

ids_to_delete = []
for i in all_urls:
    add_date = datetime.strptime(i.add_date, '%d/%m/%Y')
    add_date_after_30 = str(add_date + timedelta(days=30))[0: -9]
    today = str(datetime.today())[0: -16]

    if add_date_after_30 == today:
        ids_to_delete.append(i.url_id)

if ids_to_delete:
    for i in ids_to_delete:
        Urls.query.filter_by(id=i).delete()

    db.session.commit()

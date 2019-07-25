from city import City
from dbhelper import Database
from config import MongoDB

if __name__ == '__main__':
    db = Database(MongoDB)
    beijing = City('南宁', searchDB=db)
    beijing.get()
    results = beijing.search(keyword='朝阳广场地铁站', category='美食', save=True, details=False)

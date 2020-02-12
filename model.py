'''
Константы и модель данных
'''
from sqlalchemy import Column, Integer, String, create_engine, DATE, Text, ForeignKey, Table
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
import csv
import datetime as dt


VOTING_ID = 1   # Выборы Мэра Москвы, 09.09.2018
DB_FILE_NAME = 'uik_db.sqlite'   # 'db.sqlite'

PATH_BD = 'sqlite:///uik_db.sqlite'
DESC_FILE_NAME = 'Description.csv'
CITY = 'Москва'
UII = 'Университет искуственного интеллекта'
UII_URL = 'https://neural-university.ru/'
EMAIL = 'vladimir.tryastsyn@gmail.com'
FIO = 'Трясцын Владимир'
DATA_CREATION = '12.02.2020'

FILE_NAME_REGION = "regions.json"
FILE_NAME_UIK = "uiks.json"
DELIMITER = '|'
URL_MSK = 'http://www.moscow_city.vybory.izbirkom.ru/region/region/moscow_city?action=show&root=1&tvd=27720002197406&vrn=27720002197402&region=77&global=&sub_region=77&prver=0&pronetvd=null&vibid=27720002197406&type=234'
DATE_VOTING = '2020-09-09'


Base = declarative_base()


class City(Base):
    __tablename__ = 'city'
    id = Column(Integer, primary_key=True)
    name = Column(String, index=True, unique=True, nullable=False)
    voting = relationship('Voting', backref='city')

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f'{self.id}| {self.name}'


class Voting(Base):
    __tablename__ = 'voting'
    id = Column(Integer, primary_key=True)
    name = Column(String, index=True, unique=True, nullable=False)
    date_voting = Column(DATE, nullable=False)
    url_result = Column(Text)
    city_id = Column(Integer, ForeignKey('city.id'), nullable=False)
    areas = relationship('Areas', backref='areas')

    def __init__(self, name, date_voting, url_result, city_id):
        self.name = name
        self.date_voting = date_voting
        self.url_result = url_result
        self.city_id = city_id

    def __str__(self):
        return f'{self.id}| {self.name}: {self.date_voting}'


class Areas(Base):
    __tablename__ = 'areas'
    id = Column(Integer, primary_key=True)
    name = Column(String, index=True, unique=True, nullable=False)
    number = Column(Integer, index=True, nullable=False)
    url = Column(Text)
    voting_id = Column(Integer, ForeignKey('voting.id'), nullable=False)
    # uiks = relationship('Uiks', backref='uiks')

    def __init__(self, name, number, url, voting_id):
        self.name = name
        self.number = number
        self.url = url
        self.voting_id = voting_id

    def __str__(self):
        return f'{self.id}| {self.name}: {self.number}'


class Uiks(Base):
    __tablename__ = 'uiks'
    id = Column(Integer, primary_key=True)
    name = Column(String, index=True, unique=True, nullable=False)
    number = Column(Integer, index=True, nullable=False)
    url = Column(Text)
    area_id = Column(Integer, ForeignKey('areas.id'), nullable=False)
    result = relationship('Result', backref='result')

    def __init__(self, name, number, url, area_id):
        self.name = name
        self.number = number
        self.url = url
        self.area_id = area_id

    def __str__(self):
        return f'{self.id}| {self.name}: {self.number}'


class DescriptionFields(Base):
    __tablename__ = 'description_fields'
    id = Column(Integer, primary_key=True, nullable=False)
    row_number = Column(String, index=True, nullable=False)
    row_description = Column(String)
    # result = relationship('Result', backref='result')

    def __init__(self, row_number, row_description):
        self.row_number = row_number
        self.row_description = row_description

    def __str__(self):
        return f'{self.id}| {self.row_number}: {self.row_description}'


class Result(Base):
    __tablename__ = 'result'
    id = Column(Integer, primary_key=True, nullable=False)
    uik_id = Column(Integer, ForeignKey('uiks.id'), index=True, nullable=False)
    desc_id = Column(Integer, ForeignKey('description_fields.id'), index=True, nullable=False)
    value = Column(Integer, nullable=False)

    def __init__(self, uik_id, desc_id, value):
        self.uik_id = uik_id
        self.desc_id = desc_id
        self.value = value

    def __str__(self):
        return f'{self.id}| {self.uik_id}: {self.desc_id}'


def CreateAndInitDB(base, path):
    engine = create_engine(path, echo=True)
    # Создание таблиц
    base.metadata.create_all(engine)
    # Заполнение таблиц
    # Создание сессии
    # create a configured "Session" class
    Session = sessionmaker(bind=engine)

    # create a Session
    session = Session()
    # Таблица city
    city = City('Москва')
    session.add(city)
    city = City('Санкт-Петурбург')
    session.add(city)
    # Таблица voting
    voting = Voting(u'Выборы Мэра Москвы', dt.date.fromisoformat(DATE_VOTING), u'http://www.moscow_city.vybory.izbirkom.ru/region/region/moscow_city?action=show&root=1&tvd=27720002197406&vrn=27720002197402&region=77&global=&sub_region=77&prver=0&pronetvd=null&vibid=27720002197406&type=234', 1)
    session.add(voting)
    session.commit()
    # Таблица description_fields
    with open(DESC_FILE_NAME, "r") as f:
        reader = csv.reader(f, delimiter='|')
        for ind, row in enumerate(reader):
            if ind > 0:
                desc = DescriptionFields(row[0], row[1])
                session.add(desc)
        session.commit()
    session.close()


if __name__ == "__main__":
    CreateAndInitDB(Base, PATH_BD)








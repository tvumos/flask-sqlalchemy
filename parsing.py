import requests
from model import Areas, Uiks, Voting, City, DescriptionFields, Result
import model
from bs4 import BeautifulSoup
from lxml import html
import pprint
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker


def get_result(url):
    # Запрос страницы выборов
    response = requests.get(url)
    # Создаем soup для разбора html
    #soup = BeautifulSoup(response.text, 'html.parser')
    # Получаем страницу для выполнения запросов XPath
    page_body = html.fromstring(response.text, parser=html.HTMLParser(encoding='utf-8'))
    # Получаем расшифровку строк
    result = []
    for i in range(1, 18):
        numb = page_body.xpath(f'//html/body/table[3]/tr[4]/td/table[5]/tr[{i}]/td[1]/text()')
        desk = page_body.xpath(f'//html/body/table[3]/tr[4]/td/table[5]/tr[{i}]/td[2]/text()')
        val = page_body.xpath(f'//html/body/table[3]/tr[4]/td/table[5]/tr[{i}]/td[3]/b/text()')
        if len(numb) == 1:
            row = [str(numb[0]), str(desk[0]), str(val[0])]
            result.append(row)
    return result


def save_result_uik_alchemy(uik_key, result_list):
    engine = create_engine(model.PATH_BD, echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        for row in result_list:
            desc = session.query(DescriptionFields.id).filter(DescriptionFields.row_number == row[0]).all()
            if desc[0][0] > 0:
                result = Result(uik_key, desc[0][0], row[2])
                session.add(result)
        session.commit()
    except Exception as err:
        print('ERROR Save result: ', err)
        session.rollback()
        return False
    finally:
        session.close()
    return True


def extract_result_from_base_alchemy(uik_key):
    engine = create_engine(model.PATH_BD, echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        result = session.query(DescriptionFields.row_number, DescriptionFields.row_description, Result.value).\
            join(Result, DescriptionFields.id == Result.desc_id).filter(Result.uik_id == uik_key)\
            .order_by(DescriptionFields.id).all()
        session.commit()
    except Exception as err:
        print('ERROR return list Region and UIK', err)
        session.rollback()
        return
    finally:
        session.close()
    return result


def exists_result_uik_alchemy(uik_key):
    result = False
    engine = create_engine(model.PATH_BD, echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        # Проверяем в таблице Результатов Result
        col = session.query(func.count(Result.id)).filter(Result.uik_id == uik_key).all()
        print('col[0][0] = ', col[0][0])
        if col[0][0] > 0:
            result = True
        session.commit()
    except Exception as err:
        print('ERROR return list Region and UIK', err)
        session.rollback()
        return
    finally:
        session.close()
    return result


def get_name_region_and_uik_alchemy(region_key, uik_key):
    engine = create_engine(model.PATH_BD, echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    result = []
    try:
        region_name = session.query(Areas.name).filter(Areas.id == region_key).all()
        uik_name = session.query(Uiks.name).filter(Uiks.id == uik_key).all()
        result.append(region_name[0])
        result.append(uik_name[0])
        # print('get_name_region_and_uik_alchemy')
        # print('region_name = ', region_name)
        # print('uik_name = ', uik_name)
        # print('result = ', result)
        session.commit()
    except Exception as err:
        print('ERROR return list Region and UIK', err)
        session.rollback()
        return
    finally:
        session.close()
    return result


def get_url_uik_alchemy(uik_id):
    engine = create_engine(model.PATH_BD, echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        # print('get_url_uik_alchemy')
        url_row = session.query(Uiks.url).filter(Uiks.id == uik_id).all()
        # print('url_row = ', url_row)
        session.commit()
    except Exception as err:
        print('ERROR return list UIKS', err)
        session.rollback()
        return
    finally:
        session.close()
    return url_row


def get_uik_rows_alchemy(region_key):
    """
    Возвращает список из кортежей:
    [(8888, 'УИК №3647'),
    (8874, 'УИК №375'),
    (8875, 'УИК №376'), ......]
    :return:
    """
    engine = create_engine(model.PATH_BD, echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        # print('get_uik_rows_alchemy')
        uiks = session.query(Uiks.id, Uiks.name).filter(Uiks.area_id == region_key).all()
        # print('uiks = ', uiks)
        session.commit()
    except Exception as err:
        print('ERROR return list UIKS', err)
        session.rollback()
        return None
    finally:
        session.close()
    return uiks


def get_regions_alchemy():
    """
    Возвращает список из кортежей:
    [(621, 'Академический район'),
    (574, 'Алексеевский район'),
    (575, 'Алтуфьевский район'),
    (576, 'Бабушкинский район'),......]
    :return:
    """
    engine = create_engine(model.PATH_BD, echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        # print('get_regions_alchemy')
        regions = session.query(Areas.id, Areas.name).filter(Areas.voting_id == model.VOTING_ID).all()
        # for area in q:
        #     print(area)
        # print('regions = ', regions)
        session.commit()
    except Exception as err:
        print('ERROR return list Regions', err)
        session.rollback()
        return None
    finally:
        session.close()
    return regions


def check_regions_db_alchemy():
    engine = create_engine(model.PATH_BD, echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        q = session.query(func.count(Areas.id)).join(Voting, Areas.voting_id == Voting.id).\
            filter(Voting.id == model.VOTING_ID).all()

        if q[0][0] == 0:  # Необходимо загрузить в базу список Регионов
            response = requests.get(model.URL_MSK)
            # Создаем soup для разбора html
            soup = BeautifulSoup(response.text, 'html.parser')

            regions_tag = soup.find_all('option')
            for region in regions_tag:  # [:11] ОТЛАДКА Удалить ограничение регионов
                region_name = region.text
                region_ind = region_name.split()[0]
                region_name = region_name.replace(str(region_ind), '', 1).strip()
                url_region = region.get('value')
                if len(region_name) > 0:
                    area = Areas(region_name, region_ind, url_region, model.VOTING_ID)
                    session.add(area)
                    session.flush()

                    response_region = requests.get(url_region)
                    region_soup = BeautifulSoup(response_region.text, 'html.parser')
                    uiks_tag = region_soup.find_all('option')
                    for uik_tag in uiks_tag:
                        uik_name = uik_tag.text
                        uik_ind = uik_name.split()[0]
                        uik_name = uik_name.replace(str(uik_ind), '', 1).strip()
                        url_uik = uik_tag.get('value')
                        if len(uik_name) > 0:
                            uik = Uiks(uik_name, uik_ind, url_uik, area.id)
                            session.add(uik)
                            session.flush()
                    session.commit()
    except Exception as err:
        print('Connect to database ERROR', err)
        session.rollback()
        return False
    finally:
        session.close()
    return True


if __name__ == "__main__":
    # engine = create_engine(model.PATH_BD, echo=True)
    # Session = sessionmaker(bind=engine)
    # session = Session()
    #
    # area = Areas('test1', '2', 'url', 1)
    # session.add(area)
    # session.flush()
    # print(area.id)
    # session.commit()
    # session.close()
    # check_connect_db()
    # print(get_regions_alchemy())
    result = extract_result_from_base_alchemy(323)
    pprint.pprint(result)



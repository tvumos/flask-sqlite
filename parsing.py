import requests
import model
from bs4 import BeautifulSoup
from lxml import html
import pprint
import sqlite3


def get_result(url):
    # Запрос страницы выборов
    response = requests.get(url)
    # Создаем soup для разбора html
    soup = BeautifulSoup(response.text, 'html.parser')
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


def save_result_uik(uik_key, result_list):
    conn = sqlite3.connect(model.DB_FILE_NAME)
    try:
        cursor = conn.cursor()
        for row in result_list:
            cursor.execute('INSERT INTO result (uik_id, desc_id, value) SELECT ?, d.id, ? '
                           'FROM description_fields d WHERE d.row_number = ?', (uik_key, row[2], row[0]))
        conn.commit()
    except Exception as err:
        print('ERROR Save result: ', err)
        return False
    finally:
        conn.close()
    return True


def extract_result_from_base(uik_key):
    conn = sqlite3.connect(model.DB_FILE_NAME)
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT d.row_number, d.row_description, r.value FROM result r INNER JOIN description_fields d '
                       'ON d.id = r.desc_id WHERE r.uik_id = ? ORDER BY d.id', (uik_key,))
        result = cursor.fetchall()
    except Exception as err:
        print('ERROR return list Region and UIK', err)
        return
    finally:
        conn.close()
    return result


def exists_result_uik(uik_key):
    result = False
    conn = sqlite3.connect(model.DB_FILE_NAME)
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT count(*) FROM result WHERE uik_id = ?', (uik_key,))
        col = cursor.fetchall()
        if col[0][0] > 0:
            result = True
    except Exception as err:
        print('ERROR return list Region and UIK', err)
        return
    finally:
        conn.close()
    return result


def get_name_region_and_uik(region_key, uik_key):
    conn = sqlite3.connect(model.DB_FILE_NAME)
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT a.name, u.name FROM areas a INNER JOIN uiks u ON a.id = u.area_id '
                       'WHERE a.id = ? AND u.id = ?', (region_key, uik_key))
        result = cursor.fetchall()
    except Exception as err:
        print('ERROR return list Region and UIK', err)
        return
    finally:
        conn.close()
    return result


def get_url_uik(uik_id):
    conn = sqlite3.connect(model.DB_FILE_NAME)
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT u.url FROM uiks u WHERE u.id = ?', (uik_id, ))
        url_row = cursor.fetchall()
        # pprint.pprint(url)
    except Exception as err:
        print('ERROR return list UIKS', err)
        return
    finally:
        conn.close()
    return url_row


def get_uik_rows(region_key):
    """
    Возвращает список из кортежей:
    [(8888, 'УИК №3647'),
    (8874, 'УИК №375'),
    (8875, 'УИК №376'), ......]
    :return:
    """
    conn = sqlite3.connect(model.DB_FILE_NAME)
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT u.id, u.name FROM uiks u INNER JOIN areas a ON u.area_id = a.id AND '
                       'a.voting_id = ? AND u.area_id = ? ORDER BY u.name   ', (str(model.VOTING_ID), str(region_key)))
        items = cursor.fetchall()
    except Exception as err:
        print('ERROR return list UIKS', err)
        return None
    finally:
        conn.close()
    return items


def get_regions():
    """
    Возвращает список из кортежей:
    [(621, 'Академический район'),
    (574, 'Алексеевский район'),
    (575, 'Алтуфьевский район'),
    (576, 'Бабушкинский район'),......]
    :return:
    """
    conn = sqlite3.connect(model.DB_FILE_NAME)
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT id, name FROM areas WHERE voting_id = ? ORDER BY name', str(model.VOTING_ID))
        items = cursor.fetchall()
    except Exception as err:
        print('ERROR return list Regions', err)
        return None
    finally:
        conn.close()
    return items


def check_connect_db():
    conn = sqlite3.connect(model.DB_FILE_NAME)
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT count(a.id) as col_row FROM areas a INNER JOIN voting v '
                       'ON a.voting_id = v.id AND v.id = ?', str(model.VOTING_ID))
        count_row = cursor.fetchall()
        if count_row[0][0] == 0:        # Необходимо загрузить в базу список Регионов
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
                    cursor.execute('INSERT INTO areas (name, number, url, voting_id) VALUES (?, ?, ?, ?);',
                                   (region_name, region_ind, url_region, model.VOTING_ID))

                    response_region = requests.get(url_region)
                    region_soup = BeautifulSoup(response_region.text, 'html.parser')
                    uiks_tag = region_soup.find_all('option')
                    for uik_tag in uiks_tag:
                        uik_name = uik_tag.text
                        uik_ind = uik_name.split()[0]
                        uik_name = uik_name.replace(str(uik_ind), '', 1).strip()
                        url_uik = uik_tag.get('value')
                        if len(uik_name) > 0:
                            cursor.execute("INSERT INTO uiks (name, number, url, area_id) SELECT ?, ?, ?, a.id "
                                           "FROM areas a WHERE a.voting_id = ? AND a.number = ?",
                                           (uik_name, uik_ind, url_uik, model.VOTING_ID, region_ind))
            conn.commit()
    except Exception as err:
        print('Connect to database ERROR', err)
        return False
    finally:
        conn.close()
    return True


if __name__ == "__main__":

    check_connect_db()


from flask import Flask, render_template, request
import model
from parsing import get_result, check_regions_db_alchemy, get_uik_rows_alchemy, get_regions_alchemy, \
    get_url_uik_alchemy, get_name_region_and_uik_alchemy, exists_result_uik_alchemy, \
    save_result_uik_alchemy, extract_result_from_base_alchemy
from os import path
import json
from flask_wtf import Form
from wtforms import SelectField
import pprint


app = Flask(__name__)
app.config['SECRET_KEY'] = model.UII


class FormRegionsUiks(Form):
    regions = SelectField(u'Выберите регион: ', coerce=int)
    uiks = SelectField(u'Выберите УИК:', coerce=int)

    def __init__(self, *args, **kwargs):
        super(FormRegionsUiks, self).__init__(*args, **kwargs)

        regions_list = get_regions_alchemy()
        # region[0] - Значение поля id из таблицы areas
        # region[1] - Значение поля name из таблицы areas
        self.regions.choices = [(region[0], u"%s" % region[1]) for region in regions_list]
        #  выбранное поле по умолчанию
        self.regions.choices.insert(0, (0, u"Не выбрано"))

        self.uiks.choices = list()
        #  выбранное поле по умолчанию
        self.uiks.choices.insert(0, (0, u"Не выбрано"))


@app.route("/")
@app.route('/index')
def index():
    if not path.isfile(model.DB_FILE_NAME):  # Если файл с базой данных не существует, создаём БД
        model.CreateAndInitDB(model.Base, model.PATH_BD)
    check_regions_db_alchemy()  # И заполняем таблицы Areas и Uiks
    return render_template('index.html', url_msk=model.URL_MSK, uii=model.UII, uii_url=model.UII_URL)


@app.route('/contacts/')
def contacts():
    return render_template('contact.html', creation_date=model.DATA_CREATION,
                           fio=model.FIO, email=model.EMAIL, city=model.CITY,
                           uii=model.UII, uii_url=model.UII_URL)


@app.route('/form/')
def forms():
    form = FormRegionsUiks()
    return render_template('form.html', form=form, uii=model.UII, uii_url=model.UII_URL)


@app.route('/result/', methods=['GET', 'POST'])
def results():
    region_key = request.form['regions']
    uik_key = request.form['uiks']
    names = get_name_region_and_uik_alchemy(region_key, uik_key)
    # print('names=', names, names[0], names[1])

    if not exists_result_uik_alchemy(uik_key):  # Если = True есть записи, если False - нет записей с результатами в базе
        url = get_url_uik_alchemy(uik_key)
        """     list_result = 
        [['1', 'Число избирателей, внесенных в список', '85'],
        ['2', 'Число бюллетеней, полученных УИК', '300'],
        ['3', 'Число бюллетеней, выданных в помещении для голосования', '69'],
        ['4', 'Число  бюллетеней, выданных вне помещения для голосования', '16'], ....]
        """
        list_result = get_result(url[0][0])     # Если нет записей - парсим сайт и сохраняем результаты в базе
        save_result_uik_alchemy(uik_key, list_result)
    else:                                     # Иначе извлекаем из базы, сайт не парсим
        list_result = extract_result_from_base_alchemy(uik_key)
    return render_template('result.html', list_result=list_result, region=names[0][0], uik=names[1][0],
                           uii=model.UII, uii_url=model.UII_URL)


@app.route('/get_uik', methods=('GET', 'POST'))
def get_uiks():
    region_key = request.form['regions']
    dict_uiks = {}
    list_uik = get_uik_rows_alchemy(region_key)
    for uik in list_uik:
        dict_uiks[uik[0]] = uik[1]
    return json.dumps(dict_uiks)


if __name__ == "__main__":
    app.run(debug=True)

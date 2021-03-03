from flask import Flask, render_template, request, redirect, url_for
import plotly
import plotly.graph_objs as go
import json
import joblib
import pandas as pd



# untuk membuat route
app = Flask(__name__)


df = pd.read_csv('D:\Project\Project\earthquake\earthquake_clean.csv')

with open('database.json') as base:
    data = json.load(base)

@app.route('/', methods = ['GET', 'POST'])
def welcome():
    if request.method == 'POST':
        nam_l = request.form['log_nama']
        pwd_l = request.form['pass_nama']
        
        for a in range(len(data)):
            if nam_l == data[a]['nama'] and pwd_l == data[a]['pass']:
                return redirect(url_for('index'))
            elif a == len(data) - 1:
                return render_template('error_login.html', nama = nam_l)
            else:
                continue
    else:
        return render_template('welcome.html')

@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    if request.method == 'POST':
        nam_s = request.form['nama_signup']
        pwd_s = request.form['pass_signup']
        data.append({'nama': nam_s, 'pass': pwd_s})
        y = json.dumps(data)

        json_data = open('database.json', 'w')
        json_data.write(y)
        return redirect(url_for('index'))
    else:
        return render_template('signup.html')

# category plot function
def category_plot(
    cat_plot = 'histplot',
    cat_x = 'district_id', cat_y = 'height_ft_pre_eq',
    estimator = 'count', hue = 'damage'):

    # jika menu yang dipilih adalah histogram
    if cat_plot == 'histplot':
        # siapkan list kosong untuk menampung konfigurasi hist
        data = []
        # generate config histogram dengan mengatur sumbu x dan sumbu y
        for val in df[hue].unique():
            hist = go.Histogram(
                x=df[df[hue]==val][cat_x],
                y=df[df[hue]==val][cat_y],
                histfunc=estimator,
                name=val
            )
            #masukkan ke dalam array
            data.append(hist)
        #tentukan title dari plot yang akan ditampilkan
        title='Histogram'

    elif cat_plot == 'boxplot':
        data = []

        for val in df[hue].unique():
            box = go.Box(
                x=df[df[hue] == val][cat_x], #series
                y=df[df[hue] == val][cat_y],
                name = val
            )
            data.append(box)
        title='Box'

    if cat_plot == 'histplot':
        layout = go.Layout(
            title=title,
            xaxis=dict(title=cat_x),
            # boxmode group digunakan berfungsi untuk mengelompokkan box berdasarkan hue
            boxmode = 'group'
        )
    else:
        layout = go.Layout(
            title=title,
            xaxis=dict(title=cat_x),
            yaxis=dict(title=cat_y),
            # boxmode group digunakan berfungsi untuk mengelompokkan box berdasarkan hue
            boxmode = 'group'
        )
    #simpan config plot dan layout pada dictionary
    result = {'data': data, 'layout': layout}

    #json.dumps akan mengenerate plot dan menyimpan hasilnya pada graphjson
    graphJSON = json.dumps(result, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON


@app.route('/home')
def index():

    plot = category_plot()
    # dropdown menu
    # kita lihat pada halaman dashboard terdapat menu dropdown
    # kita mengirimnya dalam bentuk list agar mudah mengolahnya di halaman html menggunakan looping
    list_plot = [('histplot', 'Histogram'), ('boxplot', 'Box')]
    list_x = [('foundation_type', 'Foundation Type'), ('damage', 'Damage Grade'), ('roof_type', 'Roof Type'), ('land_surface_condition', 'Land Surface'), ('height_ft_pre_eq', 'Height'), ('plinth_area_sq_ft', 'Plinth Area'), ('height_ft_post_eq', 'Height Post'), ('count_floors_pre_eq', 'Count Floors'), ('count_floors_post_eq', 'Count Floors Post'), ('vdcmun_id', 'Municipality id'), ('district_id', 'District id'), ('position', 'Position'), ('other_floor_type', 'Other Floor Type'), ('plan_configuration', 'Plan Configuration'), ('condition_post_eq', 'Condition Post Eq'), ('technical_solution_proposed', 'Technical Solution')]
    list_y = [('foundation_type', 'Foundation Type'), ('damage', 'Damage Grade'), ('roof_type', 'Roof Type'), ('land_surface_condition', 'Land Surface'), ('height_ft_pre_eq', 'Height'), ('plinth_area_sq_ft', 'Plinth Area'), ('height_ft_post_eq', 'Height Post'), ('count_floors_pre_eq', 'Count Floors'), ('count_floors_post_eq', 'Count Floors Post'), ('vdcmun_id', 'Municipality id'), ('district_id', 'District id'), ('position', 'Position'), ('other_floor_type', 'Other Floor Type'), ('plan_configuration', 'Plan Configuration'), ('condition_post_eq', 'Condition Post Eq'), ('technical_solution_proposed', 'Technical Solution')]
    list_est = [('count', 'Count'), ('avg', 'Average'), ('max', 'Max'), ('min', 'Min')]
    list_hue = [('damage', 'Damage Grade'), ('foundation_type', 'Foundation Type'), ('roof_type', 'Roof Type'), ('land_surface_condition', 'Land Surface'), ('count_floors_pre_eq', 'Count Floors'), ('count_floors_post_eq', 'Count Floors Post'), ('district_id', 'District id'), ('position', 'Position'), ('other_floor_type', 'Other Floor Type'), ('plan_configuration', 'Plan Configuration'), ('condition_post_eq', 'Condition Post Eq'), ('technical_solution_proposed', 'Technical Solution')]

    return render_template(
        # file yang akan menjadi response dari API
        'category.html',
        # plot yang akan ditampilkan
        plot=plot,
        # menu yang akan tampil di dropdown 'Jenis Plot'
        focus_plot='histplot',
        # menu yang akan muncul di dropdown 'sumbu X'
        focus_x='foundation_type',

        # untuk sumbu Y tidak ada, nantinya menu dropdown Y akan di disable

        # menu yang akan muncul di dropdown 'Estimator'
        focus_estimator='count',
        # menu yang akan tampil di dropdown 'Hue'
        focus_hue='damage',
        # list yang akan digunakan looping untuk membuat dropdown 'Jenis Plot'
        drop_plot= list_plot,
        # list yang akan digunakan looping untuk membuat dropdown 'Sumbu X'
        drop_x= list_x,
        # list yang akan digunakan looping untuk membuat dropdown 'Sumbu Y'
        drop_y= list_y,
        # list yang akan digunakan looping untuk membuat dropdown 'Estimator'
        drop_estimator= list_est,
        # list yang akan digunakan looping untuk membuat dropdown 'Hue'
        drop_hue= list_hue)


@app.route('/cat_fn/<nav>')
def cat_fn(nav):

    # saat klik menu navigasi
    if nav == 'True':
        cat_plot = 'histplot'
        cat_x = 'district_id'
        cat_y = 'height_ft_pre_eq'
        estimator = 'count'
        hue = 'damage'
    
    # saat memilih value dari form
    else:
        cat_plot = request.args.get('cat_plot')
        cat_x = request.args.get('cat_x')
        cat_y = request.args.get('cat_y')
        estimator = request.args.get('estimator')
        hue = request.args.get('hue')

    if estimator == None:
        estimator = 'count'
    
    # Saat estimator == 'count', dropdown menu sumbu Y menjadi disabled dan memberikan nilai None
    if cat_y == None:
        cat_y = 'height_ft_pre_eq'

    list_plot = [('histplot', 'Histogram'), ('boxplot', 'Box')]
    list_x = [('foundation_type', 'Foundation Type'), ('age_building', 'Age'), ('damage', 'Damage Grade'), ('roof_type', 'Roof Type'), ('land_surface_condition', 'Land Surface'), ('height_ft_pre_eq', 'Height'), ('plinth_area_sq_ft', 'Plinth Area'), ('height_ft_post_eq', 'Height Post'), ('count_floors_pre_eq', 'Count Floors'), ('count_floors_post_eq', 'Count Floors Post'), ('vdcmun_id', 'Municipality id'), ('district_id', 'District id'), ('position', 'Position'), ('other_floor_type', 'Other Floor Type'), ('plan_configuration', 'Plan Configuration'),   ('condition_post_eq', 'Condition Post Eq'), ('technical_solution_proposed', 'Technical Solution')]
    list_y = [('foundation_type', 'Foundation Type'), ('age_building', 'Age'), ('damage', 'Damage Grade'), ('roof_type', 'Roof Type'), ('land_surface_condition', 'Land Surface'), ('height_ft_pre_eq', 'Height'), ('plinth_area_sq_ft', 'Plinth Area'), ('height_ft_post_eq', 'Height Post'), ('count_floors_pre_eq', 'Count Floors'), ('count_floors_post_eq', 'Count Floors Post'), ('vdcmun_id', 'Municipality id'), ('district_id', 'District id'), ('position', 'Position'), ('other_floor_type', 'Other Floor Type'), ('plan_configuration', 'Plan Configuration'),   ('condition_post_eq', 'Condition Post Eq'), ('technical_solution_proposed', 'Technical Solution')]
    list_est = [('count', 'Count'), ('avg', 'Average'), ('max', 'Max'), ('min', 'Min')]
    list_hue = [('damage', 'Damage Grade'), ('foundation_type', 'Foundation Type'), ('roof_type', 'Roof Type'), ('land_surface_condition', 'Land Surface'), ('count_floors_pre_eq', 'Count Floors'), ('count_floors_post_eq', 'Count Floors Post'), ('district_id', 'District id'), ('position', 'Position'), ('other_floor_type', 'Other Floor Type'), ('plan_configuration', 'Plan Configuration'), ('condition_post_eq', 'Condition Post Eq'), ('technical_solution_proposed', 'Technical Solution')]

    plot = category_plot(cat_plot, cat_x, cat_y, estimator, hue)
    return render_template(
        # file yang akan menjadi response dari API
        'category.html',
        # plot yang akan ditampilkan
        plot=plot,
        # menu yang akan tampil di dropdown 'Jenis Plot'
        focus_plot=cat_plot,
        # menu yang akan muncul di dropdown 'sumbu X'
        focus_x=cat_x,
        focus_y=cat_y,

        # menu yang akan muncul di dropdown 'Estimator'
        focus_estimator=estimator,
        # menu yang akan tampil di dropdown 'Hue'
        focus_hue=hue,
        # list yang akan digunakan looping untuk membuat dropdown 'Jenis Plot'
        drop_plot= list_plot,
        # list yang akan digunakan looping untuk membuat dropdown 'Sumbu X'
        drop_x= list_x,
        # list yang akan digunakan looping untuk membuat dropdown 'Sumbu Y'
        drop_y= list_y,
        # list yang akan digunakan looping untuk membuat dropdown 'Estimator'
        drop_estimator= list_est,
        # list yang akan digunakan looping untuk membuat dropdown 'Hue'
        drop_hue= list_hue
    )


def pie_plot(hue = 'damage'):
    


    vcounts = df[hue].value_counts()

    labels = []
    values = []

    for item in vcounts.iteritems():
        labels.append(item[0])
        values.append(item[1])
    
    data = [
        go.Pie(
            labels=labels,
            values=values
        )
    ]

    layout = go.Layout(title='Pie', title_x= 0.48)

    result = {'data': data, 'layout': layout}

    graphJSON = json.dumps(result,cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON

@app.route('/pie_fn')
def pie_fn():
    hue = request.args.get('hue')

    if hue == None:
        hue = 'damage'

    list_hue = [('damage', 'Damage Grade'), ('foundation_type', 'Foundation Type'), ('roof_type', 'Roof Type'), ('land_surface_condition', 'Land Surface'), ('count_floors_pre_eq', 'Count Floors'), ('count_floors_post_eq', 'Count Floors Post'), ('district_id', 'District id'), ('position', 'Position'), ('other_floor_type', 'Other Floor Type'), ('plan_configuration', 'Plan Configuration'), ('condition_post_eq', 'Condition Post Eq'), ('technical_solution_proposed', 'Technical Solution')]

    plot = pie_plot(hue)
    return render_template('pie.html', plot=plot, focus_hue=hue, drop_hue= list_hue)


@app.route('/pred_lr')
def pred_lr():
    return render_template('predict.html')

@app.route("/pred_result", methods = ["POST","GET"])
def pred_result():
    pass
    if request.method == "POST":
        input = request.form

        age = int(input['Umur'])

        c_floor = int(input['Jumlah_Lantai'])

        height = float(input['Tinggi_Bangunan'])

        plinth = float(input['Luas_Area_Bangunan'])

        foundation = input['Pondasi']
        if foundation == 'Mud mortar-Stone/Brick':
            A_Foundation = 'Mud mortar-Stone/Brick'
            dataFoundation = 'Mud mortar-Stone/Brick'
        elif foundation == 'Bamboo/Timber':
            A_Foundation = 'Bamboo/Timber'
            dataFoundation = 'Bamboo/Timber'
        elif foundation == 'Cement-Stone/Brick':
            A_Foundation = 'Cement-Stone/Brick'
            dataFoundation = 'Cement-Stone/Brick'
        elif foundation == 'RC':
            A_Foundation = 'RC'
            dataFoundation = 'RC'
        elif foundation == 'Other':
            A_Foundation = 'Other'
            dataFoundation = 'Other'
        
        roof = input['Atap']
        if roof == 'Bamboo/Timber-Light roof':
            A_Roof = 'Bamboo/Timber-Light roof'
            dataRoof = 'Bamboo/Timber-Light roof'
        elif roof == 'Bamboo/Timber-Heavy roof':
            A_Roof = 'Bamboo/Timber-Heavy roof'
            dataRoof = 'Bamboo/Timber-Heavy roof'
        elif roof == 'RCC/RB/RBC':
            A_Roof = 'RCC/RB/RBC'
            dataRoof = 'RCC/RB/RBC'

        ground_floor = input['Lantai']
        if ground_floor == 'Mud':
            A_Ground_floor = 'Mud'
            dataGround_floor = 'Mud'
        elif ground_floor == 'RC':
            A_Ground_floor = 'RC'
            dataGround_floor = 'RC'
        elif ground_floor == 'Brick/Stone':
            A_Ground_floor = 'Brick/Stone'
            dataGround_floor = 'Brick/Stone'
        elif ground_floor == 'Timber':
            A_Ground_floor = 'Timber'
            dataGround_floor = 'Timber'
        elif ground_floor == 'Other':
            A_Ground_floor = 'Other'
            dataGround_floor = 'Other'
        
        ground = input['Konstruksi_Lantai']
        if ground == 'TImber/Bamboo-Mud':
            A_Ground = 'TImber/Bamboo-Mud'
            dataGround = 'TImber/Bamboo-Mud'
        elif ground == 'Timber-Planck':
            A_Ground = 'Timber-Planck'
            dataGround = 'Timber-Planck'
        elif ground == 'Not applicable':
            A_Ground = 'Not applicable'
            dataGround = 'Not applicable'
        elif ground == 'RCC/RB/RBC':
            A_Ground = 'RCC/RB/RBC'
            dataGround = 'RCC/RB/RBC'
        

        build1 = pd.DataFrame({
            'age_building': [age],
            'count_floors_pre_eq': [c_floor],
            'plinth_area_sq_ft': [plinth],
            'height_ft_pre_eq': [height],
            'foundation_type' : [dataFoundation],
            'roof_type': [dataRoof],
            'ground_floor_type': [dataGround_floor],
            'other_floor_type': [dataGround]
        })
        

        pred = model.predict(build1)[0]
        print(pred)

        if pred == 0:
            hasil = 'Memiliki Kemungkinan Kerusakan Rendah'
        else:
            hasil = 'Memiliki Kemungkinan Kerusakan Tinggi'
        
        return render_template('result.html', age = age, c_floor = c_floor, height = height, plinth = plinth, foundation = A_Foundation, roof = A_Roof, 
            ground_floor = A_Ground_floor, ground = A_Ground, result = hasil)

@app.route('/about')
def about():
    return render_template('about.html')
    

if __name__ == '__main__':
    # Load Model
    model = joblib.load('Model.sav')
    app.run(debug=True)
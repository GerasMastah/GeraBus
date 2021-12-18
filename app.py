import requests
import configparser
from flask import Flask, render_template, request, session, redirect, url_for
#from flask_mysqldb import MySQL
#import mysql.connector
from datetime import datetime, date, timezone,timedelta
import time
import string
import random
#from humanfriendly import format_timespan
import sqlite3
from fpdf import FPDF
Ruta1 = "test"

app = Flask(__name__)

app.secret_key = "TioGeras23!"
##DATABASE!!
conn = sqlite3.connect('gerabus.db', check_same_thread=False)
print ("Opened database successfully")



boletoID = ""


today = str(date.today())

present = datetime.now()
tomorrow = present + timedelta(1)
#tomorrow = datetime.date.today() + datetime.timedelta(days=1)

'''Esta funcion genera un string aleatorio para ser utilizado como numero de control '''
def controlNumber():
    N = 10
    res = ''.join(random.choices(string.ascii_uppercase + string.digits, k = N))
    return (str(res))

#secondsPassed = 102488.765162
#print(format_timespan(secondsPassed))



'''pagina principal INDEX '''
@app.route('/', methods =['GET', 'POST'])
def index():



    
    timeNow = datetime.now()

    
    newDate = request.form.get('outTime')
    
    if (newDate is not None):
        timeNow = datetime.strptime(newDate, '%Y-%m-%d %H:%M:%S.%f')
        
    
    print("out Time: ",timeNow)
    items = []
    cursor = conn.execute("SELECT * from RUTAS")
    conn.commit()
    for item in cursor:
        items.append(item[1]+" - " + item[2])

    print(items)

    return render_template('index.html', data = items, today = today, tomorrow = tomorrow)



@app.route('/comprarAsistente', methods =['GET', 'POST'])
def comprarAsitente():

    if "user" in session:
        user = session["user"]
        timeNow = datetime.now()

        
        newDate = request.form.get('outTime')
        
        if (newDate is not None):
            timeNow = datetime.strptime(newDate, '%Y-%m-%d %H:%M:%S.%f')
            
        
        print("out Time: ",timeNow)
        items = []
        cursor = conn.execute("SELECT * from RUTAS")
        conn.commit()
        for item in cursor:
            items.append(item[1]+" - " + item[2])

        print(items)

        return render_template('comprarAsistente.html', data = items, today = today, tomorrow = tomorrow)
    else:
        return redirect(url_for("login"))

'''pagina del panel de control'''
@app.route('/dashboard', methods =['GET', 'POST'])
def dashboard():

    if "user" in session:
        user = session["user"]

        item = conn.execute("SELECT * from BOLETOS")
        conn.commit()
        print(item)

        return render_template('dashboard.html', data = item, today = today, tomorrow = tomorrow)
    else:
        return redirect(url_for("login"))



'''Muestra el historial de vehiculos que han abandonado el estacionamiento'''
@app.route('/salidas.html', methods =['GET', 'POST'])
def salidas():

    print(session["user"])

    if session["user"] == "gws":
        user = session["user"]
        buses = []
        cities = []
        cursor = conn.execute("SELECT plate from AUTOBUSES where status=1 ")
        cursor2 = conn.execute("SELECT ciudad from CIUDADES")
        for item in cursor:
            buses.append(item)
        #print(buses)

        for item in cursor2:
            cities.append(item)
        #print(cities)


        ##Inserta nueva ruta
        #if request.form.get('cities_origen')== NULL
        origen = request.form.get('cities_origen')
        destino = request.form.get('cities_destino')
        fecha_salida = request.form.get('fecha_salida')
        autobus = request.form.get('autobus')

        placa = request.form.get('placa')
        asientos = request.form.get('asientos')
        chofer = request.form.get('chofer')
        terminal = request.form.get('city_belong')
        status = 1
        #print(fecha_salida)
        try:
            print(placa, asientos, chofer, terminal)
            conn.execute("INSERT INTO RUTAS (ORIGEN,DESTINO,DEPARTURE, AUTOBUS) VALUES (?,?,?,?)",(origen, destino, fecha_salida, autobus))
            #conn.commit()
            query = "UPDATE AUTOBUSES SET STATUS = 'FALSE' where PLATE= " + autobus
            #print(query)
            #conn.commit()
            
            

            conn.execute(query)
            conn.commit()
            #query = "Update USERS set name = ? where id = ?"
            #cursor.execute(query,(names,idd,))
            #conn.close()
            pass
        except Exception as e:
            print(e)
        try:
            print("test")
            print("INSERT INTO AUTOBUSES (PLATE,STATUS,SEATS, TERMINAL, CHOFER) VALUES " + placa, status, asientos, terminal, chofer)
            conn.execute("INSERT INTO AUTOBUSES (PLATE,STATUS,SEATS, TERMINAL, CHOFER) VALUES (?,?,?,?,?)",(placa, status, asientos, terminal, chofer))
            conn.commit()
            pass

        except Exception as e:
            print(e)

        return render_template('salidas.html', tomorrow = tomorrow, buses = buses, cities = cities, today = today)
    else:
        return redirect(url_for("login"))

'''da la opcion para pagar boleto asi como el desglose del total a pagar'''
@app.route('/pagar.html', methods =['GET', 'POST'])
def pagar():
    destino = request.form.get('Destino')
    salida = request.form.get('fecha_salida')
    pasajeros = request.form.get('pasajeros')
    cliente = request.form.get('cliente')
    regreso = request.form.get('fecha_regreso')

    NumBoleto = controlNumber()
    db_registro = NumBoleto + salida+" payment"+ " vendido "+ destino+ pasajeros+ cliente
    print(db_registro)

    if regreso == None:
        salida = salida
    else:
        salida = salida +" / " + str(regreso)

    # save FPDF() class into a 
    # variable pdf
    pdf = FPDF()
      
    # Add a page
    pdf.add_page()
      
    # set style and size of font 
    # that you want in the pdf
    pdf.set_font("Arial", size = 15)

    header = "Cliente"  + "     " + "Destino" + " " + "Salida" + " " + "Pasajeros"

    datos_boleto = cliente + " " + destino + " " + salida + " " + pasajeros
      
    # create a cell
    pdf.cell(200, 10, txt = header, ln = 1, align = 'C')
    pdf.cell(200, 10, txt = datos_boleto, ln = 2, align = 'C')
      
    # save the pdf with name .pdf
    pdf.output("static/assets/pdfs/boleto.pdf") 

            
    return render_template('pagar.html', tomorrow = tomorrow, destino = destino, salida = salida, pasajeros = pasajeros, cliente = cliente, NumBoleto = NumBoleto , db_registro = db_registro, today = today)


@app.route('/pagado', methods =['GET', 'POST'])
def pago():
    

    try:
        tipo_pago = request.form.get('pagado')
        print(tipo_pago)

        NumBoleto = request.form.get('NUMBOLETO')
        destino = request.form.get('DESTINO')
        salida = request.form.get('FECHA_SALIDA')
        pasajeros = request.form.get('PASAJEROS')
        cliente = request.form.get('NOMBRE')
        status = "vendido"
        print(destino)

        conn.execute("INSERT INTO BOLETOS (CONTROL_NUMBER, SOLD_DATE, PAYMENT, CURRENT_STATUS, DESTINO, PASAJEROS, CLIENTE) VALUES (?, ?, ?, ?, ?, ?, ?)",
          (NumBoleto, salida, tipo_pago, status, destino, pasajeros, cliente))
        conn.commit()
        pass
    except Exception as e:
        items = []
        cursor = conn.execute("SELECT * from RUTAS")
        conn.commit()
        for item in cursor:
            items.append(item[1]+" - " + item[2])

        print(items)
        return render_template('index.html', tomorrow = tomorrow, data = items, today = today)
    



    return render_template('errorPago.html', tomorrow = tomorrow, NumBoleto = NumBoleto, destino = destino, salida=salida, pasajeros=pasajeros, cliente=cliente, pago=tipo_pago, today = today)




@app.route('/admin', methods =['GET', 'POST'])
def admin():



    return render_template('admin.html', tomorrow = tomorrow, today = today)

@app.route('/tomarBoleto.html', methods =['GET', 'POST'])
def tomarBoleto():

    item = conn.execute("SELECT * from BOLETOS")

    
    return render_template('tomarBoleto.html', tomorrow = tomorrow, today = today)





@app.route('/cancelar.html', methods =['GET', 'POST'])
def cancelarBoleto():
    if "user" in session:
        user = session["user"]
        print(request.form.get('cancelar'))
        cNumber =request.form.get('cancelar')

        query = "UPDATE BOLETOS SET CURRENT_STATUS = 'CANCELADO' where CONTROL_NUMBER= ?", (cNumber)
        conn.execute("UPDATE BOLETOS SET CURRENT_STATUS = 'CANCELADO' where CONTROL_NUMBER= ?", (cNumber,))
        conn.commit()


    
        return render_template('cancelar.html', tomorrow = tomorrow, today = today)
    else:
        return redirect(url_for("login"))

    


@app.route('/login.html', methods =['GET', 'POST'])
def login():

    user = request.form.get('username')
    

    if (request.form.get('loginButton') == "Login"):
        if (user == "gws"):
            session["user"] = user
            print(session)

            item = conn.execute("SELECT * from BOLETOS")
            conn.commit()

            return render_template('dashboard.html', data = item, today = today, tomorrow = tomorrow)

        if (user == "AsistenteVentas"):
            session["user"] = user

            item = conn.execute("SELECT * from BOLETOS")
            conn.commit()

            return render_template('dashboard_asistente.html', data = item, today = today, tomorrow = tomorrow)
    else:
            error = "Credenciales Invalidas!"
            return render_template('login.html', tomorrow = tomorrow, today = today)

    return render_template('login.html', tomorrow = tomorrow, today = today)



@app.route('/consultaBoleto.html', methods =['GET', 'POST'])
def consultaBoleto():
    


    try:
        consulta = request.form.get('#Boleto')
        print(consulta)
        items = conn.execute("SELECT * from BOLETOS where CONTROL_NUMBER= ? ",(consulta,))
        print(items)
        conn.commit()
        itemlist = []

        consulta = items
        print(consulta)
        for dato in items:
            print("consulta")
            print(dato)
            itemlist.append(dato)

        print("consulta2")
        print(itemlist)

        # save FPDF() class into a 
        # variable pdf
        pdf = FPDF()
      
        # Add a page
        pdf.add_page()
      
        # set style and size of font 
        # that you want in the pdf
        pdf.set_font("Arial", size = 15)

        header = "Cliente"  + "                       " + "Destino" + "       " + "Salida" + "                " + "Pasajeros"

        itemsito = itemlist[0]
        print(itemsito[0])
      
        # create a cell
        pdf.cell(200, 10, txt = header, ln = 1, align = 'C')
        pdf.cell(200, 10, txt = itemsito[7] +"     " +  itemsito[5] +"     " +  itemsito[2] +"     " +  str(itemsito[6]), ln = 2, align = 'C')
      
        # save the pdf with name .pdf
        pdf.output("static/assets/pdfs/boleto.pdf") 
        pass
    except Exception as e:
        print(e)
        pass

        
        return render_template('index.html', tomorrow = tomorrow, today = today)
    



    return render_template('consultaBoleto.html', tomorrow = tomorrow, today = today, item =itemlist )

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)


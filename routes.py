from app import app
from flask import render_template,request
import sqlite3
from celery import Celery
import pdfkit

##con=sqlite3.connect("slangweb.db")
##con.execute
##c=con.cursor()
##print("base de datos abierta")
##
##
##def creartabla():
##    c.execute("""
##    CREATE TABLE SLANGSWEB(
##    ID  INTEGER PRIMARY KEY AUTOINCREMENT,
##    SLANG        TEXT                 NOT NULL,
##    SIGNIFICADO  TEXT                 NOT NULL,
##    USER        TEXT                  NOT NULL,
##    Name        TEXT                  NOT NULL,
##    LOCATION   TEXT                    NOT NULL
##    )""")
##def rellenar_tabla():
##    c.execute("""
##         INSERT INTO slangsweb(ID,SLANG,SIGNIFICADO)
##         VALUES(1,'Que xopa','saludo')
##         """)
##
##    c.execute("""
##         INSERT INTO slangsweb(ID,SLANG,SIGNIFICADO)
##         VALUES(2,'Mopri','Amigo cercano')
##         """)
##
##    c.execute("""
##         INSERT INTO slangsweb(ID,SLANG,SIGNIFICADO)
##         VALUES(3,'Rantan','Bastante')
##         """)
##    con.commit()
##creartabla()
##rellenar_tabla()
##print("tabla creada")


def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery
##añadir registro
@app.route("/")
def index():
    return render_template("index.html");

@app.route("/add")
def add():
    return render_template("add.html")
@app.route("/savedetails",methods =["POST","GET"])
def saveDetails():
    msg="msg"
    if request.method == "POST":
        try:
            Slang=request.form["Slang"]
            Significado=request.form["significado"]
            with sqlite3.connect("slangweb.db") as con:
                cur=con.cursor()
                cur.execute("INSERT into SLANGSWEB(Slang,Significado) values(?,?)",(Slang,Significado))
                con.commit()
                msg="Slang agregado con éxito!"
        except:
             con.rollback()
             msg="No se puede agregar slang al diccionario"
        finally:
            return render_template("success.html",msg=msg)
            con.close()
#ver lista
@app.route("/view")
def view():
    con=sqlite3.connect("slangweb.db")
    con.row_factory=sqlite3.Row
    cur=con.cursor()
    cur.execute("select * from SLANGSWEB")
    rows= cur.fetchall()
    return render_template("view.html",rows=rows)
#eliminar registro
@app.route("/delete")
def delete():
    return render_template("delete.html")
##eliminar registro
@app.route("/deleterecord",methods = ["POST"])  
def deleterecord():  
    ID = request.form["ID"]  
    with sqlite3.connect("slangweb.db") as con:  
        try:  
            cur = con.cursor()  
            cur.execute('DELETE FROM SLANGSWEB WHERE ID=?',ID)  
            msg = "eliminado con éxito!" 
        except:  
            msg = "no se puede eliminar" 
        finally:  
            return render_template("eliminar_registro.html")
#editar registro
@app.route('/Editar_registro/<int:id>',methods=['GET','POST'])
def Editar_registro(id):
    return render_template('editar_registro.html')

##enviar correo electronico
@celery.task(name='celery_mail_pdf.send')
def send(user,name,location):
    rendered = render_Tempalte('pdf_Template.html',name=name, location=location)
    pdf=pdfkit.from_string(rendered, False)
    cur = con.cursor()  
    usuario=  cur.execute("select * from SLANGSWEB WHERE USER ==user")
    msg=Message('Hola',sender='Francisco@gmail.com',recipients=['usuario.email'])
    msg.attach("result.pdf","application/pdf",pdf)
    mail.send(msg)
    msg= Message('Hello',sender='francisco@')
if __name__== '__main__':
    app.run(debug=True)

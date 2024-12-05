from flask import Flask, render_template, url_for, request, redirect, session, sessions, jsonify
import base as db
from datetime import datetime

application = Flask(__name__)
application.config['SECRET_KEY'] = 'jkguishgUIHUIHiughduihsUIGHiughSIDGHUs'
domain = 'http://udp-express.com'
import aiosqlite

async def conn():
    return await aiosqlite.connect('./base.db')


@application.context_processor
def handle_context():
    return dict(
        datetime = datetime,
        day = 18,
        month = 2,
        year = 2023,
        )

@application.route('/')
async def index():
    return render_template('/index.html')

@application.route('/about')
async def about():
    return render_template('/aboutus.html')

@application.route('/contacts')
async def contacts():
    return render_template('/contact.html')

@application.route('/logistics')
async def logistics():
    return render_template('/logistics.html')

@application.route('/services')
async def services():
    return render_template('services.html')

@application.route('/roter/<string:to>')
async def router(to):
    if str(to) == str('index'):
        return redirect(domain + '/')
    if str(to) == str('services'):
        return redirect(domain + '/services')
    if str(to) == str('logistics'):
        return redirect(domain + '/logistics')
    if str(to) == str('contacts'):
        return redirect(domain + '/contacts')
    if str(to) == str('about'):
        return redirect(domain + '/about')
    

@application.route('/admin', methods = ['POST', 'GET'])
async def admin():
    if request.method == 'GET':
        return render_template('/admin/login.html')
    else:
        login = request.form['a-username']
        password = request.form['a-password']
        res = await db.check_admin(login=login, password = password)
        if res == True:
            session_key = await db.add_session(login = login)
            session['session'] = session_key
            return redirect(str(domain) + '/apanel')
        elif res == False:
            return 'Неверный пароль!'
        else:
            return 'Аккаунта с таким логином не существует!'


@application.route('/apanel')
async def apanel():
    if await db.check_session(session=session.get('session')) == True:
        return render_template('admin/panel.html')
    else:
        return redirect(domain + "/admin")

@application.route('/createtrack', methods=["GET", "POST"])
async def createtrack():
    if request.method == 'GET':
        if await db.check_session(session=session.get('session')) == True:
            return render_template('admin/create_track.html', day = int(18), year = int(2023), month = int(2))
        else:
            return redirect(domain + '/admin')
    if request.method == 'POST':
        if await db.check_session(session=session.get('session')) == True:
            op = 0
            res = await db.new_track(track = request.form['track_number'], sender = request.form['sender'], recipient=request.form['recipient'], weight=request.form['weight'])
            if res != 'Not':
                for i in range(40):
                    get_date = request.form[f'dates[{op}]'].replace(' ', ',')
                    await db.updateStatusTrack(track=request.form['track_number'], status_number=str(op), status = f"{get_date}|{request.form[f'names[{op}]']}")
                    op += 1
                return "Yes"
            else:
                return "Такой трек-номер уже существует!"
            
        else:
            return 'None'

@application.route('/search', methods=['POST', 'GET'])
async def search():
    if request.method == "GET":
        return render_template('/search.html', data = 'Stop')
    if request.method == 'POST':
        res = await db.track_check(track = str(request.form['track']))
        if res != False:
            resstatues = await db.getStatuses(track = str(request.form['track']))
            if resstatues != False:
                return render_template('/search.html', data = res, ss=resstatues, datetime=datetime)
            else:
                return render_template('/search.html', data = 'None')
        else:
            return render_template('/search.html', data = 'None')

@application.route('/orders', methods=['POST', "GET"])
async def orders():
    if request.method == 'GET':
        orders = await db.getOrders()
        if await db.check_session(session=session.get('session')) == True:
            return render_template('./admin/track_list.html', orders=orders)

@application.route('/srch/<string:track>')
async def srch(track):
    res = await db.track_check(track =track)
    resstatues = await db.getStatuses(track = track)
    return render_template('./search.html', data = res, ss = resstatues, datetime=datetime)

@application.route('/editTrack/<string:track>', methods=['POST', 'GET'])
async def editTrack(track):
    if request.method == 'GET':
        info = await db.get_track(track = track)
        statuses = await db.getStatuses(track = track)
        return render_template('./admin/edit.html',info = info ,track = str(track), stat = statuses)
    if request.method == 'POST':
        data = {
            'sender': request.form['sender'],
            'recipient': request.form['recipient'],
            'weight': request.form['weight'],
            'track': request.form['track_number']
        }
        op = 0  
        for i in range(40):
            await db.updateStatusTrack(track=track, status_number=op, status = F"{request.form[f'dates[{op}]'].replace(' ', ',')} | {request.form[f'names[{op}]']}")
            op += 1
        await db.newStatusTrack(old_track=track, track=data['track'])
        await db.changeTrack(track = track, sender=data['sender'], recipient=data['recipient'], weight=data['weight'], track_number=data['track'])
        return redirect(str(domain) + "/orders")

@application.route('/deleteTrack/<string:track>')
async def deleteTrack(track):
    try:
        db = await conn()
        sql = await db.cursor()
        await sql.execute("DELETE FROM tracks WHERE track = ?", (track,))
        await db.commit()
        await db.close()
        return("Yes")
    except:
        return("error")

@application.route('/logout')
async def logout():
    res = await db.logout(session=session.get('session'))
    if str(res) == 'yes':
        return redirect(domain + '/')
    else:
        return str(res)

if __name__ == "__main__":
    application.run(debug=True, host='127.0.0.1')
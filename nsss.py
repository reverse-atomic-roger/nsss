from flask import Flask, render_template, request
import random
from email.message import EmailMessage
import smtplib, ssl

app = Flask(__name__)

@app.route('/start')
def start() -> 'html':
    return render_template('start.html', the_title="Welcome to the NSSS Randomogrificator")

@app.route('/game_type', methods=['POST'])
def input() -> 'html':
    x = int(request.form['numberofpeeps'])
    partlist = []
    for person in range(x):
        partlist.append(
            {
                "number" : person+1
            }
            )
    
    if request.form['game_type'] == "nsss":
        return render_template('nsss.html', the_title="Enter Participants", partlist=partlist)

    if request.form['game_type'] == "email":
        return render_template('email.html', the_title="Enter Participants", partlist=partlist)

## processing for email SS ########################################

@app.route('/eshuffle', methods=['POST'])
def eshuffle() -> 'html':
    participants = []
    for x in range (int(len(request.form)/2)):
        participants.append([request.form[str(x + 1)],request.form[str(x + 1) + "email"]])

    results = replicate(participants)

    for x in range(len(results)):
        msg = EmailMessage()
        msg['Subject'] = "Secret Santa!"
        msg['From'] = "Python-nsss@hotmail.com"
        msg['To'] = results[x][0][1]
        msg.set_content("Welcome to the Loreto Science Secret Santa!\n\n The budget is £10. You have been chosen to buy a present for " + results[x][1][0])

        ## SSL secured email
        port = 587 #outlook.com smtp port
        password = "j2vxqmKDjhgukZW"
        host = "smtp-mail.outlook.com" #outlook.com host name for smtp
        login = "Python-nsss@hotmail.com" #username/email to log in with

        #create proper SSL context using system CA and certs
        context = ssl.create_default_context()

        with smtplib.SMTP(host,port) as server:
            server.starttls(context = context)
            server.login(login,password)
            server.send_message(msg)

    return render_template('success.html', the_title = "Success!")

## End processing for email SS ####################################

## processing for NSSS ############################################
@app.route('/shuffle', methods=['POST'])
def shuffle() -> 'html':
    participants = []
    for x in range(len(request.form)):
        participants.append(request.form[str(x + 1)])

    results = replicate(participants)

    return render_template('results.html',
                           results = results,
                           the_title = "NSSS Pairings")

## End processing for NSSS ############################################

## Processing for all paths, shuffling the list entered by the user ###

def randomise(list1: list, list2: list) -> list:
    y = True
    while y:
        y = False
        random.shuffle(list2)
        for x in range (len(list2)):
            if list2[x] == list1[x]:
                y = True

    return list2

def replicate(participants: list) -> list:

    shuffled = []
    for part in participants:
        shuffled.append(part)
        
    shuffled = randomise(participants, shuffled)
    results = []
    for x in range(len(participants)):
        results.append([participants[x],shuffled[x]])

    return results

## End shuffling ######################################################

## DB stuff ###########################################################

def log(req: 'flask_request', res: str) -> None:

    import psycopg

    dbconfig = {'host': '127.0.0.1',
                'user': 'nsss',
                'dbname': 'nssslog',
                'password': 'test'}

    with psycopg.connect(dbconfig) as conn:
        with conn.cusor() as cur:
            cur.execute("some sql")

app.run()

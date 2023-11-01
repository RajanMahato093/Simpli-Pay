from django.shortcuts import render, HttpResponse, redirect
import requests
# for connecting database
import mysql.connector as sql
# for sending email
import smtplib
from email.message import EmailMessage
# for generating OTP
import random
# for getting date
from datetime import date

admin_no="8928038098 / 9082802109"
admin_mail=["prabhat328@outlook.com","rajan03.mahato@gmail.com"]
def email_send(sub, body, to):
    msg = EmailMessage()
    msg.set_content(body)
    msg['subject'] = sub
    msg['to'] = to

    user = "simpli.pay.rp@gmail.com"
    msg['from'] = user
    password = "jrjhtfuumglkzamr"

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(user, password)
    server.send_message(msg)
    server.quit()


# Welcome page
def welcome(request):
    return render(request, 'welcome.html')

# signup
def signup(request):
    global fn,ln,phno,email,passwd,gender,dob
    # when submit button is clicked
    if request.method == 'POST':
        db = sql.connect(host='localhost', user='root',passwd="151103", database='simplipay')
        cursor = db.cursor()
        # saving form data in dictionary
        data = request.POST
        # saving data in python variable recieved from html form
        fn = request.POST['fname']
        ln = request.POST['lname']
        phno = request.POST['phno']
        email = request.POST['email']
        passwd = request.POST['passw']
        confpasswd = request.POST['confpassw']
        gender = request.POST['gender']
        dob = request.POST['dob']

        # checking if password field matches with confirm password
        if (passwd==confpasswd):
            # checking whether enetered phone or mailid is already registered
            reg_check=f"select userid from personal_detail where phno='{phno}' or email='{email}'"
            cursor.execute(reg_check)
            reg=tuple(cursor.fetchall())
            # if not already registered, send otp for email
            if reg==():
                global mail_otp, ph_otp
                mail_otp=random.randint(100000, 999999)
                ph_otp=random.randint(100000,999999)
                verf_sub="Email Verification | SimpliPay"
                email_send(verf_sub, f"This is you otp for verifying email and opening account with SimpliPay:\n\n{mail_otp}\n\nFor any help visit help section of our website or call on {admin_no} with your registered mobile number\n\nThank You,\nTeam SimpliPay", f"{email}")
                ph_verf()
                return redirect('http://127.0.0.1:8000/signup/email_verf')
            # if already registered, show message
            else:
                return HttpResponse("Phone/Email already registered")
        else:
            return redirect('http://127.0.0.1:8000/signup')
    return render(request, 'signup_pg.html')

# redirected for email verification if OTP is sent
def otp_verf(request):
    if request.method=='POST':
        global ent_mailotp, ent_photp
        db = sql.connect(host='localhost', user='root',passwd="151103", database='simplipay')
        cursor = db.cursor()
        # saving data in python variable recieved from html form
        ent_mailotp = request.POST['email_verf']
        ent_photp = request.POST['ph_verf']
        if (int(mail_otp)==int(ent_mailotp) and int(ph_otp)==int(ent_photp)):
            return redirect('http://127.0.0.1:8000/signup/set_uid')
        # if entered otp is incorrect, give a message
        else:
            return HttpResponse('Wrong OTP entered')

    return render(request, 'email_verf.html',{"mail":email,"phno":phno,})

def set_uid(request):
    if request.method=='POST':
            db = sql.connect(host='localhost', user='root',passwd="151103", database='simplipay')
            cursor = db.cursor()
            # saving data in python variable recieved from html form
            global uerid,tpin
            userid = request.POST['userid']
            tpin = request.POST['tpin']
            # checking if entered username is already in use
            chk_uid=f"select userid from personal_detail where userid='{userid}'"
            cursor.execute(chk_uid)
            chk=tuple(cursor.fetchall())
            if chk == ():
                # setting balance 500 by default
                bal=500
                reg_pdt = f"insert into personal_detail values('{fn}','{ln}',{phno},'{email}',{phno},'{userid}','{gender}','{dob}',{bal})"
                reg_credt = f"insert into credential values({phno},'{userid}',{phno},'{email}','{passwd}',{tpin},0)"
                # registering user in database
                cursor.execute(reg_pdt)
                cursor.execute(reg_credt)
                db.commit()
                # sending mail to admin about new user registration
                notify_admin="New Registration | SimpliPay"
                for i in admin_mail:
                    email_send(notify_admin, f"A new user has registered to SimpliPay\n\nName: {fn}\nEmail ID: {email}\nPh No.: {phno}\n\nEnjoy providing service😄👍", {i})
                # sending welcome message to user with details
                email_send("Registration Confirmation | SimpliPay", f"Congratulations,\nYou have successfully set your account with SimpliPay\n\nName: {fn} {ln}\nEmail ID: {email}\nPh No.: {phno}\nD.O.B.: {dob}\nUserID: {userid}\nTpin: {tpin}\nPassword: {passwd}\n*Acc no. is same as phone no.\nDo not share your Tpin or password with anyone.\n\nSee you enjoying our services\n\nRegards,\nTeam SimpliPay\nA platform you can trust", f"{email}")
                return redirect('http://127.0.0.1:8000/login')
            # if entered username is already in use
            else:
                return HttpResponse("UserID entered is not available")
    return render(request, 'set_userid.html')

# login function
def login(request):
        global userid
        userid=""
        passwd=""
        # when login button is clicked
        if request.method == 'POST':
            db = sql.connect(host='localhost', user='root', passwd="151103",database='simplipay')
            cursor = db.cursor()
            # saving data in python variable recieved from html form
            userid=request.POST['userid']
            passwd=request.POST['password']
            # fetching password for entered username
            entr1 = f"select userid from credential where userid='{userid}' and passwd='{passwd}'"
            cursor.execute(entr1)
            t = tuple(cursor.fetchall())
            # when password/username do not match
            if t == ():
                return render(request, 'login_pg.html')
            # if password & userid matches
            else:
                global lis
                lis=1
                return redirect('http://127.0.0.1:8000/dashb')
        
        return render(request, 'login_pg.html')

# user dashboard/homepage
def home(request):
        # if user has logged in, lis will be true
        if lis:
            # declaring a variable to prevent access without login
            global lis2
            lis2=1
            # connecting database
            db = sql.connect(host='localhost', user='root', passwd="151103",database='simplipay')
            cursor = db.cursor()
            # fetching details to show in sidebar
            entr1 = f"select fname,userid,email,phno,acc_no,balance from personal_detail where userid='{userid}'"
            cursor.execute(entr1)
            t = tuple(cursor.fetchall())
            # will be used as label for details to be displayed in sidebar
            t1=('Name:','UserId:','Email:','Phone No.:','Acc No.:','Balance:',)
            return render(request, 'dashboard.html',{'t':t,'t1':t1,'userid':userid,})
        # if link is directly tried to accessed without login
        else:
            return redirect('http://127.0.0.1:8000/login')

# add money
def add_mon(request):
    if lis2:
        global addmon
        addmon=0
        if request.method=='POST':
            addmon=request.POST['amount']

            db = sql.connect(host='localhost', user='root', passwd="151103",database="simplipay")
            cursor = db.cursor()
            addm=f"update personal_detail set balance=balance+{addmon} where userid='{userid}'"
            cursor.execute(addm)
            db.commit()
            return HttpResponse(f'{addmon} Rs. added successfully')
            # except:
            # return redirect('http://127.0.0.1:8000/addm')
        return render(request, 'add_money.html')
    else:
        redirect('http://127.0.0.1:8000/login')

# Bank Money Transfer
def bank_trans(request):
    if lis2:
        # variable for verifying entered acc no & balance
        global toacc,amt,crr_bal
        # connecting to mysql
        db = sql.connect(host='localhost', user='root', passwd="151103",database='simplipay')
        cursor = db.cursor()
        # for diplaying insufficient/sufficient balance to user in html page
        stat=f"select balance from personal_detail where userid='{userid}'"
        cursor.execute(stat)
        # storing data retrieved in t1
        t1=tuple(cursor.fetchall())
        crr_bal=int(t1[0][0])
        if request.method=="POST":
            # connecting to mysql
            db = sql.connect(host='localhost', user='root', passwd="151103",database='simplipay')
            cursor = db.cursor()
            # saving data in python variable recieved from html form
            toacc = request.POST['toacc']
            amt = request.POST['amt']
            # checking entered amount with balance
            if(int(amt)>crr_bal or int(amt)<1):
                return HttpResponse("Invalid Amount Entered")
            # checking eneterd account no.
            check=f"select userid from personal_detail where acc_no='{toacc}'"
            cursor.execute(check)
            cursor_res = tuple(cursor.fetchall())
            if cursor_res==() or cursor_res[0][0]==userid:
                return HttpResponse("<script>alert('Entered Account No. is Invalid')</script>")
            else:
                return redirect('http://127.0.0.1:8000/trans/actpin')

        context={"crr_bal":crr_bal,}
        return render(request, 'bank_trans.html',context)
    else:
        return redirect('http://127.0.0.1:8000/login')

# UserID Money Transfer
def userid_trans(request):
    if lis2:
        # variable for verifying entered userID & balance
        global touid,amt,crr_bal
        # connecting to mysql
        db = sql.connect(host='localhost', user='root', passwd="151103",database='simplipay')
        cursor = db.cursor()
        # for diplaying insufficient/sufficient balance to user in html page
        stat=f"select balance from personal_detail where userid='{userid}'"
        cursor.execute(stat)
        # storing data retrieved in t1
        t1=tuple(cursor.fetchall())
        crr_bal=int(t1[0][0])
        if request.method=="POST":
            # connecting to mysql
            db = sql.connect(host='localhost', user='root', passwd="151103",database='simplipay')
            cursor = db.cursor()
            # saving data in python variable recieved from html form
            touid = request.POST['touid']
            amt = request.POST['amt']
            # checking entered amount with balance
            if(int(amt)>crr_bal or int(amt)<1):
                return HttpResponse("Invalid Amount Entered")
            # checking eneterd account no.
            check=f"select userid from personal_detail where userid='{touid}'"
            cursor.execute(check)
            cursor_res = tuple(cursor.fetchall())
            if cursor_res==() or cursor_res[0][0]==userid:
                return HttpResponse("<script>alert('Entered UserID is Invalid')</script>")
            else:
                return redirect('http://127.0.0.1:8000/trans/utpin')

        context={"crr_bal":crr_bal,}
        return render(request, 'user_trans.html',context)
    else:
        return redirect('http://127.0.0.1:8000/transaction/login')

# QR Money Transfer
def qr_trans(request):
    if lis2:
        # variable for verifying uploaded QR & balance
        global touid,amt,crr_bal
        # connecting to mysql
        db = sql.connect(host='localhost', user='root', passwd="151103",database='simplipay')
        cursor = db.cursor()
        # for diplaying insufficient/sufficient balance to user in html page
        stat=f"select balance from personal_detail where userid='{userid}'"
        cursor.execute(stat)
        # storing data retrieved in t1
        t1=tuple(cursor.fetchall())
        crr_bal=int(t1[0][0])
        if request.method=="POST":
            # connecting to mysql
            db = sql.connect(host='localhost', user='root', passwd="151103",database='simplipay')
            cursor = db.cursor()
            # saving data in python variable recieved from html form
            touid = request.POST['touid']
            amt = request.POST['amt']
            # checking entered amount with balance
            if(int(amt)>crr_bal or int(amt)<1):
                return HttpResponse("Invalid Amount Entered")
            # checking eneterd account no.
            check=f"select * from personal_detail where userid='{touid}'"
            cursor.execute(check)
            cursor_res = tuple(cursor.fetchall())
            if cursor_res==():
                return HttpResponse("No registered user matches with uploaded QR")
            else:
                return redirect('http://127.0.0.1:8000/trans/utpin')

        context={"crr_bal":crr_bal,}
        return render(request, 'qr_trans.html',context)
    else:
        return redirect('http://127.0.0.1:8000/transaction/login')

# Confirming Tpin for Account transaction
def tpin_verf_acc(request):
    global tpin
    if request.method=="POST":
        # connecting to mysql
        db = sql.connect(host='localhost', user='root', passwd="151103",database='simplipay')
        cursor = db.cursor()
        # saving data in python variable recieved from html form
        tpin = request.POST['tpin']

        tpin_check=f"select * from credential where userid='{userid}' and tpin={tpin}"
        cursor.execute(tpin_check)
        t=tuple(cursor.fetchall())
        if t==():
            return redirect('http://127.0.0.1:8000/dashb')
        else:
            # updating balance
            sendm=f"update personal_detail set balance=balance+{amt} where acc_no='{toacc}'"
            deductm=f"update personal_detail set balance=balance-{amt} where userid='{userid}'"
            cursor.execute(sendm)
            cursor.execute(deductm)
            db.commit()
            # fetching debtors detail
            dr_mail=f"select email,userid,fname from personal_detail where userid='{userid}'"
            cursor.execute(dr_mail)
            tr1=tuple(cursor.fetchall())
            # fetching creditors detail
            cr_mail=f"select email,userid,fname from personal_detail where acc_no='{toacc}'"
            cursor.execute(cr_mail)
            tr2=tuple(cursor.fetchall())
            # recording transaction
            trans_his=f"insert into trans_his2 values ('{tr1[0][1]}','{tr1[0][2]}','{tr2[0][1]}','{tr2[0][2]}',{amt},'{date.today()}','0')"
            cursor.execute(trans_his)
            db.commit()
            # sending mail
            email_send("Transaction Update | SimpliPay", f"Dear user,\nyour Account has debited by Rs.{amt} to {toacc}\n\nTeam SimpliPay", f"{tr1[0][0]}")
            email_send("Transaction Update | SimpliPay", f"Dear user,\nyour Account has credited by Rs.{amt} from {userid}\n\nTeam SimpliPay", f"{tr2[0][0]}")
            return redirect('http://127.0.0.1:8000/transaction/status')
    return render(request, 'tpin_verf.html')

# Confirming Tpin for UserID & QR Transaction
def tpin_verf_uid(request):
    global tpin
    if request.method=="POST":
        # connecting to mysql
        db = sql.connect(host='localhost', user='root', passwd="151103",database='simplipay')
        cursor = db.cursor()
        # saving data in python variable recieved from html form
        tpin = request.POST['tpin']
        tpin_check=f"select * from credential where userid='{userid}' and tpin={tpin}"
        cursor.execute(tpin_check)
        t=tuple(cursor.fetchall())
        if t==():
            return redirect('http://127.0.0.1:8000/dashb')
        else:
            # updating balance
            sendm=f"update personal_detail set balance=balance+{amt} where userid='{touid}'"
            deductm=f"update personal_detail set balance=balance-{amt} where userid='{userid}'"
            cursor.execute(sendm)
            cursor.execute(deductm)
            db.commit()
            # fetching debtors detail
            dr_mail=f"select email,fname from personal_detail where userid='{userid}'"
            cursor.execute(dr_mail)
            tr1=tuple(cursor.fetchall())
            # fetching creditors detail
            cr_mail=f"select email,fname from personal_detail where userid='{touid}'"
            cursor.execute(cr_mail)
            tr2=tuple(cursor.fetchall())
            # recording transaction
            trans_his=f"insert into trans_his2 values ('{userid}','{tr1[0][1]}','{touid}','{tr2[0][1]}',{amt},'{date.today()}','0')"
            cursor.execute(trans_his)
            db.commit()
            email_send("Transaction Update | SimpliPay", f"Dear user,\nyour Account has debited by Rs.{amt} to {touid}\n\nTeam SimpliPay", f"{tr1[0][0]}")
            email_send("Transaction Update | SimpliPay", f"Dear user,\nyour Account has credited by Rs.{amt} from {userid}\n\nTeam SimpliPay", f"{tr2[0][0]}")
            return redirect('http://127.0.0.1:8000/transaction/status')
    return render(request, 'tpin_verf.html')

# Sending Otp on phone no. for verification
def ph_verf():
    url = f"https://2factor.in/API/V1/480100eb-2829-11ed-9c12-0200cd936042/SMS/+91{phno}/{ph_otp}/OTP1"

    payload={}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

# request money
def reqmon(request):
    if lis2:
        # variable for verifying entered userID & balance
        global fromuid,amt
        if request.method=="POST":
            # connecting to mysql
            db = sql.connect(host='localhost', user='root', passwd="151103",database='simplipay')
            cursor = db.cursor()
            # saving data in python variable recieved from html form
            fromuid = request.POST['fromuid']
            amt = request.POST['amt']
            # checking eneterd account no.
            check=f"select userid from personal_detail where userid='{fromuid}'"
            cursor.execute(check)
            cursor_res = tuple(cursor.fetchall())
            if cursor_res==() or cursor_res[0][0]==userid:
                return HttpResponse("<script>alert('Entered UserID is Invalid')</script>")
            else:
                crdetail=f"select fname,userid from personal_detail where userid='{userid}'"
                cursor.execute(crdetail)
                t1=tuple(cursor.fetchall())
                drdetail=f"select fname,userid from personal_detail where userid='{fromuid}'"
                cursor.execute(drdetail)
                t2=tuple(cursor.fetchall())
                ins_req=f"insert into req_mon values ('{t1[0][0]}','{t1[0][1]}','{t2[0][0]}','{t2[0][1]}',{amt},'{date.today()}','0')"
                cursor.execute(ins_req)
                db.commit()
                return HttpResponse("<script>alert('Money requested!')</script>")

        return render(request, 'reqmon.html')

# transaction successful message
def success(request):
    return render(request, 'success.html')

# transaction history
def trans_his(request):
    if (lis2):
        # connecting database
        db = sql.connect(host='localhost', user='root', passwd="151103",database='simplipay')
        cursor = db.cursor()
        # fetching data of Debited transaction
        dr_entry = f"select cr_fname,cr_userid,amt,tot from trans_his2 where dr_userid='{userid}'"
        cursor.execute(dr_entry)
        t1 = tuple(cursor.fetchall())
        # fetching data of Credited transaction
        cr_entry = f"select dr_fname,dr_userid,amt,tot from trans_his2 where cr_userid='{userid}'"
        cursor.execute(cr_entry)
        t2 = tuple(cursor.fetchall())
        # will be used as label for details to be displayed in sidebar
        t=('Name:','UserId:','Amount','Date')
        return render(request, 'trans_his.html',{'t':t,'t1':t1,'t2':t2,'userid':userid,})

# request recieved
def show_req(request):
    if (lis2):
        # connecting database
        db = sql.connect(host='localhost', user='root', passwd="151103",database='simplipay')
        cursor = db.cursor()
        fetch_req=f"select crname,cruid,amt,dor from req_mon where druid='{userid}'"
        cursor.execute(fetch_req)
        t1=tuple(cursor.fetchall())
        t=['Name','Userid','Amount','Date']
    return render(request,'rec_req.html',{'t':t,'t1':t1,})
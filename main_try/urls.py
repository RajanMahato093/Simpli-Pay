from django.contrib import admin
from django.urls import path, include
from main_try import views

urlpatterns = [
    path('', views.welcome, name='SimpliPay | Welcome'),
    path('signup/', views.signup, name='SimpliPay | SignUp'),
    path('login/', views.login, name='SimpliPay | Login'),
    path('signup/email_verf', views.otp_verf, name="SimpliPay | Email Verification"),
    path('signup/set_uid', views.set_uid, name="SimpliPay | Account Setup"),
    path('dashb/', views.home, name='SimpliPay | Home'),
    path('addm/', views.add_mon, name='Add Money | Bank'),
    path('bankt/', views.bank_trans, name='Transfer | Bank'),
    path('useridt/', views.userid_trans, name='Transfer | UserID'),
    path('qrt/', views.qr_trans, name='Transfer | QR'),
    path('money/request', views.reqmon, name='Req_Money'),
    path('rec/request', views.show_req, name='Rec_Request'),
    path('history/', views.trans_his, name='History | SimpliPay'),
    path('trans/utpin/', views.tpin_verf_uid, name='Tpin Verf | SimpliPay'),
    path('trans/actpin/', views.tpin_verf_acc, name='Tpin Verf | SimpliPay'),
    path('transaction/status', views.success,name='Transaction Status | SimpliPay'),

]
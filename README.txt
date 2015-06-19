For testing the autoLogin part, please connect with the machine below(by vnc or other tools):
address: 157.159.100.132
password: moocTSP91000


then open the site : http://127.0.0.1:8002/,
click LoginXBlock,
you can test with the account:
email:ines.wei@icloud.com
nom:wei
prenom:yuqing
with the option of "already have the account of ProctorU" to test the autologin part,
or you can test with other email who doesn't yet sign up in ProctorU, in this case it will create automaticallly an account in ProctorU and also return a link.


if you can not open the site, follow the steps below:
open an terminal, type the commands suivant:
>cd ~/xblock-sdk-master/
>python manage.py runserver 8002


IP=`cat /etc/network/interfaces | grep address |awk '{print $2;}'| grep 192`
echo $IP

cd /home/receiver/Desktop/DataDiodeReceiver/
python3 manage.py runserver $IP:8080

IP=`cat /etc/network/interfaces | grep address |awk '{print $2;}'| grep 192`
echo $IP

cd /home/transmitter/Desktop/DataDiodeTransmitter/
python3 manage.py runserver $IP:8080

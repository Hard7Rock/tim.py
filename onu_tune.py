# -*- coding: utf-8 -*-
"""Скрипт для налаштування ONU через модуль pexpect"""
#version 1.1
#author: hard
#contrib: silk (pretty output)
#moral support: deftones, den4ik, ihor

#Скрипт налаштування ONU

#Назва:Блок захопленя логіна і пароля
#Мета:	Стандартизувати процес авторизації
from sys import argv
from re import match
arguments = argv[1:]

proc Autentification { ip AllAuthData } {
	global spawn_id
	set login [lindex $AllAuthData 0];
	set pass [lindex $AllAuthData 1];
	set ena_pass [lindex $AllAuthData 2];

	spawn telnet $ip
	expect "Username:" {send "$login\r"}
	expect "*assword:" {send "$pass\r"}
	expect -re "^(.*)>|#$" {set dev_names $expect_out(1,string);send "enable\r"}
	expect "*assword:" {send "$ena_pass\r"}
	return $dev_names
}

#exp_internal 1
#log_user 1
if len(arguments) < 5:
    print "\nВикористання onu_tune: expect onu_tune ip_olt epon_port onu_mac abon_vlan abon_descr add_iptv\n\
ip_olt - ip адреса OLT в форматі X.X.X.X\n\
epon_port - номер EPON в форматі X/X\n\
onu_mac - mac ONU в форматі xxxx.xxxx.xxxx\n\
abon_vlan - номер абоненського VLAN\'a\n\
abon_descr - адреса проживання абонента: наприклад Kalinina.18\n\
add_iptv - прапор налаштування IPTV на ONU\n\n";
return 1

def Verify(args):
    #перевірка валідності вхідних данних
    #ip_olti
    isOk = True
    ip_olt =argv[1]
    if match("^\d+\.\d+\.\d+\.\d+$",ip_olt)==None:
        print "Невірно введена ІР адреса OLT\n";
        isOk = False
    #epon_number
    epon = argv[2]
    if match("^\d/[1-9](\d)?$",epon) == None:# перевірити на правильність?
        print "Невірно введений номер EPON: наприклад 0/3\n"
        isOk = False

    #onu_mac
    onu_mac = argv[3]
    if match("^[0-9a-f]{4}\.[0-9a-f]{4}\.[0-9a-f]{4}$",onu_mac) == None: 
        print "Невірний формат МАC адреси ONU: приклад fa3a.f7c5.f7c3\n"
        isOk = False

    #vlan  патерн
    abon_vlan = argv[4]
    if match("\d{4}" abon_vlan) == None:
        print "Невірно введений абонентський VLAN: приклад 1954\n"
        isOk = False 

    abon_descr = argv[5]
    IPTV_plus = argv[6]

    return isOk


#введення налаштувань
print "\n\n = Привязка ONU по MAC ="
expect "GP*#" { send "config\r" } #config режим
expect "*config#" { send "interface epon $epon\r" }	        #Вхід у налаштування epon
expect -re "#$" { send "epon bind-onu mac $onu_mac\r" }	        #Привязка ONU по MAC
expect -re "#$" { send "exit\r" }
expect -re "#$" { send "exit\r" }	#Вихід з режиму конфігурації

lid = 0
set timeout 1;

while {$lid==0} {
    #По таймауту поновлюється посил
    expect timeout {
        send "show epon active-onu mac-address $onu_mac\r";
        print "\n\n = Шукаємо чи привязалась ONU =\n";
    }
    expect -re "EPON$epon:\(\[1-9]\[0-9]?)" {
        print "\n\n = ONU привязалась до LID: $expect_out(1,string) =";
        set lid $expect_out(1,string); break;
    }
	set timeout 5;
}


print "\n\n = Норми рівнів сигналу: =\nІ - не вимірюється через надто потужний сигнал;\
\nІІ - 15-17 dBm\
\nIII - 22-24 dBm\n"

set timeout 5;

print " \n = Перевірка сили сигналу ONU -> OLT, таймаут $timeout сек. =\n"

sleep $timeout

expect -re ".*GP.*\#" {send "show epon optical-transceiver-diagnosis interface epon $epon:$lid\r"}

expect -re ".*GP.*\#" {send "\rshow epon interface EPON $epon:$lid onu ctc optical-transceiver-diagnosis\r"}
print " \n\n = Перевірка сили сигналу OLT -> ONU, таймаут $timeout сек. ="
#expect -re "\(-?\\d+\\.\\d\)" {set RxPower $expect_out(1,string)}
#send_user "RxPower: EPON$epon:$lid = $RxPower dBm"

#Заходимо в режим конфігурації
expect  -re "#$" {send "config\r"}

#Налаштовуємо базу VLAN
print "\n\n = Налаштовуємо VLAN =\n"
expect -re "config#$" {send "vlan $abon_vlan\r"}
expect -gl "*vlan$abon_vlan#" {send "exit\r"}

#Заходимо в налаштування порта gi0/3
expect -re "#$" {send "interface gi 0/3\r"}
print "\n\n = Налаштовуємо порти =\n"

#Прокидка VLAN на gi0/3
expect -re "#$" {send "switchport trunk vlan-allowed add $abon_vlan\r"}
expect -re "#$" {send "exit\r"}

#Вхід в налаштування EPON
expect -re "#$" {send "interface epon $epon\r"}
expect -re "#$" {send "switchport trunk vlan-allowed add $abon_vlan\r"}	#прокидка vlan на epon
#Вихід з налаштувань EPON
expect -re "#$" {send "exit\r"}


#Якщо ONU активна - налаштовуємо
expect -re "#$" {send "interface epon $epon:$lid\r"}				#Заходимо на ONU
print "\n\n = Налаштовуємо ONU =\n"
expect -re "#$" {send "description \$.$abon_descr\r"}				#Заповнюємо опис
expect -re "#$" {send "epon onu port 1 ctc vlan mode tag $abon_vlan\r"}		#Прокидаємо VLAN на ONU

#Налаштування ONU на мультикаст
if {$IPTV_plus=="add_iptv"} {
print "\n\n = Налаштовуємо мультикаст для IPTV =\n";
expect -re "#$" {send "epon onu port 1 ctc mcst tag-stripe enable\r"}
expect -re "#$" {send "epon onu port 1 ctc mcst mc-vlan add 4001\r"}
}

expect -re "#$" {send "exit\r";}    					#Вихід з налаштувань ONU
expect -re "GP_.*#" {send "exit\r";}    				#Вихід з режиму конфігурації
expect -re "GP_.*#" {send "write\r";}					#Збереження налаштувань
print "\n\n = Зберігаємо налаштування... =\n"
expect -re "OK!.*GP_.*#" {send "exit";}

print "\n\n = Налаштування успішно завершене! =\n"

exit 0;
#Налаштування завершене

if Verify(argv)==True:
    Connect()
    Bind()
    Config()
    Check()
    Exit()
else:
    exit()


# -*- coding: utf-8 -*-
"""Скрипт для роздруківок через модуль pexpect"""
import pexpect, auth, dev_specific, sys

#Мета:
#exp_internal 1

dev_ip = argv[1:]
set AllAuthData [GetAllAuthData]
#set AllAuthData ""

set buffer1 ""
file_out = "/tmp/Rozdruk.txt"
set file [open $file_out w];
print "Відкритий файл збереження статусу портів: $file_out\n";
print "Номер\tОбладнання\t\tАутентифікація\t\tОтриманя списку портів\n"


for ips in dev_ip:
	log_user 0
	stty rows 10000
	Autentification "10.10.[lindex $argv $i]" $AllAuthData
	dev = what_device()
	log_user 0
	if {$dev=="ec"} {expect -re "#$" {stty -echo; send "terminal length 512\r"; stty echo;}}
	expect -re "^.*#$" {stty -echo; send "[interface_status $dev]\r"; stty echo}
	expect -re "[interface_status $dev]\r(.*)\n(.*)#$" {
			set dev_desc $expect_out(2,string);
			set int_status $expect_out(1,string)
			append buffer1 "$dev_desc $int_status\n++++++\n\n";
			send "exit\r";
			send_user "[expr $i+1]\t$dev_desc\t\tOK\t\tOK\n";}
}

puts $file $buffer1

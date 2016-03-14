# -*- coding: utf-8 -*-
"""Скрипт для для автентифікації через модуль pexpect"""
from getpass import getpass, getuser
import pexpect
from sys import stdout
#Назва:Блок захопленя логіна і пароля
#Мета:	Стандартизувати процес авторизації


def Autentification (ip):
    spawn_id =pexpect.spawn("telnet "+ ip)
    spawn_id.logfile = stdout
    spawn_id.expect("Username:")
    spawn_id.sendline(getuser())
    spawn_id.expect('.assword:')
    spawn_id.sendline(getpass(prompt='Pass: '))
    spawn_id.expect(">|#\r\n")
    spawn_id.sendline("enable")
    spawn_id.expect(".assword:")
    spawn_id.sendline(getpass(prompt='Ena pass: '))
    spawn_id.interact()

#	expect "Username:" {send "$login\r"}
#	expect "*assword:" {send "$pass\r"}
#	expect -re "^(.*)>|#$" {set dev_names $expect_out(1,string); send "enable\r"}
#	expect "*assword:" {send "$ena_pass\r"}
    return spawn_id

Autentification("10.10.6.82")

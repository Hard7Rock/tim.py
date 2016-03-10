# -*- coding: utf-8 -*-
import pexpect
"""Назва:dev_specific - містить функції по визначенні обладнання до якого підключається user"""

def what_device(instance):
	"""Визначення типу обладнання по команді sh version"""
	instance.expect()

	log_user 0
stty rows 1000
expect -re ">|#$" {send "show version\r"}
expect {
	-re "(C|c)isco WS-C.*processor" {log_user 1; return "cisco"}
	-re "Marvell" {log_user 1; return "ec"}

	return 0

def interface_status(dev):
	"""Процедура повертає вірний запит команди відображення портів"""
	int_status = {
		"ec" : "show int brief",
		"cisco" :"show int status"
	}

	return int_status[dev]

def adequate_mac_style(mac, device):
	"""процедура яка задає адекватний стиль відображення мак адреси"""
	mac_style = {
		"ec":"[cisco2ec $mac]",
		"cisco": "[ec2cisco $mac]"
	}
	return 0

def adequate_interface_name (dev):
	device_list = {"ec":"Eth", "cisco":"GigabitEthernet|FastEthernet"}

	return device_list[dev]


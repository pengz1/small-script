#!/usr/bin/env python
"""
Test script for odr 817
"""
import time
import subprocess
import pexpect

def sudo_execute(cmd):
    """
    execute sudo function
    """
    child = pexpect.spawn(cmd)
    index = child.expect(["\[sudo\] password for[\S\s]*", pexpect.TIMEOUT])
    if index == 0:
        child.send("onrack")
    child.close()

def ssh_login(ip, passwd, user):
    """
    SSH login
    """
    ret = -1
    ssh = pexpect.spawn('ssh %s@%s' % (user, ip))
    try:
        i = ssh.expect(['password: ', 'continue connecting (yes/no)?'], timeout=5)
        if i == 0:
            ssh.sendline(passwd)
        elif i == 1:
            ssh.sendline('yes\n')
            ssh.expect('password: ')
            ssh.sendline(passwd)
        ret = 0
    except pexpect.EOF:
        print "EOF"
        ssh.close()
        ret = -1
    except pexpect.TIMEOUT:
        print "TIMEOUT"
        ssh.close()
        ret = -2
    return ret

def run_workflow(jth):
    """
    Anything
    """
    active_workflow_flag = True
    subprocess.check_output("rackhd -DW 57b583d51918b0800a3688dc", shell=True)
    rm_log_cmd = "sudo rm /var/log/upstart/*"
    sudo_execute(rm_log_cmd)
    subprocess.check_output("rackhd -i 57b583d51918b0800a3688dc -w Graph.BootstrapUbuntuMocks",
                            shell=True)
    for i in range(15):
        active_workflow_console = subprocess.check_output("rackhd -W 57b583d51918b0800a3688dc",
                                                          shell=True)
        if not active_workflow_console:
            time.sleep(10)
            arp_result = subprocess.check_output("arp | grep 2c:60:0c:83:f3:ce", shell=True)
            ip_str = arp_result.split(" ")[0]
            print ip_str
            ssh_result = ssh_login(ip_str, "monorail", "monorail")
            if not ssh_result:
                active_workflow_flag = False
            break
        time.sleep(30)

    if active_workflow_flag:
        time_string = time.strftime("%Y%m%d_%H%M%S")
        tar_cmd = "sudo tar -cvf /home/onrack/upstart_{}.tar /var/log/upstart".format(time_string)
        sudo_execute(tar_cmd)
        print "==============================================="
        print "This is the {}th test and it failed".format(jth)
        print "==============================================="

if __name__ == "__main__":
    for k in range(1000):
        run_workflow(k)

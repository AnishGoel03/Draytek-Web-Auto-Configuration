from selenium import webdriver
from selenium.webdriver.support.ui import Select
from urllib import parse
from base64 import b64encode
import csv, time

page_timeout = 5 # timeout in seconds

# Selectors used #############################################################################################

frame_main = "main"
frame_menu = "menu"

systemMaintenenceMenu_link_text = "System Maintenance"

snmpMenu_link_text = "SNMP"
enableSNMPAgent_name = "SNMPAgentEn"
snmpSetCommunitySelector_name = "SNMPSetCom"
snmpHostIp1_name = "SNMPMngHostIP0"
snmpHostIp2_name = "SNMPMngHostIP1"
snmpHostIp3_name = "SNMPMngHostIP2"
subnetValue1_name = "SNMPMngHostMask0"
subnetValue2_name = "SNMPMngHostMask1"
subnetValue3_name = "SNMPMngHostMask2"
snmpConfirmButton_name = "snmp_btnOk"

managementMenu_link_text = "Management"
managementInternetAccessOnButton_name = "sRMC"
managementSNMPServerOnButton_name = "sRMCSnmp"
managementConfirmButton_class = "btnw"

submitChangesButton_name = "submit"

##############################################################################################################

def fetch(filename):                                            # FETCHES CSV FILE, IF CSV FILE IS OPTED
    if filename[-4:] != ".csv":
        return []
    try:
        with open(filename, mode='r') as test:
            csv_reader = csv.reader(test)
            main = []
            for row in csv_reader:
                for value in row:
                    value = value.rstrip()
                main.append(row)
            
        return main
    
    except FileNotFoundError:
        return False
    
def encode(arg):                                                # ENCODES ARGUMENT INTO BASE64
    return parse.quote_plus(b64encode(str.encode(arg)))

def getSNMPOps():                                               # GETS SNMP DATA FROM USER (MANUAL)
    set_community = input("Set Community string: ")
    manager_host_ip_1 = input("Set Manager Host IP 1: ")
    manager_host_ip_2 = input("Set Manager Host IP 2: ")
    manager_host_ip_3 = input("Set Manager Host IP 3: ")
    subnet1 = input("Set Subnet Mask 1: ")
    subnet2 = input("Set Subnet Mask 2: ")
    subnet3 = input("Set Subnet Mask 3: ")

    SNMPOptions = {"set_community":set_community,
                   "manager_host_ip_1":manager_host_ip_1,
                   "manager_host_ip_2":manager_host_ip_2,
                   "manager_host_ip_3":manager_host_ip_3,
                   "subnet1":subnet1,
                   "subnet2":subnet2,
                   "subnet3":subnet3}

    return SNMPOptions

def getRouter(port = ''):                                       # GETS ROUTER DATA FROM USER (MANUAL)
    username = input("Enter username: ")
    password = input("Enter password: ")
    ip = input("Enter IP: ")
    port = input("Enter port: ")

    return username, password, ip, port

def checkIP(ip_check):                                          # CHECKS FORMAT OF IP ADDRESS
    ip_list = ip_check.split('.')
    if len(ip_list) != 4:
        return False
    for ip in ip_list:
        if ip.isdigit() == True:
            if int(ip) > 255:
                return False
        else:
            return False

def subnetCheck(subnet):                                        # CHECKS FORMAT OF SUBNET
    if subnet.isdigit():
        if int(subnet) > 32 or int(subnet) < 22:
            return False
    else:
        return False      

def validateCSV(data):                                          # VALIDATES ALL INPUTTED DATA TO ENSURE MATCHING FORMATS
    bad_routers = []
    for router in data:
        router[1] = router[1].replace(":","")
        invalid_checks = False
        if checkIP(router[0])== False:                          # ip check
            invalid_checks = True
            
        if router[1].isdigit():
            if int(router[1]) > 65535 or int(router[1]) < 0:
                invalid_checks = True                           # port check
        elif router[1] != '':
            invalid_checks = True

        for input_data in router[2:5]:          
            if type(input_data) != str:                         # username, password, community string check
                invalid_checks = True

        for input_data in router[5:8]:
            if checkIP(input_data)== False:                     # ip checks
                invalid_checks = True

        for input_data in router[8:11]:
            if subnetCheck(input_data)==False:                  # subnet checks
                invalid_checks = True

        if invalid_checks == True:
            bad_routers.append(router)

    if bad_routers == []:                                       # returns routers with invalid formatted text
        return True
    else:
        return bad_routers

def fillTextField(driver,element_name,text,value):              # FILLS TEXT FIELDS ON WEBDRIVER
    set_text = driver.find_element_by_name(element_name)
    if set_text.get_attribute("value") != value:
        driver.quit()
        return element_name
    else:
        set_text.clear()
        set_text.send_keys(text)
        return True

def selectBtn(driver,button_name):                              # SELECTS BUTTON IF NOT ALREADY SELECTED
    enableBtn = driver.find_element_by_name(button_name)        
    if not enableBtn.is_selected():                               
        enableBtn.click()

def selectSubnet(driver,element_name,subnet_to_set):            # SELECTS SUBNETS ON WEBDRIVER
    select = Select(driver.find_element_by_name(element_name))
    select.select_by_value(subnet_to_set)

def printInfo():
    print('''

    CONFIGURING DEVICE -
    
    IP: \t\t\t{ip}
    PORT: \t\t\t{port}


    ENTERED CONFIG -

    COMMUNITY STRING: \t\t{commstring}
    SNMP ACCESS 1: \t\t{acc1}
    SNMP ACCESS 2: \t\t{acc2}
    SNMP ACCESS 3: \t\t{acc3}
    SUBNET 1: \t\t\t{sub1}
    SUBNET 2: \t\t\t{sub2}
    SUBNET 3: \t\t\t{sub3}

    '''.format(ip = ip,
               port = port.replace(":",""),
               commstring = SNMPOptions['set_community'],
               acc1 = SNMPOptions['manager_host_ip_1'],
               acc2 = SNMPOptions['manager_host_ip_2'],
               acc3 = SNMPOptions['manager_host_ip_3'],
               sub1 = SNMPOptions['subnet1'],
               sub2 = SNMPOptions['subnet2'],
               sub3 = SNMPOptions['subnet3'],))                 # printing out relevent information

def logIn(driver):
    try:
        driver.get("https://{ip}{port}/cgi-bin/wlogin.cgi?aa={username}&ab={password}".format(
            username = encode(username),
            password = encode(password),
            ip = ip,
            port = port,))                                      # Logs into router
        
    except Exception as e:                                      # Returns exception if unable to log in
        print("\n{}".format(e))
        driver.quit()
        return e

    try:
        driver.switch_to.frame(frame_menu)
        return True
    
    except Exception as e:
        print("\nInvalid Credentials")
        driver.quit()
        return e

def fillSNMP(driver):    
    driver.find_element_by_link_text(snmpMenu_link_text).click()
    driver.switch_to.default_content()                          # finding elements on the website via xpath
    driver.switch_to.frame(frame_main)                              # navigation to correct page

    enable_SNMP_btn = driver.find_element_by_name(enableSNMPAgent_name)# enables SNMP if not already
    if not enable_SNMP_btn.is_selected():
        enable_SNMP_btn.click()
        
    valid = fillTextField(driver,snmpSetCommunitySelector_name,SNMPOptions['set_community'],'private')
    if valid != True:                                           
        return [valid]                  
    
    valid = fillTextField(driver,snmpHostIp1_name,SNMPOptions['manager_host_ip_1'],'')
    if valid != True:
        return [valid]
        
    valid = fillTextField(driver,snmpHostIp2_name,SNMPOptions['manager_host_ip_2'],'')
    if valid != True:
        return [valid]

    valid = fillTextField(driver,snmpHostIp3_name,SNMPOptions['manager_host_ip_3'],'')
    if valid != True:
        return [valid]                                          # locates and fills in relevant text fields in SNMP config
    
    selectSubnet(driver,subnetValue1_name,SNMPOptions['subnet1'])
    selectSubnet(driver,subnetValue2_name,SNMPOptions['subnet2'])
    selectSubnet(driver,subnetValue3_name,SNMPOptions['subnet3'])
                                                                # locates and selects desired subnet option
    driver.find_element_by_name(snmpConfirmButton_name).click() # applies changes
    return True

def fillManagement(driver):
    driver.switch_to.default_content()                          # locates management section
    driver.switch_to.frame(frame_menu)
    driver.find_element_by_link_text(managementMenu_link_text).click()

    driver.switch_to.default_content()
    driver.switch_to.frame(frame_main)

    selectBtn(driver,managementInternetAccessOnButton_name)     # enables internet management
    selectBtn(driver,managementSNMPServerOnButton_name)         # enables SNMP server

    driver.find_element_by_class_name(managementConfirmButton_class).click()
    
def config():                                                   # MAIN FUNCTION - DRIVES CHANGES
    try:
        printInfo()
        
        start_time = time.time()
        driver = webdriver.Firefox()                                # gets webdriver
        driver.set_page_load_timeout(page_timeout)                  # set page timeout
        driver.implicitly_wait(1)

        login_result = logIn(driver)
        if login_result != True:
            return login_result

        driver.find_element_by_link_text(systemMaintenenceMenu_link_text).click()
                                                                    # Navigates to System Maintenance - head sub section
        snmp_result = fillSNMP(driver)
        if snmp_result != True:                                     # Fills SNMP details
            return snmp_result

        fillManagement(driver)                                      # Fills Management details
        
        driver.find_element_by_name(submitChangesButton_name).click()
        driver.quit()                                               # enables all changes and restarts router
        
        elapsed_time = time.time() - start_time
        print("\nconfiguration took {:.2f}s\n".format(elapsed_time))
        return True
    except:
        return False
            
def analyseResults(result):                                     # ANALYSES RESULT AFTER ROUTER CONFIG 
    if type(result) == list:
        print("\nPrexisting SNMP Data found at {}. Action terminated".format(result[0]))
    elif result == True:
        print("UPDATE SUCCESSFUL, ROUTER {} IS NOW REBOOTING\n\n".format(ip))
    elif result == False:
        print("\n\nOperation Terminated: Gecko Driver closed")

def userCheck():                                                # FINAL CONFIRMATION WITH USER BEFORE CONFIGURATION IS LAUNCHED
    if input("\nInput recieved, proceed with configuration of routers? Y/N: ").upper() == 'Y':
        print("\n\nConfiguration Commencing [!]")
        return True
    else:
        print("\n\nAction aborted [!]")
        return False                                            # returns True or False dependent on whether user says Y or N


###############################################################################################################################################################################################################################################
###############################################################################################################################################################################################################################################

while True:
    choice = input("\nMANUAL or CSV input? ")                   # choice between manual input and csv file
    if choice.upper() == "MANUAL":
        username, password, ip, port = getRouter()
        SNMPOptions = getSNMPOps()

        if port != '':
            port = ':'+port

        validate_out = validateCSV([[ip,
                              port,
                              username,
                              password,
                              SNMPOptions['set_community'],
                              SNMPOptions['manager_host_ip_1'],
                              SNMPOptions['manager_host_ip_2'],
                              SNMPOptions['manager_host_ip_3'],
                              SNMPOptions['subnet1'],
                              SNMPOptions['subnet2'],
                              SNMPOptions['subnet3']
                              ]])
        
        if validate_out == True:                                # validates data to match format
            if userCheck() == True:
                result = config()                               # CONFIG FUNCTIONS FIRES -> ROUTER CONFIG COMMENCES
                analyseResults(result)                          # analyses results to see whether successful/not
                
        else:
            print("\nBad router config detected. Please review these and replace file:\n")
            for router in validate_out:
                print(router)
            print("\n\n")
                
            
    elif choice.upper() == "CSV":

        filename = input("\nCSV file name: ")
        router_list = fetch(filename)
        
        if router_list == False:
            print("\nfile not found")

        elif router_list == []:
            print("\ninvalid file")

        else:
            try:
                validate_out =  validateCSV(router_list)          # validates data to match format

                if validate_out == True:
                    if userCheck() == True:
                        total_start_time = time.time()
                        for entry in router_list:
                            username = entry[2]
                            password = entry[3]
                            ip = entry[0]
                            port = entry[1]
                            if port != '':
                                port = ':'+port
                            SNMPOptions = {"set_community":entry[4],
                                           "manager_host_ip_1":entry[5],
                                           "manager_host_ip_2":entry[6],
                                           "manager_host_ip_3":entry[7],
                                           "subnet1":entry[8],
                                           "subnet2":entry[9],
                                           "subnet3":entry[10]}
                            result = config()                       # CONFIG FUNCTIONS FIRES -> ROUTER CONFIG COMMENCES
                            analyseResults(result)                  # analyses results to see whether successful/not
                            if result == False:
                                break

                        total_elapsed_time = time.time() - total_start_time
                        print("\nTotal elapsed time: {:.2f}s".format(total_elapsed_time))
                        
                else:
                    print("\nBad router config detected. Please review these and replace file:\n")
                    for router in validate_out:
                        print (router)
                    print("\n\n")
                
            except IndexError:
                print("\ninvalid file")
                pass
        
    else:
        print("\nInvalid Option")

# EXAMPLE INPUT LAYOUT:
#
# IP:                   192.168.100.4
# PORT:                 443
# USERNAME:             admin
# PASSWORD:             admin                   N.B if administrator password remains default, alert box appears when running the program which causes a break
# 
# MANAGER HOST IP 1:    192.168.100.58
# MANAGER HOST IP 1:    233.155.52.55
# MANAGER HOST IP 1:    218.4.0.39
# SUBNET 1:             24                      N.B subnet value must be between 22 < n < 32
# SUBNET 2:             32
# SUBNET 3:             31
#
# NOTE: This program directly accesses an https:// page.
#       You can change this in the code above.
# When uploading csv file, input data in rows as follow:
#
# IP ADDRESS, PORT, USERNAME, PASSWORD, SET COMMUNITY, SNMP HOST 1, SNMP HOST 2, SNMP HOST 3, SUBNET 1, SUBNET 2, SUBNET 3
#
#


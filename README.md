# Draytek-Web-Auto-Configuration

[TODO] ADD Introduction
This programme will automate the process to log into  DrayTek routers and fill in desired SNMP configurations.

## Requirements
[TODO] Add Intro to requirements
- This was written in python 3.7
- Python 3.x
- Python binding for [Selenium](https://pypi.org/project/selenium/)

Supported Browsers:

- Chrome - requires [ChromeDriver](http://chromedriver.chromium.org/)
- Firefox - requires [GeckoDriver](https://github.com/mozilla/geckodriver/releases)

To install requirements: `pip install -r requirements.txt`

## Usage

- Is for use with the DrayTek Vigor2860Ln router.
- Can be used with a manual input or an imported csv file.

- **Manual input**:

	- IP:                 192.168.100.4
	- PORT:               443
	- USERNAME:           admin
	- PASSWORD:           admin                   _N.B if administrator password remains default, alert box appears when running the                                                       program which causes a break_
	- SET COMMUNITY:    	highlight
	- SNMP HOST IP 1:    	192.168.100.58
	- SNMP HOST IP 1:   	233.155.52.55
	- SNMP HOST IP 1:   	218.4.0.39
	- SUBNET 1:           24                      _N.B subnet value must be between 22 < n < 32_
	- SUBNET 2:           32
	- SUBNET 3:           31

- **CSV file input**:
	
	- Select a CSV file with pre-recorded data on it
	- Each row accounts for a separate router
	- Each row must follow format:
		
	IP ADDRESS, PORT, USERNAME, PASSWORD, SET_COMMUNITY_STRING, SNMP_HOST_IP_1, SNMP_HOST_IP_2, SNMP_HOST_IP_3, SUBNET_1, SUBNET_2,         SUBNET_3

	e.g.  192.168.42.57, admin, admin, highlight, 240.14.44.105, 179.44.100.57, 212.33.4.156, 24, 23, 32	

## Examples

[TODO]

## Contributors

- Jackie Zhang
- Anish Goel

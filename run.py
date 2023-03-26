from APSpaceAttendance import *
import requests

print("# APSpace Attendance Automation v1 #")
print("Press ENTER to start the program")
check = input("Press C and Enter to terminate")

if check == "c":
    print("Stopping...")
    exit()

casUrl = f'https://cas.apiit.edu.my/cas/v1/tickets?username={apkey}&password={apkey_password}'
headers = {'Content-Type': 'application/x-www-form-urlencoded'}

x = requests.post(casUrl, headers=headers)

if x.status_code == 401:
    print("Log in to APSpace failed! Check config.ini or network connection!")
    exit()

soup = BeautifulSoup(x.text, 'html.parser')

tgt = soup.find('form').get('action')

# CAS TGT #
service = 'https://api.apiit.edu.my/student/profile'
headers = {'Content-Type': 'application/x-www-form-urlencoded'}
tgtUrl = tgt + f"?service={service}"

serviceTicket = requests.post(tgtUrl, headers=headers)

profile = f'https://api.apiit.edu.my/student/profile?ticket={serviceTicket.text}'

getProfile = requests.get(profile, headers=headers)
response = json.loads(getProfile.text)
student_id = response['STUDENT_NUMBER']
student_name = response['NAME']
print("\n")
print(f"Logged in as {student_name} ({student_id})")
print("\n")
run = APSpaceAttendance()


# AttendanceUpdater

A automation script to automatically scan and update attendance. The program is purely for educational purposes and real usage is not recommended.

UPDATE:: Great times, great times, great times! A love and hate relationship with the pandemic, the word 'front-liners' were being used almost everyday so was students with the word 'attendance' through their speakers. We are now hearing the word through our ears now, times have changed! Uh, although we hear it occasionally now and then still through our speakers... meh!


## Prerequisites

Install dependencies.

```python
pip install -r requirements.txt
```
or
```python
pip3 install -r requirements.txt
```

Add your credentials in config.ini.

```json
[APKEY]
ID: tp000000
Password: Tp000000@1234
```


## Usage

Run the program and follow the onscreen instructions.

```bash
py run.py
```
or
```bash
python3 run.py
```
## How to Use

The programs needs to be running and Microsoft Teams needs to be open and visible in the foreground. 
The program will not detect the attendance QR if Microsoft Teams is minimised or hidden behind other application.

#### Disable timeout or sleep
Disable screen timeouts or sleep due to inactivity because the script will stop working if the computer goes to sleep or hibernation.

#### Increased Battery Consumption
Setting a lower RETRY_INTERVAL in config.ini may increase battery and memory consumption and plugging in is recommended if applicable.


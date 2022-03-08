import os
import sys
import codecs
import time
import traceback
import datetime as dt

import win32api #this is used to get the current user , the current time and the total time workded.
import win32file
import win32profile
import win32gui
import win32evtlog
import win32con
import win32evtlogutil
import winerror

FILEPATH = f'{win32profile.GetProfilesDirectory()}\\{win32api.GetUserName()}\\Desktop\\systemadmin.txt'

def check_file_exists():
    '''Checks Wether the File Exists or Not if not then creates the file using win32file'''
    if(not win32file.FindFilesW(FILEPATH)):
        win32file.CreateFile(FILEPATH, win32file.GENERIC_WRITE, win32file.FILE_SHARE_WRITE, None, 2, 0, 0)

    if(not os.path.isdir('C:\\logs')):
        os.mkdir('C:\\logs')
    
def write_to_file(inp):
    with open(FILEPATH,'a') as file:
        file.write(inp)

def get_date():
    wdate = win32api.GetSystemTime()
    date = f'{wdate[1]}-{wdate[3]}-{wdate[0]}'
    return date

def get_time_worked():
    time_ms = win32api.GetTickCount()
    time_min = (time_ms/(1000*60))%60
    time_hr = (time_ms/(1000*60*60))%24
    return f'{int(time_hr)} Hours and {int(time_min)} Minutes'

def window_message():
    win32gui.MessageBeep(1)
    message = f'Your Attendance Has Been Marked For Today! Updated Info stored at {FILEPATH} and System Application Logs at C:\logs'
    win32gui.MessageBox(0,message,'System Administrator',0)

def getAllEvents(server, logtypes, basePath):
    if not server:
        serverName = "localhost"
    else: 
        serverName = server
    for logtype in logtypes:
        path = os.path.join(basePath, f"{serverName}_{logtype}_log")
        getEventLogs(server, logtype, path)

def getEventLogs(server, logtype, logPath):
    """
    Get the event logs from the specified machine according to the
    logtype (Example: Application) and save it to the appropriately
    named log file
    """
    logPath=f"{logPath}-{dt.date.today()}.log"
    print(f"Logging {logtype} events")
    log = codecs.open(logPath, encoding='utf-8', mode='w')
    line_break = '-' * 80
    
    log.write(f"\n{server} Log of {logtype} Events\n")
    log.write(f"Created: {time.ctime()}\n\n")
    log.write("\n" + line_break + "\n")
    hand = win32evtlog.OpenEventLog(server,logtype)
    total = win32evtlog.GetNumberOfEventLogRecords(hand)
    print(f"Total events in {logtype} = {total}")
    flags = win32evtlog.EVENTLOG_BACKWARDS_READ|win32evtlog.EVENTLOG_SEQUENTIAL_READ
    events = win32evtlog.ReadEventLog(hand,flags,0)
    evt_dict={win32con.EVENTLOG_AUDIT_FAILURE:'EVENTLOG_AUDIT_FAILURE',
              win32con.EVENTLOG_AUDIT_SUCCESS:'EVENTLOG_AUDIT_SUCCESS',
              win32con.EVENTLOG_INFORMATION_TYPE:'EVENTLOG_INFORMATION_TYPE',
              win32con.EVENTLOG_WARNING_TYPE:'EVENTLOG_WARNING_TYPE',
              win32con.EVENTLOG_ERROR_TYPE:'EVENTLOG_ERROR_TYPE'}
    
    try:
        events=1
        while events:
            events=win32evtlog.ReadEventLog(hand,flags,0)
        
            for ev_obj in events:
                the_time = ev_obj.TimeGenerated.Format() 
                evt_id = str(winerror.HRESULT_CODE(ev_obj.EventID))
                record = ev_obj.RecordNumber
                msg = win32evtlogutil.SafeFormatMessage(ev_obj, logtype)
                
                source = str(ev_obj.SourceName)
                if not ev_obj.EventType in list(evt_dict.keys()):
                    evt_type = "unknown"
                else:
                    evt_type = str(evt_dict[ev_obj.EventType])
                log.write(f"Event Date/Time: {the_time}\n")
                log.write(f"Event ID / Type: {evt_id} / {evt_type}\n")
                log.write(f"Record #{record}\n")
                log.write(f"Source: {source}\n\n")
                log.write(msg)
                log.write("\n\n")
                log.write(line_break)
                log.write("\n\n")
    except:
        print(traceback.print_exc(sys.exc_info()))
                
    print(f"Log creation finished. Location of log is {logPath}")

def main():
    check_file_exists()
    username = win32api.GetUserName()
    machine_name = win32api.GetComputerName()
    today_date = get_date()
    worked_hours = get_time_worked()
    system_info = win32api.GetSystemInfo()

    template = f'For Day : {today_date}\nMachine Name : {machine_name} \nUser Name : {username} \nWorked Hours : {worked_hours} \nSystem Info : {system_info}'
    write_to_file(template)
    write_to_file('\n\n')

    server = None 
    logTypes = ["System", "Application"]
    getAllEvents(server, logTypes, "C:\logs")
    window_message()

if  __name__ == '__main__':
    main()
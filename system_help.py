import sys
import ctypes
import win32api #this is used to get the current user , the current time and the total time workded.
import win32file
import win32profile
import win32security
import win32gui

FILEPATH = f'{win32profile.GetProfilesDirectory()}\\{win32api.GetUserName()}\\Desktop\\systemadmin.txt'

def check_file_exists():
    '''Checks Wether the File Exists or Not if not then creates the file using win32file'''
    if(not win32file.FindFilesW(FILEPATH)):
        win32file.CreateFile(FILEPATH,win32file.GENERIC_WRITE,win32file.FILE_SHARE_WRITE,None,2,0,0)

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

def get_SIK():
    info = (win32security.GetFileSecurity(FILEPATH),win32security.OWNER_SECURITY_INFORMATION)
    return info.GetSecurityDescriptorOwner()

def window_message():
    win32gui.MessageBeep(1)
    message = f'Your Attendance Has Been Marked For Today! Updated Info stored at {FILEPATH}'
    win32gui.MessageBox(0,message,'System Administrator',0)

def main():
    check_file_exists()
    username = win32api.GetUserName()
    machine_name = win32api.GetComputerName()
    today_date = get_date()
    worked_hours = get_time_worked()
    system_info = win32api.GetSystemInfo()
    sik = get_SIK()
    #sik = None

    template = f'For Day : {today_date}\nMachine Name : {machine_name} \nUser Name : {username} \nWorked Hours : {worked_hours} \nSystem Info : {system_info} \nSecuriy Identification Key : {sik}'
    write_to_file(template)
    write_to_file('\n\n')
    window_message()

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if __name__ == '__main__':
    if is_admin():
        main()
    else:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)

# if  __name__ == '__main__':
#     main()
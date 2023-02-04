import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
import numpy as np
import sys
import os
import re
import time


#RegData (BQ2429x)
InputCurrName=['100', '150', '500', '900', '1000', '1500', '2000', '3000']
ChargingStatus=["Not Charging", "Pre-charge", "Fast Charging", "Charge Termination Done"]


class battery_parser:
    def __init__(self):
        if len(sys.argv) < 2:
            print ("No filename, exit")
            sys.exit(0)
        self.filename=sys.argv[1]

        self.RawFile="RawData.log"
        self.extFile=""
        self.dataFile=""
        #healthdData
        self.capa=[]
        self.volt=[]
        self.temp=[]
        self.curr=[]
        self.fcc=[]
        self.rc=[]
        self.cc=[]
        self.chrg=[]
        self.basetime=0
        self.time=[]

        #regData
        self.ChgLimitCurr=[]
        self.ChgEnable=[]
        self.Charging=[]
        self.ChgStatus=[]
        self.RegTime=[]

        #Qi issue
        self.QiBroken=[]

        #Picture Display
        self.show=False

    def getTime(self, line):
        pattern="\[(\d+\/\d+\/\d+ \d+:\d+:\d+)\]"
        match=re.search(pattern,line)
        if(match):
            if self.basetime == 0:
                self.basetime = int(time.mktime(time.strptime(match.group(1), "%m/%d/%y %H:%M:%S")))
            else:
                return int(time.mktime(time.strptime(match.group(1), "%m/%d/%y %H:%M:%S"))) - self.basetime
        else:
            return None

    def logunzip(self):
        curDir=os.path.dirname(os.path.abspath(__file__))
        fname = self.filename.split('.')
        pre_pass = re.split(r"_",fname[0])
        passwd=pre_pass[len(pre_pass)-2] + '_' + pre_pass[len(pre_pass)-1]
        extDir=curDir + '/' + passwd

        #if extract directory exist, we assume we have do before just skip.
        if(os.path.isdir(extDir)):
            subDir_t=os.listdir(path=extDir)
            subDir=os.path.join(extDir, subDir_t[0])

            chdDir=os.listdir(path=subDir)
            for filep in chdDir:
                if filep == 'Kernel' or filep == 'SaioLog':
                    tarDir=os.path.join(subDir, filep)
                    self.extFile = tarDir
                    break
            print(extDir + ' exist skip')
            return

        command = '7z x ' + self.filename + ' -p' + passwd + ' -o' + extDir + ' -y > /dev/null'
        os.system(command)

        subDir_t=os.listdir(path=extDir)
        subDir=os.path.join(extDir, subDir_t[0])

        chdDir=os.listdir(path=subDir)
        for filep in chdDir:
            if filep == 'Kernel' or filep == 'SaioLog':
                tarDir=os.path.join(subDir, filep)
                self.extFile = tarDir

                #list file and sort
                files = os.listdir(path=tarDir)
                #remove other files cuz sort report error
                files = [ item for item in files if '.log' not in item ]

                files.sort(key=lambda x: int(x.split('_')[1]))

                for extFile_t in files:
                    extFile=os.path.join(tarDir, extFile_t)
                    if '.gz' in extFile:
                        command = '7z x ' + extFile + ' -o' + tarDir + ' -y > /dev/null'
                        os.system(command)
                break
        print("1.Extract " + self.filename + " done.\n\t and Go to " + tarDir)

    def healthData(self, line):
        #use '()' to group
        #if this line do not contain this pattern its index is the same as the line that's having this pattern but the contain will show "None"
        pattern="(l=(\d+)) (v=(\d+)) (t=(\d+.\d+)) (h=(\d)) (st=(\d)) (c=([-]?\d+)) (fc=(\d+) ){0,1}(rc=(\d+) ){0,1}(cc=(\d+) ){0,1}(chg=([uaw]?)) (\d+-\d+-\d+ \d+:\d+:\d+).\d+"
        match=re.search(pattern,line)
        if(match):
            logTime = self.getTime(line)
            if self.basetime != 0:
                if logTime == None:
                    return
                else:
                    self.time.append(logTime) #Timestamp

            #Note: plotting needs a number not  string
            self.capa.append(int(match.group(2)))       #Soc
            self.volt.append(float(match.group(4))/1000)     #Voltage
            self.temp.append(round(float(match.group(6))))     #Temperature
            self.curr.append(float(match.group(12))/1000)      #Current

            if(match.group(14) != None):
                self.fcc.append(int(match.group(14)))
                self.rc.append(int(match.group(16)))
                self.cc.append(int(match.group(18)))
            chrg = match.group(20)
            if(chrg != ''):
                self.chrg.append(1)
            else:
                self.chrg.append(0)

    def regData(self, line):
        pattern="((0x\S+)[ ]*)"
        #findall returns a list of matching strings
        #match index is equal reg index. for example:match[0] = Reg00
        match=re.findall(pattern,line)
        if(match):
            logTime = self.getTime(line)
            if self.basetime != 0:
                if logTime == None:
                    return
                else:
                    self.RegTime.append(logTime) #Timestamp

            InputCurrIdx = int((match[0])[1],0) & 0x7
            self.ChgLimitCurr.append(InputCurrIdx)

            charging=(int((match[8])[1],0) & 0x30) >> 4
            self.Charging.append(charging)

            enable=(int((match[1])[1],0) & 0x10)>>4
            self.ChgEnable.append(enable)

            #if(charging == 0 and enable == 1):
            #    print ("Not Charging", charging,enable)
            #    print (line)

            status=int((match[9])[1],0) & 0xFF
            if status != 0:
                self.ChgStatus.append(1)
            else:
                self.ChgStatus.append(0)

    def qiBroken(self, line):
        pattern="\[(\d+\/\d+\/\d+ \d+:\d+:\d+)\]"
        match=re.search(pattern,line)
        if(match):
            QiBrokentime = int(time.mktime(time.strptime(match.group(1), "%m/%d/%y %H:%M:%S")))
            self.QiBroken.append([QiBrokentime - self.basetime, 1])

    def SocPlot(self, ax):
        x=self.time
        y=self.capa
        if len(self.time) == 0:
            soc = ax.plot(y, 'b:', label="SOC")
        else:
            soc = ax.plot(x, y, 'b:', label="SOC")
        ax.set_yticks(np.arange(0, 105, 5))
        ax.set_yticklabels(np.arange(0, 105, 5))
        ax.tick_params(axis='y', labelcolor='blue')
        ax.set_ylabel("Percentage (%)/Temp ($^\circ$C)", color='blue')
        return soc

    def ChargingPlot(self, ax):
        x=self.time
        y=self.chrg
        if len(self.time) == 0:
            chrgEn = ax.plot(y, 'b', label="Charging? (Y=1/N=0)")
        else:
            chrgEn = ax.plot(x, y, 'b', label="Charging? (Y=1/N=0)")
        return chrgEn

    def TempPlot(self, ax):
        x=self.time
        y=self.temp

        if len(x) == 0:
            temperature = ax.plot(y, 'b.', label="Temp")
        else:
            temperature = ax.plot(x, y, 'b.', label="Temp")
        #ax.set_yticks(np.arange(-20, 105, 5))
        #ax.set_yticklabels(np.arange(-20, 105, 5))
        #ax.tick_params(axis='y', labelcolor='red')
        #ax.set_ylabel("Temp ($^\circ$C)", color='red')
        return temperature

    def CurrPlot(self, ax):
        x=self.time
        y=self.curr

        if len(x) == 0:
            current = ax.plot(y, 'r.', label="Current")
        else:
            current = ax.plot(x, y, 'r.', label="Current")
        ax.axhline(y=0, c='k')
        ax.axhline(y=3.0, c='k')
        ax.set_yticks(np.arange(-1, 4.3, 0.2))
        ax.set_yticklabels(np.arange(-1, 4.3, 0.2))
        ax.tick_params(axis='y', labelcolor='red')
        ax.set_ylabel("Current (A)/Voltage (volt)", color='red')
        return current

    def VoltPlot(self, ax):
        x=self.time
        y=self.volt

        if len(x) == 0:
            volt = ax.plot(y, 'r:', label="Voltage")
        else:
            volt = ax.plot(x, y, 'r:', label="Voltage")
        ax.tick_params(axis='y', labelcolor='r')
        ax.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
        return volt

    def QiBrokenPlot(self, ax):
        x=[]
        y=[]
        for i in range(len(self.QiBroken)):
            x.append(self.QiBroken[i][0])
            y.append(self.QiBroken[i][1])
        p=ax.plot(x,y,'g*', label="Qi Broken point")
        return p

    def HealthdPlot(self):
        fig=plt.figure()
        ax1=fig.add_subplot(111)
        plt.title("Health Information")
        plt.grid()

        #SOC
        soc=self.SocPlot(ax1)
        x=self.time

        #Charging Status
        chrg=self.ChargingPlot(ax1)

        #Temp
        temp=self.TempPlot(ax1)

        #using diffenent y axis
        ax2=plt.twinx()
        curr=self.CurrPlot(ax2)
        volt=self.VoltPlot(ax2)

        if(len(self.QiBroken) != 0):
            qi=self.QiBrokenPlot(ax1)
            lns=soc+chrg+curr+volt+qi
        else:
            lns=soc+chrg+curr+volt

        #put all labels in one legend
        labs = [l.get_label() for l in lns]
        ax1.legend(lns, labs, loc='center right')

        fig.savefig('HealthdPlot.pdf')
        self.show=True

    def RegPlot(self):
        if(len(self.ChgLimitCurr) == 0):
            print("Log file is not contain register information.")
        else:
            fig=plt.figure()
            ax1=fig.add_subplot(111)
            plt.title("BQ24296/BQ24297 Register")
            plt.grid()

            #xAxis=np.arange(0, len(self.ChgLimitCurr))
            xAxis=self.RegTime
            yAxis=self.ChgLimitCurr
            reg01 = ax1.plot(xAxis,yAxis,'b:',label="Input Limit Current (Reg01)")
            ax1.set_yticks(np.arange(0, len(InputCurrName), 1))
            ax1.set_yticklabels(InputCurrName)
            ax1.tick_params(axis='y', labelcolor='blue')
            ax1.set_ylabel("Current (mA)", color='blue')

            #Share x axis
            ax2=plt.twinx()
            #x=np.arange(0, len(self.Charging))
            x=self.RegTime
            y=self.Charging
            reg08 = ax2.plot(x,y,'rd',label="Charging Status (Reg08)")
            ax2.set_yticks(np.arange(0, len(ChargingStatus), 1))
            ax2.set_yticklabels(ChargingStatus)
            ax2.tick_params(axis='y', labelcolor='red')


            if(len(self.QiBroken) != 0):
                qi = self.QiBrokenPlot(ax1)
                lns = reg01+reg08+qi
            else:
                lns = reg01+reg08

            #put all labels in one legend
            labs = [l.get_label() for l in lns]
            ax1.legend(lns, labs, loc='center right')
            fig.savefig('ChargerReg.pdf')
            self.show = True

#(0x\S+){1,11}[ ]+,(0x\S+){1,11}[ ]+,(0x\S+){1,11}[ ]+,(0x\S+){1,11}[ ]+,(0x\S+){1,11}[ ]+,(0x\S+){1,11}[ ]+,(0x\S+){1,11}[ ]+,(0x\S+){1,11}[ ]+,(0x\S+){1,11}[ ]+,(0x\S+){1,11}[ ]+,(0x\S+)

def keywdFilter(bat, keywd, DumpFile):
    files = os.listdir(path=bat.extFile)
    files = [ item for item in files if '.log' not in item ]
    files.sort(key=lambda x: int(x.split('_')[1]))

    DumpFile = os.path.join(bat.extFile, DumpFile)
    wfd = open(DumpFile, 'w+')

    for log_t in files:
        log=os.path.join(bat.extFile, log_t)
        if '.gz' not in log:
            fd=open(log, 'r', encoding='utf-8', errors='ignore')
            for line in fd:
                for key in keywd:
                    if key in line:
                        wfd.write(line)
            fd.close()
    wfd.close()
    bat.dataFile = DumpFile;
    print('2.Filter keyword ' + str(keywd) + ' done.')

def dataCollect(bat, pat):
    datafd=open(bat.dataFile, 'r', encoding='utf-8', errors='ignore')

    for line in datafd:
        if(bat.basetime == 0):
            bat.getTime(line)
        for key in pat:
            if key in line:
                if key == 'healthd':
                    bat.healthData(line)
                    bat.regData(line)
                elif key == 'Qi Remove':
                    bat.qiBroken(line)
    datafd.close()

def debug(bat):
    print(bat.volt)

if __name__ == '__main__':
    bat=battery_parser()
    bat.logunzip()

    pat=['healthd', 'bq2429x-charger', 'bq2429x power', 'BATTERY_CHANGED', 'FG_CW221X', 'Qi Remove']
    keywdFilter(bat, pat, bat.RawFile)

    dataCollect(bat, pat)
    #debug(bat)
    bat.HealthdPlot()
    bat.RegPlot()

    if(bat.show):
        plt.show()

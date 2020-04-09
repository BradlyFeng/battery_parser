import matplotlib.pyplot as plt
import numpy as np
import sys 

a64_pattern_list=['charger->vbat', 'charger->ibat', 'charger->ocv', 'AxpOCV_percentage','AxpCoulumb_percentage', 'charger->new_capacity', 'charger->full_charging','charger->rest_vol']

sc20_pattern_list=['calculated_soc', 'last_soc', 'bat_uv', 'last_ocv_uv','ocv_at_100','current_now']
time_vbat_list=[]
time_ibat_list=[]
time_ocv_list=[]
time_ocvp_list=[]
time_coulp_list=[]
time_reprtp_list=[]

vbat_list=[] #bat_uv_list
ibat_list=[]
ibat_start_list=[]
ibat_low_list=[]
ocv_list=[] # ocv_uv_list
ocv_percentage_list=[]
coul_percentage_list=[]
reprt_percentage_list=[] #lstsoc_list

#sc20 list
calsoc_list=[]
result_list=[]

ocvp_100=[]
batp_100=[]

percentage_bat_range=[]
percentage_ocv_range=[]

start=False

d={'a':"A64","s":"SC20","c":"Charging","d":"Discharging","r":"Range"}
#for i in range(len(coul_percentage_list)):
#    if 10 ==coul_percentage_list[i]:
#        time_to_10=i
#        break

class battery_parser:
    def __init__(self):
        if len(sys.argv) < 4:
            print 'Enter [a/s](platform:a64/sc20), [c/d](charge/discharge), [filename]'
            sys.exit(0)
        self.platform=sys.argv[1]
        self.mode=sys.argv[2]
        self.filename=sys.argv[3]
        self.fd=open(self.filename)
        self.time_to_100=0
        print("Platform = " + d[self.platform] + "\nDiagram = " + d[self.mode] + "\nFile = " + self.filename)

    def sc20_parser(self):
        result_list=[]

        for line in self.fd:
            line=line.replace('\t','')
            line=line.replace('\n','')
            ret=line.find('=')
            if ret < 0:
                continue
            else:
                a=line.split('=')
                if a[0] == "ocv_at_100" or a[0] == "low_voltage_ws_active" or a[0] == "cv_ws_active" :
                    #start=False
                    continue
                res=[i for i in sc20_pattern_list if a[0] in i]
                if len(res)==0:
                    continue
                if a[0] == sc20_pattern_list[0]:
                    if len(result_list) == 5:
                        calsoc_list.append(result_list[0])
                        reprt_percentage_list.append(result_list[1])
                        vbat_list.append(result_list[2])
                        ocv_list.append(result_list[3])
                        ibat_list.append(result_list[4])
                    result_list = []
                    #start=True
                    h_flag=False
                ret=line.find('[')
                if ret > 0:
                    h_flag=True
                    continue
                #if h_flag and start:
                #    continue
                #result_list.append(int(a[1]))
                if a[0] == sc20_pattern_list[0]:
                    result_list.append(int(a[1]))
                elif a[0] == sc20_pattern_list[1]:
                    result_list.append(int(a[1]))
                elif a[0] == sc20_pattern_list[2]:
                    result_list.append(int(a[1]))
                elif a[0] == sc20_pattern_list[3]:
                    result_list.append(int(a[1]))
                elif a[0] == sc20_pattern_list[5]:
                    result_list.append(int(a[1]))
                else:
                    continue
        for i in range(len(reprt_percentage_list)):
            if 100 ==reprt_percentage_list[i]:
                self.time_to_100=i
                break

    def a64_parser(self):
        for line in self.fd:
            line=line.replace('\t','')
            line=line.replace('\n','')
            line=line.replace(' ','')
            ret=line.find('=')
            time_start=line.find('[')
            time_end=line.find('.')
            symbol_end=line.find(']')
            t=line[time_start+1:time_end]
            line=line[symbol_end+1:]
            if ret < 0:
                continue
            else:
                a=line.split('=')
                res=[i for i in a64_pattern_list if a[0] in i]
                if len(res)==0:
                    continue
                else:
                    if a[0] == a64_pattern_list[0]:
                        vbat_list.append(int(a[1]))
                        time_vbat_list.append(int(t))
                    elif a[0] == a64_pattern_list[1]:
                        if int(a[1]) <= 0:
                            ibat_list.append(0)
                        else:
                            ibat_list.append(int(a[1]))
                        time_ibat_list.append(int(t))
                    elif a[0] == a64_pattern_list[2]:
                        ocv_list.append(int(a[1]))
                        time_ocv_list.append(int(t))
                    elif a[0] == a64_pattern_list[3]:
                        ocv_percentage_list.append(int(a[1]))
                        time_ocvp_list.append(int(t))
                    elif a[0] == a64_pattern_list[4]:
                        coul_percentage_list.append(int(a[1]))
                        time_coulp_list.append(int(t))
                    elif a[0] == a64_pattern_list[7]:
                        reprt_percentage_list.append(int(a[1]))
                        time_reprtp_list.append(int(t))
                    else:
                        continue
        for i in range(len(coul_percentage_list)):
            if 100 == coul_percentage_list[i]:
                self.time_to_100=i
                break
    def range_plot(self):
        if(self.platform == 'a'):
            self.a64_range_plot()
        elif bat.platform == 's':
            bat.sc20_range_plot()

    def sc20_range_plot(self):
        for i in range(len(reprt_percentage_list)):
            if 100 == reprt_percentage_list[i]:
                ocvp_100.append(ocv_list[i])
                batp_100.append(vbat_list[i])
        plt.title( self.filename + '\n' "range of voltage when 100%")

        #Get the current peak
        for i in range(len(ibat_list)):
            if ibat_list[i] != 0:
                if (i > 0):
                    if(ibat_list[i-1] == 0):
                        if i < 1000:
                            continue
                        ibat_start_list.append(i)
                        ibat_low_list.append(i-1)
                        #print (ibat_list[i],i)

        #vbat plot
        batp_100.sort()
        xbat = np.arange(0,len(batp_100))
        ybat = batp_100
        plt.ylabel("mv")
        plt.plot(xbat,ybat,'b',label="vbat range")
        plt.annotate('(bat min=%smv)' % (batp_100[0]), xy=(0,batp_100[0]), xycoords='data', xytext=(+30, -30),
                     textcoords='offset points', fontsize=16,
                     arrowprops=dict(arrowstyle='->', connectionstyle="arc3,rad=.2"))
        plt.annotate('(bat max=%smv)' % (batp_100[len(batp_100)-1]),
                     xy=(len(batp_100),batp_100[len(batp_100)-1]), xycoords='data', xytext=(+30, -30),
                     textcoords='offset points', fontsize=16,
                     arrowprops=dict(arrowstyle='->', connectionstyle="arc3,rad=.2"))

        # ocv plot
        ocv_100_len = len(ocvp_100)
        ocvp_100.sort()
        xocv = np.arange(0,len(ocvp_100))
        yocv = ocvp_100
        plt.plot(xocv,yocv,'r',label="ocv range")
        plt.plot(xbat,ybat)
        plt.annotate('(ocv min=%smv)' % (ocvp_100[0]), xy=(0,ocvp_100[0]), xycoords='data', xytext=(+30, -30),
                     textcoords='offset points', fontsize=16,
                     arrowprops=dict(arrowstyle='->', connectionstyle="arc3,rad=.2"))
        plt.annotate('(ocv max=%smv)' % (ocvp_100[len(ocvp_100)-1]),
                     xy=(len(ocvp_100),ocvp_100[len(ocvp_100)-1]), xycoords='data', xytext=(+30, -30),
                     textcoords='offset points', fontsize=16,
                     arrowprops=dict(arrowstyle='->', connectionstyle="arc3,rad=.2"))
        plt.legend(loc='best')

    def a64_range_plot(self):
        # find the range of bat and ocv voltage between 100%
        for i in range(len(coul_percentage_list)):
            if 100 == coul_percentage_list[i]:
                percentage_bat_range.append(vbat_list[i])
                percentage_ocv_range.append(ocv_list[i])
                ocvp_100.append(time_ocv_list[i])
                batp_100.append(time_vbat_list[i])
        plt.title( self.filename + '\n' "range of voltage when 100%")

        #vbat plot
        bat_100_len = len(percentage_bat_range)
        percentage_bat_range.sort()
        xbat = np.arange(0,len(percentage_bat_range))
        ybat = percentage_bat_range
        plt.ylabel("mv")
        plt.plot(xbat,ybat,'b',label="vbat range")
        plt.annotate('(bat min=%smv)' % (percentage_bat_range[0]), xy=(0,percentage_bat_range[0]), xycoords='data', xytext=(+30, -30),
                     textcoords='offset points', fontsize=16,
                     arrowprops=dict(arrowstyle='->', connectionstyle="arc3,rad=.2"))
        plt.annotate('(bat max=%smv)' % (percentage_bat_range[len(percentage_bat_range)-1]),
                     xy=(len(percentage_bat_range),percentage_bat_range[len(percentage_bat_range)-1]), xycoords='data', xytext=(+30, -30),
                     textcoords='offset points', fontsize=16,
                     arrowprops=dict(arrowstyle='->', connectionstyle="arc3,rad=.2"))

        #ocv plot
        ocv_100_len = len(percentage_ocv_range)
        percentage_ocv_range.sort()
        xocv = np.arange(0,len(percentage_ocv_range))
        yocv = percentage_ocv_range
        plt.plot(xocv,yocv,'r',label="ocv range")
        plt.annotate('(ocv min=%smv)' % (percentage_ocv_range[0]), xy=(0,percentage_ocv_range[0]), xycoords='data', xytext=(+30, -30),
                     textcoords='offset points', fontsize=16,
                     arrowprops=dict(arrowstyle='->', connectionstyle="arc3,rad=.2"))
        plt.annotate('(ocv max=%smv)' % (percentage_ocv_range[len(percentage_ocv_range)-1]),
                     xy=(len(percentage_ocv_range),percentage_ocv_range[len(percentage_ocv_range)-1]), xycoords='data', xytext=(+30, -30),
                     textcoords='offset points', fontsize=16,
                     arrowprops=dict(arrowstyle='->', connectionstyle="arc3,rad=.2"))
        plt.legend(loc='best')

    def charge_plot(self):
        if(self.platform == 'a'):
            self.a64_charge_plot()
        elif bat.platform == 's':
            bat.sc20_charge_plot()

    def sc20_charge_plot(self):
        plt.subplot(211)
        self.discharge_plot()
        plt.title(self.filename + '\n' "Charging")
        '''
        '''
        #vbat v.s ocv
        x_bat = np.arange(0,len(vbat_list))
        y_bat = vbat_list

        x_ocv = np.arange(0,len(ocv_list))
        y_ocv = ocv_list
        plt.subplot(212)
        plt.ylabel("voltage")
        plt.plot(x_bat,y_bat,label="Bat uv")
        plt.plot(x_ocv,y_ocv,label="OCV uv")
        plt.grid()
        plt.legend(loc='best')

        plt.annotate('(%ss, vbat=%s uV)' % (self.time_to_100,vbat_list[self.time_to_100]), xy=(self.time_to_100,vbat_list[self.time_to_100]),
                     xycoords='data', xytext=(+30, -30),
                     textcoords='offset points', fontsize=16,
                     arrowprops=dict(arrowstyle='->', connectionstyle="arc3,rad=.2"))
        plt.annotate('(%ss, ocv=%s uV)' % (self.time_to_100,ocv_list[self.time_to_100]), xy=(self.time_to_100,ocv_list[self.time_to_100]),
                     xycoords='data', xytext=(+80, -80),
                     textcoords='offset points', fontsize=16,
                     arrowprops=dict(arrowstyle='->', connectionstyle="arc3,rad=.2"))
        for i in range(len(ibat_start_list)):
            plt.annotate('(%ss, vbat=%smV)' % (ibat_start_list[i],vbat_list[ibat_start_list[i]]),
                         xy=(ibat_start_list[i],vbat_list[ibat_start_list[i]]), xycoords='data', xytext=(-50, +20),
                         textcoords='offset points', fontsize=16,
                         arrowprops=dict(arrowstyle='->', connectionstyle="arc3,rad=.2"))
        for i in range(len(ibat_low_list)):
            plt.annotate('(%ss, ocv=%smV)' % (ibat_low_list[i],ocv_list[ibat_low_list[i]]),
                         xy=(ibat_low_list[i],ocv_list[ibat_low_list[i]]), xycoords='data', xytext=(+30, -100),
                         textcoords='offset points', fontsize=16,
                         arrowprops=dict(arrowstyle='->', connectionstyle="arc3,rad=.2"))

    def a64_charge_plot(self):
        plt.subplot(211)
        self.discharge_plot()
        plt.title( self.filename + '\n' "Charging")

        #Get the current peak
        for i in range(len(ibat_list)):
            if ibat_list[i] != 0:
                if (i > 0):
                    if(ibat_list[i-1] == 0):
                        if i < 1000:
                            continue
                        ibat_start_list.append(i)
                        ibat_low_list.append(i-1)
                        #print (ibat_list[i],i)

        #vbat v.s ocv
        x_time = time_vbat_list
        y_vbat = vbat_list

        y_ocv = ocv_list
        plt.subplot(212)
        plt.ylabel("voltage")
        plt.plot(x_time,y_vbat,label="Bat mv")
        plt.plot(x_time,y_ocv,label="OCV mv")
        plt.grid()
        plt.legend(loc='upper right')
        if(self.time_to_100 != 0):
            plt.annotate('(%ss, vbat=%smV)' % (time_vbat_list[self.time_to_100],vbat_list[self.time_to_100]),
                         xy=(time_vbat_list[self.time_to_100],vbat_list[self.time_to_100]), xycoords='data', xytext=(+30, -50),
                         textcoords='offset points', fontsize=16,
                         arrowprops=dict(arrowstyle='->', connectionstyle="arc3,rad=.2"))
        for i in range(len(ibat_low_list)):
            plt.annotate('(%ss, vbat=%smV)' % (time_vbat_list[ibat_low_list[i]],vbat_list[ibat_low_list[i]]),
                         xy=(time_vbat_list[ibat_low_list[i]],vbat_list[ibat_low_list[i]]), xycoords='data', xytext=(+30, -30),
                         textcoords='offset points', fontsize=16,
                         arrowprops=dict(arrowstyle='->', connectionstyle="arc3,rad=.2"))
        for i in range(len(ibat_start_list)):
            plt.annotate('(%ss, vbat=%smV)' % (time_vbat_list[ibat_start_list[i]],vbat_list[ibat_start_list[i]]),
                         xy=(time_vbat_list[ibat_start_list[i]],vbat_list[ibat_start_list[i]]), xycoords='data', xytext=(-50, +20),
                         textcoords='offset points', fontsize=16,
                         arrowprops=dict(arrowstyle='->', connectionstyle="arc3,rad=.2"))
        for i in range(len(ibat_low_list)):
            plt.annotate('(%ss, ocv=%smV)' % (time_ocv_list[ibat_low_list[i]],ocv_list[ibat_low_list[i]]),
                         xy=(time_ocv_list[ibat_low_list[i]],ocv_list[ibat_low_list[i]]), xycoords='data', xytext=(+30, -100),
                         textcoords='offset points', fontsize=16,
                         arrowprops=dict(arrowstyle='->', connectionstyle="arc3,rad=.2"))
        for i in range(len(ibat_start_list)):
            plt.annotate('(%ss, ocv=%smV)' % (time_ocv_list[ibat_start_list[i]],ocv_list[ibat_start_list[i]]),
                         xy=(time_ocv_list[ibat_start_list[i]],ocv_list[ibat_start_list[i]]), xycoords='data', xytext=(-50, +20),
                         textcoords='offset points', fontsize=16,
                         arrowprops=dict(arrowstyle='->', connectionstyle="arc3,rad=.2"))
        if(self.time_to_100 != 0):
            plt.annotate('(%ss, ocv=%smV)' % (time_ocv_list[self.time_to_100],ocv_list[self.time_to_100]),
                         xy=(time_ocv_list[self.time_to_100],ocv_list[self.time_to_100]), xycoords='data', xytext=(+30, -80),
                        textcoords='offset points', fontsize=16,
                        arrowprops=dict(arrowstyle='->', connectionstyle="arc3,rad=.2"))
        ax2=plt.twinx()
        #Charging Current plot
        x_ibat = time_ibat_list
        y_ibat = ibat_list
        ax2.set_ylabel("Current")
        ax2.plot(x_ibat,y_ibat, color="r", label="charging current")
        ax2.legend(loc='lower right')

        for i in range(len(ibat_start_list)):
            plt.annotate('(%ss, %s%%, %smA)' %
                         (time_ibat_list[ibat_start_list[i]],coul_percentage_list[ibat_start_list[i]],ibat_list[ibat_start_list[i]]),
                         xy=(time_ibat_list[ibat_start_list[i]],coul_percentage_list[ibat_start_list[i]]), xycoords='data', xytext=(+30, +30),
                         textcoords='offset points', fontsize=16,
                         arrowprops=dict(arrowstyle='->', connectionstyle="arc3,rad=.2"))

    def discharge_plot(self):
        if(self.platform == 'a'):
            self.a64_discharge_plot()
        elif bat.platform == 's':
            bat.sc20_discharge_plot()

    def sc20_discharge_plot(self): 
        plt.ylim(0,105)
        new_ticks = np.linspace(0, 100, 21)
        x_calsoc = np.arange(0,len(calsoc_list))
        y_calsoc = calsoc_list

        x_realsoc = np.arange(0,len(reprt_percentage_list))
        y_realsoc = reprt_percentage_list
        plt.yticks(new_ticks)
        plt.ylabel("capacity")
        plt.grid()
        plt.plot(x_calsoc,y_calsoc,'b',label="Calculated Soc",)
        plt.plot(x_realsoc,y_realsoc, 'r',label="Displayed Soc")
        plt.legend(loc='best')
        if (self.time_to_100 != 0):
            plt.annotate('(%ss, %s%%, ocv=%smV)' % (self.time_to_100,100,ocv_list[self.time_to_100]), xy=(self.time_to_100,100),
                         xycoords='data', xytext=(+30, -30),
                         textcoords='offset points', fontsize=16,
                         arrowprops=dict(arrowstyle='->', connectionstyle="arc3,rad=.2"))
        #plt.annotate('(%s,%s)' % (first_below_100_percent,reprt_percentage_list[first_below_100_percent]), 
        #             xy=(first_below_100_percent,reprt_percentage_list[first_below_100_percent]), xycoords='data', xytext=(+130, -130),
        #             textcoords='offset points', fontsize=16,
        #             arrowprops=dict(arrowstyle='->', connectionstyle="arc3,rad=.2"))

    def a64_discharge_plot(self): 
        # find the first point at 100% in coul
        x1 = time_reprtp_list
        y1 = reprt_percentage_list
        x1_1 = time_coulp_list
        y1_1 = coul_percentage_list
        if (self.time_to_100 != 0):
            plt.annotate('(%ss, %s%%, ocv=%smV)' % (time_ocvp_list[self.time_to_100],100,ocv_list[self.time_to_100]),
                         xy=(time_ocvp_list[self.time_to_100],100), xycoords='data', xytext=(+30, -60),
                         textcoords='offset points', fontsize=16,
                         arrowprops=dict(arrowstyle='->', connectionstyle="arc3,rad=.2"))
        #plt.annotate('(%s,%s)' % (time_to_100+bat_100_len,vbat_list[time_to_100+bat_100_len-1]),
        #             xy=(time_to_100+bat_100_len,vbat_list[time_to_100+bat_100_len-1]), xycoords='data', xytext=(+30, -30),
        #             textcoords='offset points', fontsize=16,
        #             arrowprops=dict(arrowstyle='->', connectionstyle="arc3,rad=.2"))
        #plt.annotate('(%s,%s)' % (time_to_100+ocv_100_len,ocv_list[time_to_100+ocv_100_len-1]),
        #             xy=(time_to_100+ocv_100_len,ocv_list[time_to_100+ocv_100_len-1]), xycoords='data', xytext=(+80, -80),
        #             textcoords='offset points', fontsize=16,
        #             arrowprops=dict(arrowstyle='->', connectionstyle="arc3,rad=.2"))

        plt.title( self.filename + '\n' "Discharging")
        plt.xlabel("seconds")
        plt.ylim(0,105)
        new_ticks = np.linspace(0, 100, 21)
        plt.yticks(new_ticks)
        plt.ylabel("Capacity")
        plt.grid()
        plt.plot(x1,y1,'b',label="Report percentage")
        plt.plot(x1_1,y1_1, 'r',label="Real percentage")
        plt.legend(loc='best')

if __name__ == '__main__':
    bat=battery_parser()
    if bat.platform == 'a':
        bat.a64_parser()
    elif bat.platform == 's':
        bat.sc20_parser()
    else:
        print 'assign platform (a or s) => (a64 or sc20)'

    if bat.mode == 'c':
        bat.charge_plot()
        plt.show()
    elif bat.mode == 'd':
        bat.discharge_plot()
        plt.show()
    elif bat.mode == 'r':
        bat.range_plot()
        plt.show()
    else:
        print 'assign (c or d) => (charge or discharge)'

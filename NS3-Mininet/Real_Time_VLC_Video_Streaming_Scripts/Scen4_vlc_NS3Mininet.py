#Author: Jakub Bryl

from mininet.net import Mininet
from mininet.node import Node, Switch
from mininet.link import Link, Intf
from mininet.log import setLogLevel, info
from mininet.cli import CLI

import mininet.ns3
from mininet.ns3 import WIFISegment

import ns.core
import ns.wifi
import ns.flow_monitor
import sys
import argparse
import time
import ns.config_store


def Main():
    parser = argparse.ArgumentParser(description='802.11ac mininet-ns3 scenario')
    parser.add_argument('-g', '--GI', help='Setting Guard Interval', action='store_true', default=False)
    parser.add_argument('-b', '--BANDWIDTH', help='Set bandwidth', default=40, type = int)
    parser.add_argument('-m', '--MCS', help='Setting MCS', default=3, type = int)
    parser.add_argument('-u', '--UDP', help='Turning off UDP protocol', action='store_false', default=True)
    parser.add_argument('-t', '--TP', help='Setting client throughout', default=54, type = float)
    parser.add_argument('-p', '--PCAP', help='Enable Pcap collection', action='store_true', default=False)
    
    args = parser.parse_args()

    Start(args.GI, args.MCS, args.BANDWIDTH, args.UDP, args.TP, args.PCAP)
    
def Start(GI=False, MCS=3, Bandwidth=40, UDP=True, TP=54, PCAP=False):
    setLogLevel( 'info' )
    #info( '*** ns-3 network demo\n' )
    net = Mininet()

    #info( '*** Creating Network\n' )
    h0 = net.addHost( 'h0')
    #h1 = net.addHost( 'h1' )
    h2 = net.addHost( 'h2')

    wifi = WIFISegment()

    #CONFIGURATION
    udp = UDP
    gi = GI #0,1
    bandwidth = Bandwidth #20,40,80
    mcs = MCS #2,4,7
    
    # ns.core.Config.SetDefault ("ns3::TcpSocket::SegmentSize", ns.core.UintegerValue (payloadSize))
    

    wifi.wifihelper.SetStandard(ns.wifi.WIFI_PHY_STANDARD_80211ac)

    # Enabling Shor guard intervals:
    wifi.phyhelper.Set("ShortGuardEnabled",ns.core.BooleanValue(gi))
    
    DataRate = "VhtMcs"+str(mcs)

    # set datarate for node h0
    wifi.wifihelper.SetRemoteStationManager( "ns3::ConstantRateWifiManager",
                                             "DataMode", ns.core.StringValue (DataRate), "ControlMode", ns.core.StringValue (DataRate) )
    
    wifi.machelper = ns.wifi.WifiMacHelper()
   
    Sssid = "wifi-80211ac"

    wifi.addSta( h0, ssid=Sssid, qosSupported=True, ext="ac")
    wifi.addAp( h2, ssid=Sssid, qosSupported=True,  ext="ac")

    # mininet.ns3.setPosition( h0, 10.0, 10.0, 0.0)
    # mininet.ns3.setPosition( h2, 5.0, 5.0, 0.0)

    # set channel bandwidth
    ns.core.Config.Set ("/NodeList/*/DeviceList/*/$ns3::WifiNetDevice/Phy/ChannelWidth", ns.core.UintegerValue (bandwidth))

    if PCAP == True:
        wifi.phyhelper.SetPcapDataLinkType (ns.wifi.WifiPhyHelper.DLT_IEEE802_11_RADIO)
        wifi.phyhelper.EnablePcap( "AP_Scen4STA_VLCStreaming_NS3Mininet.pcap", h0.nsNode.GetDevice( 0 ), True, True )
        #wifi.phyhelper.EnablePcap( "Ap-h1.pcap", h1.nsNode.GetDevice( 1 ), True, True );
        wifi.phyhelper.EnablePcap( "AP_Scen4_VLCStreaming_NS3Mininet.pcap", h2.nsNode.GetDevice( 0 ), True, True )
    
    #info( '*** Configuring hosts\n' )
    h0.setIP('192.168.123.1/24')
    #h1.setIP('192.168.123.2/24')
    h2.setIP('192.168.123.3/24')

    ns.core.Config.SetDefault ("ns3::ConfigStore::Filename", ns.core.StringValue ("output-attr.xml"))
    ns.core.Config.SetDefault ("ns3::ConfigStore::FileFormat", ns.core.StringValue ("Xml"))
    ns.core.Config.SetDefault ("ns3::ConfigStore::Mode", ns.core.StringValue ("Save"))
    outputConfig = ns.config_store.ConfigStore ()
    #outputConfig.ConfigureDefaults ()
    outputConfig.ConfigureAttributes ()
    

    mininet.ns3.start()
    
    
    h2.cmd("iptables -t mangle -N mark-tos")
    h2.cmd("iptables -t mangle -A OUTPUT -j mark-tos")
    h2.cmd("iptables -t mangle -A mark-tos -p tcp --sport 5004 -j TOS --set-tos 0x05")
    h2.cmd("iptables -t mangle -A mark-tos -p tcp --dport 5004 -j TOS --set-tos 0x05")
    h2.cmd("iptables -t mangle -A mark-tos -p tcp --sport 5005 -j TOS --set-tos 0x04")
    h2.cmd("iptables -t mangle -A mark-tos -p tcp --dport 5005 -j TOS --set-tos 0x04")

    h0.cmd("iptables -t mangle -N mark-tos")
    h0.cmd("iptables -t mangle -A OUTPUT -j mark-tos")
    h0.cmd("iptables -t mangle -A mark-tos -p tcp --sport 5004 -j TOS --set-tos 0x05")
    h0.cmd("iptables -t mangle -A mark-tos -p tcp --dport 5004 -j TOS --set-tos 0x05")
    h0.cmd("iptables -t mangle -A mark-tos -p tcp --sport 5005 -j TOS --set-tos 0x04")
    h0.cmd("iptables -t mangle -A mark-tos -p tcp --dport 5005 -j TOS --set-tos 0x04")
  
    h0.cmd("ifconfig h0-eth0 mtu 1452 ")
    h2.cmd("ifconfig h2-eth0 mtu 1452 ")

    info( '*** Testing network connectivity \n' )
    h0.cmdPrint("ping 192.168.123.3 -c 3")

    # info( '*** Testing network connectivity\n' )
    # h0.cmd("tcpdump -i h0-eth0 -w h0_test.pcap & ")
    # h2.cmd("tcpdump -i h2-eth0 -w h2_test.pcap & ")

    #info( '***Position of our architecture***\n')
    #info( 'STA:', mininet.ns3.getPosition( h0 ), '\n')
    #info( 'AP:', mininet.ns3.getPosition( h2 ), '\n')

    info( '**Opening stream of Video Bunny Rabbit in HQ from AP to STA***\n')
    h2.cmd( " $(echo Y3ZsYyBmaWxlOi8vL2hvbWUvb3Nib3hlcy9Eb3dubG9hZHMvYmJiX3N1bmZsb3dlcl8yMTYwcF82MGZwc19ub3JtYWwubXA0IC0tc291dD0jaHR0cHttdXg9ZmZtcGVne211eD1mbHZ9LGRzdD06NTAwNC99IC0tbm8tc291dC1hbGwgLS1zb3V0LWtlZXAK | base64 -d) &")    
    
    time.sleep(0.5)
    
    info( '**Opening HTTP stream on STA***\n')
    #Use h0 vlc-wrapper to open VLC on host 0
    h0.cmdPrint( "cvlc http://192.168.123.3:5004/ &")

    time.sleep(8)
    
    info( '*** Voice measurement\n' )
    h0.cmd( "iperf3 -s -i 1 -p 9998 | tee sta_VO_Scen3.txt &" )
    h2.cmd( "iperf3 -s -i 1 -p 9989 | tee  ap_VO_Scen3.txt &" )
    
    time.sleep(2)

    val = "iperf3 -c 192.168.123.1 -u -b 90k -Z --length 160 -p 9998 -t 30 -i 1 --cport 9998  -S 0x06 &"
    h2.cmd(val)
    val = "iperf3 -c 192.168.123.3 -u -b 90k -Z --length 160 -p 9989 -t 30 -i 1 --cport 9989  -S 0x06 &"
    h0.cmd(val)

    time.sleep(9)

    info( '**Streaming of Video Panasonic from AP to STA HTTP traffic***\n')
    h0.cmd( " $(echo Y3ZsYyBmaWxlOi8vL2hvbWUvb3Nib3hlcy9Eb3dubG9hZHMvUGFuYXNvbmljX0hEQ19UTV83MDBfUF81MGkubXA0IC0tc291dD0jaHR0cHttdXg9ZmZtcGVne211eD1mbHZ9LGRzdD06NTAwNS99IC0tc291dC1hbGwgLS1zb3V0LWtlZXAK | base64 -d) &")    

    time.sleep(1)
    
    info( '**Opening HTTP stream 2 on STA***\n')
    #Scen 4
    h2.cmdPrint( "cvlc http://192.168.123.1:5005/ &")

    time.sleep(8)
    # #CLI(net)
    info( '*** BE&BK measurement\n' )
    h0.cmd( "iperf3 -s -i 1 -p 9977 | tee sta_BE_Scen3.txt &" )
    
    time.sleep(1)

    val = "iperf3 -c 192.168.123.1 -M 750 -l 750 -Z -b 1m -p 9977 -t 10 --cport 9997 -i 1 -S 0x0 &"
    h2.cmd(val)


    info( '**Transmission will take 30s***\n')
    time.sleep(11)
    
    info("***Ending TCPDump and cleaning up***\n")
    h0.cmd("killall tcpdump")
    h2.cmd("killall tcpdump")
    h0.cmd("pkill -9 vlc")
    h2.cmd("pkill -9 vlc")

    mininet.ns3.stop()      
    mininet.ns3.clear()
    net.stop()

if __name__ == '__main__':
    Main()


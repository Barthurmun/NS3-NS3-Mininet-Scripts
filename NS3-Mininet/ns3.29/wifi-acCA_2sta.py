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
import sys
import argparse

def Main():
    parser = argparse.ArgumentParser(description='802.11acCA mininet-ns3 scenario')
    parser.add_argument('-g', '--GI', help='Setting Guard Interval', action='store_true', default=False)
    parser.add_argument('-b', '--BANDWIDTH', help='Set bandwidth', default=20, type = int)
    parser.add_argument('-m', '--MCS', help='Setting MCS', default=2, type = int)
    parser.add_argument('-u', '--UDP', help='Turning off UDP protocol', action='store_false', default=True)
    parser.add_argument('-t', '--TP', help='Setting client throughout', default=20, type = float)
    parser.add_argument('-p', '--PCAP', help='Enable Pcap collection', action='store_true', default=False)
    
    args = parser.parse_args()

    Start(args.GI, args.MCS, args.BANDWIDTH, args.UDP, args.TP, args.PCAP)

def Start(GI=False, MCS=2, Bandwidth=20, UDP=True, TP=20, PCAP=False):
    setLogLevel( 'info' )
    #info( '*** ns-3 network demo\n' )
    net = Mininet()

    #info( '*** Creating Network\n' )
    h0 = net.addHost( 'h0' )
    h1 = net.addHost( 'h1' )
    h2 = net.addHost( 'h2' )

    wifi = WIFISegment()

    #CONFIGURATION
    udp = UDP
    gi = GI #0,1
    bandwidth = Bandwidth #20,40,80
    mcs = MCS #2,4,7

    if udp == False:
        #TCP
        payloadSize = 1448  #bytes
        ns.core.Config.SetDefault ("ns3::TcpSocket::SegmentSize", ns.core.UintegerValue (payloadSize))
    else:
        payloadSize = 1472

    wifi.wifihelper.SetStandard(ns.wifi.WIFI_PHY_STANDARD_80211ac)

    # Enabling Shor guard intervals:
    wifi.phyhelper.Set("ShortGuardEnabled", ns.core.BooleanValue(gi))
    
    DataRate = "VhtMcs"+str(mcs)

    # set datarate for node h0
    wifi.wifihelper.SetRemoteStationManager( "ns3::ConstantRateWifiManager",
                                             "DataMode", ns.core.StringValue (DataRate), "ControlMode", ns.core.StringValue ("VhtMcs0") )
    
    wifi.machelper = ns.wifi.WifiMacHelper()
    
    #wifi.wifihelper.SetRemoteStationManager( "ns3::ConstantRateWifiManager",
    #                                         "DataMode", ns.core.StringValue ("VhtMcs8"), "ControlMode", ns.core.StringValue ("VhtMcs8") )
    
    Sssid = "wifi-80211acCA"
    
    wifi.addSta( h0,ext="ac",ca=True, ssid=Sssid )
    wifi.addSta( h1,ext="ac",ca=True, ssid=Sssid )
    wifi.addAp( h2,ext="ac",ca=True, ssid=Sssid  )
    
    # set channel bandwidth
    ns.core.Config.Set ("/NodeList/*/DeviceList/*/$ns3::WifiNetDevice/Phy/ChannelWidth", ns.core.UintegerValue (bandwidth))
    
    if PCAP == True:
        wifi.phyhelper.EnablePcap( "80211acCA_Sta1.pcap", h0.nsNode.GetDevice( 0 ), True, True );
        wifi.phyhelper.EnablePcap( "80211acCA_Sta2.pcap", h1.nsNode.GetDevice( 0 ), True, True );
        wifi.phyhelper.EnablePcap( "80211acCA_Ap.pcap", h2.nsNode.GetDevice( 0 ), True, True );
   
    #info( '*** Configuring hosts\n' )
    h0.setIP('192.168.123.1/24')
    h1.setIP('192.168.123.2/24')
    h2.setIP('192.168.123.3/24')

    mininet.ns3.start()

    
    #info( '\n *** Testing network connectivity\n' )
    net.pingFull([h0,h2])
    #net.pingFull([h1,h2])
    #net.pingFull([h0,h1])
    info('*** Starting UDP iperf server on AP(h2)\n')
    h2.sendCmd( "iperf -s -i 1 -u" )
    info( '*** Testing bandwidth between h0 and h2 while h1 is not transmitting\n' )
    val = "iperf -c 192.168.123.3 -u -b "+str(TP)+"M"
    h0.cmdPrint(val)
    info( '*** Testing bandwidth between h0 and h2 while h1 is also transmitting\n' )
    val = "iperf -c 192.168.123.3 -u -b "+str(TP)+"M"
    h1.sendCmd(val)
    h0.cmdPrint(val)
    
    #CLI(net)

if __name__ == '__main__':
    Main()
    
    

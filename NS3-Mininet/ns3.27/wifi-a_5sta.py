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
    parser = argparse.ArgumentParser(description='802.11a mininet-ns3 scenario')
    parser.add_argument('-or', '--OFDMRate', help='Setting OFDMRate', default=9, type = int)
    parser.add_argument('-tcp', '--UDP', help='Turning off UDP protocol', action='store_false', default=True)
    parser.add_argument('-t', '--TP', help='Setting client throughout', default=9, type = float)
    parser.add_argument('-p', '--PCAP', help='Enable Pcap collection', action='store_true', default=False)
    
    args = parser.parse_args()

    Start(args.OFDMRate, args.UDP, args.TP, args.PCAP)

def Start(OFDM_R=9, UDP=True, TP=9, PCAP=False):
    setLogLevel( 'info' )
    #info( '*** ns-3 network demo\n' )
    net = Mininet()

    #info( '*** Creating Network\n' )
    h0 = net.addHost( 'h0' )
    h1 = net.addHost( 'h1' )
    h2 = net.addHost( 'h2' )
    h3 = net.addHost( 'h3' )
    h4 = net.addHost( 'h4' )
    h5 = net.addHost( 'h5' )
    
    wifi = WIFISegment()
  
    #CONFIGURATION
    udp = UDP
    bandwidth = 20 
    ofdm_r = "OfdmRate"+str(OFDM_R)+"Mbps"
    OfdmRate = ofdm_r #9,24,48
    if udp == False:
        #TCP
        payloadSize = 1448  #bytes
        ns.core.Config.SetDefault ("ns3::TcpSocket::SegmentSize", ns.core.UintegerValue (payloadSize))
    else:
        payloadSize = 1472

    wifi = WIFISegment()

    wifi.wifihelper.SetStandard(ns.wifi.WIFI_PHY_STANDARD_80211a)
  
    wifi.wifihelper.SetRemoteStationManager( "ns3::ConstantRateWifiManager",
                                             "DataMode", ns.core.StringValue (OfdmRate), "ControlMode", ns.core.StringValue ("OfdmRate9Mbps") )
    
    Sssid = "wifi-80211a"

    wifi.addSta( h0, ssid=Sssid )
    wifi.addSta( h1, ssid=Sssid )
    wifi.addSta( h2, ssid=Sssid )
    wifi.addSta( h3, ssid=Sssid )
    wifi.addSta( h4, ssid=Sssid )
    wifi.addAp( h5, ssid=Sssid  )

    # set channel bandwidth
    ns.core.Config.Set ("/NodeList/*/DeviceList/*/$ns3::WifiNetDevice/Phy/ChannelWidth", ns.core.UintegerValue (bandwidth))
    
    if PCAP == True:
        wifi.phyhelper.EnablePcap( "80211a_sta1.pcap", h0.nsNode.GetDevice( 0 ), True, True );
        wifi.phyhelper.EnablePcap( "80211a_sta2.pcap", h1.nsNode.GetDevice( 0 ), True, True );
        wifi.phyhelper.EnablePcap( "80211a_sta3.pcap", h2.nsNode.GetDevice( 0 ), True, True );
        wifi.phyhelper.EnablePcap( "80211a_sta4.pcap", h3.nsNode.GetDevice( 0 ), True, True );
        wifi.phyhelper.EnablePcap( "80211a_sta5.pcap", h4.nsNode.GetDevice( 0 ), True, True );
        wifi.phyhelper.EnablePcap( "80211a_ap.pcap", h5.nsNode.GetDevice( 0 ), True, True );

    #info( '*** Configuring hosts\n' )
    h0.setIP('192.168.123.1/24')
    h1.setIP('192.168.123.2/24')
    h2.setIP('192.168.123.3/24')
    h3.setIP('192.168.123.4/24')
    h4.setIP('192.168.123.5/24')
    h5.setIP('192.168.123.6/24')

    mininet.ns3.start()


    #info( '\n *** Testing network connectivity\n' )
    net.pingFull([h0,h5])
    #net.pingFull([h1,h2])
    #net.pingFull([h0,h1])
    info('*** Starting UDP iperf server on AP(h5)\n')
    h5.sendCmd( "iperf -s -i 1 -u" )
    info( '*** Testing bandwidth between h0 and h5 while others stas are not transmitting\n' )
    val = "iperf -c 192.168.123.6 -u -b "+str(TP)+"M"
    h0.cmdPrint(val)
    info( '*** Testing bandwidth between h0 and h5 while all stats are also transmitting\n' )
    val = "iperf -c 192.168.123.6 -u -b "+str(TP)+"M"
    h0.sendCmd(val)
    h1.sendCmd(val)
    h2.sendCmd(val)
    h3.sendCmd(val)
    h4.cmdPrint(val)
    
    #CLI(net)
   
    
if __name__ == '__main__':
    Main()

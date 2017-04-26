#!/usr/bin/python3
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-

import logging
import pyroute2


def get_plugin_list():
    return [
        "aliyun",
    ]


def get_plugin(name):
    if name == "aliyun":
        return _PluginObject()
    else:
        assert False


class _PluginObject:

    def __init__(self):
        pass

    def init2(self, cfg, tmpDir, ownResolvConf):
        self.cfg = cfg
        self.tmpDir = tmpDir
        self.ownResolvConf = ownResolvConf
        self.proc = None

    def start(self):
        if "nameservers" in self.cfg["internet"]:
            with open(self.ownResolvConf, "w") as f:
                for ns in self.cfg["internet"]["nameservers"]:
                    f.write("nameserver %s\n" % (ns))
            logging.info("WAN: Nameservers are \"%s\"." % ("\",\"".join(self.cfg["internet"]["nameservers"])))

    def stop(self):
        with open(self.ownResolvConf, "w") as f:
            f.write("")

    def get_out_interface(self):
        return "eth1"

    def interface_appear(self, ifname):
        if ifname == "eth0":
            if "intranet" in self.cfg:
                ip, netmask = self.cfg["intranet"]["ip"].split("/")
                with pyroute2.IPRoute() as ip:
                    idx = ip.link_lookup(ifname="eth0")[0]
                    ip.link("set", index=idx, state="up")
                    ip.addr("add", index=idx, address=ip, mask=netmask)
                    if "routes" in self.cfg["intranet"]:
                        for rt in self.cfg["intranet"]["routes"]:
                            ip.route('add', dst=rt["prefix"], gateway=rt["gateway"], oif=idx)
            logging.info("WAN: Internet interface \"%s\" is managed." % (ifname))
            return True

        if ifname == "eth1":
            ip, netmask = self.cfg["internet"]["ip"].split("/")
            with pyroute2.IPRoute() as ip:
                idx = ip.link_lookup(ifname="eth1")[0]
                ip.link("set", index=idx, state="up")
                ip.addr("add", index=idx, address=ip, mask=netmask)
                if "gateway" in self.cfg["internet"]:
                    ip.route('add', dst="0.0.0.0/0", gateway=self.cfg["internet"]["gateway"], oif=idx)
            logging.info("WAN: Internet interface \"%s\" is managed." % (ifname))
            return True

        return False

    def interface_disappear(self, ifname):
        pass
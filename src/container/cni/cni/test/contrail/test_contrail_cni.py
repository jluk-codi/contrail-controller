import errno
import argparse
import json
import mock
import os
import requests
import sys
import unittest
from pyroute2 import iproute
from mock import patch
from mock import Mock
from StringIO import StringIO

from cni.tungsten import vrouter
from cni.tungsten.tungsten_cni import TungstenCni, VRouter, CniVEthPair, CniMacVlan, Cni, Error


class TungstenCniTest(unittest.TestCase):
    @mock.patch('argparse.ArgumentParser.parse_args',
                return_value=argparse.Namespace(command=None, version=Cni.CNI_VERSION,
                                                file=None, uuid='123'))
    def setUp(self, _):
        self._tungsten_json = """
{
    "tungsten": {
        "log-file": "%s",
        "log-level": "%s",
        "mode": "%s",
        "vif-type": "%s",
        "parent-interface": "%s"
    }
}
"""
        self.tungsten_json = self._build_tungsten_json('/tmp/cni.log',
                                                       'WARNING',
                                                       'mesos',
                                                       'veth',
                                                       'eth0')
        old_stdin = sys.stdin
        sys.stdin = StringIO()
        sys.stdin.write(self.tungsten_json)
        sys.stdin.seek(0)
        os.environ['CNI_COMMAND'] = 'version'
        self.tungsten_cni = TungstenCni()
        sys.stdin = old_stdin


    def tearDown(self):
        pass

    def _build_tungsten_json(self, log_file, log_level,
                             mode, vif_type, parent_iface):
        return self._tungsten_json % (log_file, log_level,
                                      mode, vif_type, parent_iface)

    def test_build_response(self):
        vr_resp = {
            'ip-address': '10.1.2.3',
            'dns-server': '10.1.0.100',
            'gateway': '10.1.0.1',
            'plen': 16
        }
        oldout,olderr = sys.stdout, sys.stderr
        try:
            out = StringIO()
            sys.stdout = out
            self.tungsten_cni.build_response(vr_resp)
            sys.stdout.seek(0)
            response = json.loads(sys.stdout.read())
            self.assertEqual(response, {
                'cniVersion': Cni.CNI_VERSION,
                'ip4': {
                    'gateway': '10.1.0.1',
                    'ip': '10.1.2.3/16',
                    'routes': [{
                        'dst': '0.0.0.0/0',
                        'gw': '10.1.0.1'
                    }]
                },
                'dns': {
                    'nameservers': ['10.1.0.100']
                }
            })
        finally:
            sys.stdout,sys.stderr = oldout, olderr


    # @patch.object(Cni, "BuildCniResponse")
    # def test_get_cmd(self, mock_build_resp):
    #     mock_build_resp.side_effect = lambda x: x
    #     mock_params = Mock(spec=params.Params)
    #     mock_params.k8s_params = Mock(spec=params.K8SParams)
    #     mock_params.k8s_params.pod_uuid = 123
    #     mock_vrouter = Mock(spec=vrouter.VRouter)
    #     mock_vrouter.get_cmd = lambda x, y: {'result':'ok'} if x==123 else {}
    #     c = Cni(mock_vrouter, mock_params)
    #     self.assertEqual(c.get_cmd(), {'result': 'ok'})
    @patch.object(VRouter, "get_cmd")
    def test_get_cmd(self, mock_get_cmd):
        mock_get_cmd.return_value = {
            'ip-address': '10.1.2.3',
            'dns-server': '10.1.0.100',
            'gateway': '10.1.0.1',
            'plen': 16
        }
        oldout = sys.stdout
        try:
            out = StringIO()
            sys.stdout = out
            self.tungsten_cni.get_cmd()
            mock_get_cmd.assert_called_once_with('123', None)
            sys.stdout.seek(0)
            response = json.loads(sys.stdout.read())
            self.assertEqual(response, {
                'cniVersion': Cni.CNI_VERSION,
                'ip4': {
                    'gateway': '10.1.0.1',
                    'ip': '10.1.2.3/16',
                    'routes': [{
                        'dst': '0.0.0.0/0',
                        'gw': '10.1.0.1'
                    }]
                },
                'dns': {
                    'nameservers': ['10.1.0.100']
                }
            })
        finally:
            sys.stdout = oldout

    @patch.object(VRouter, "poll_cmd")
    def test_poll_cmd(self, mock_poll_cmd):
        mock_poll_cmd.return_value = {
            'ip-address': '10.1.2.3',
            'dns-server': '10.1.0.100',
            'gateway': '10.1.0.1',
            'plen': 16
        }
        oldout = sys.stdout
        try:
            out = StringIO()
            sys.stdout = out
            self.tungsten_cni.poll_cmd()
            mock_poll_cmd.assert_called_once_with('123', None)
            sys.stdout.seek(0)
            response = json.loads(sys.stdout.read())
            self.assertEqual(response, {
                'cniVersion': Cni.CNI_VERSION,
                'ip4': {
                    'gateway': '10.1.0.1',
                    'ip': '10.1.2.3/16',
                    'routes': [{
                        'dst': '0.0.0.0/0',
                        'gw': '10.1.0.1'
                    }]
                },
                'dns': {
                    'nameservers': ['10.1.0.100']
                }
            })
        finally:
            sys.stdout = oldout

    @patch("cni.tungsten.tungsten_cni.CniMacVlan")
    @patch("cni.tungsten.tungsten_cni.CniVEthPair")
    @patch.object(VRouter, "add_cmd")
    @patch.object(VRouter, "poll_cfg_cmd")
    def test_add_cmd(self, mock_poll_cfg_cmd, mock_vrouter_add_cmd,
                     mock_veth, mock_macvlan):
        mock_poll_cfg_cmd = lambda x, y: {
            'mac-address': '00',
            'vlan-id': '1'
        } if x == '123' else {}
        mock_vrouter_add_cmd.return_value = {
            'mac-address': '00',
            'ip-address': '10.0.0.123',
            'plen': 16,
            'gateway': '10.0.0.1',
            'dns-server': '10.0.0.100',
        }
        mock_veth.host_ifname = 'eth0'
        intf = Mock()
        mock_veth.return_value = intf
        oldout = sys.stdout
        try:
            out = StringIO()
            sys.stdout = out
            self.tungsten_cni.add_cmd()
            sys.stdout.seek(0)
            response = json.loads(sys.stdout.read())
            self.assertEqual(response, {
                'cniVersion': Cni.CNI_VERSION,
                'ip4': {
                    'gateway': '10.0.0.1',
                    'ip': '10.0.0.123/16',
                    'routes': [{
                        'dst': '0.0.0.0/0',
                        'gw': '10.0.0.1'
                    }]
                },
                'dns': {
                    'nameservers': ['10.0.0.100']
                }
            })
            intf.create_interface.assert_called_once_with()
            intf.configure_interface.assert_called_once_with('10.0.0.123', 16, '10.0.0.1')
        finally:
            sys.stdout = oldout


    @patch("cni.tungsten.tungsten_cni.CniMacVlan")
    @patch("cni.tungsten.tungsten_cni.CniVEthPair")
    @patch.object(VRouter, "delete_cmd")
    def test_delete_cmd(self, mock_delete_cmd, mock_veth, mock_macvlan):
        intf = Mock()
        mock_veth.return_value = intf
        oldout = sys.stdout
        try:
            out = StringIO()
            sys.stdout = out
            self.tungsten_cni.delete_cmd()
            sys.stdout.seek(0)
            response = json.loads(sys.stdout.read())
            self.assertEqual(response, {
                'cniVersion': Cni.CNI_VERSION,
                'code': 0,
                'msg': 'Delete passed'
            })
            intf.delete_interface.assert_called_once_with()
        finally:
            sys.stdout = oldout


    def test_Version(self):
        oldout = sys.stdout
        try:
            out = StringIO()
            sys.stdout = out
            self.tungsten_cni.Version()
            sys.stdout.seek(0)
            response = json.loads(sys.stdout.read())
            self.assertEqual(response, {
                'cniVersion': Cni.CNI_VERSION,
                'supportedVersions': [Cni.CNI_VERSION]
            })
        finally:
            sys.stdout = oldout

    @mock.patch('argparse.ArgumentParser.parse_args',
                return_value=argparse.Namespace(command=None, version=Cni.CNI_VERSION,
                                                file=None, uuid='123'))
    @patch.object(TungstenCni, "Version")
    @patch.object(TungstenCni, "add_cmd")
    @patch.object(TungstenCni, "delete_cmd")
    @patch.object(TungstenCni, "get_cmd")
    @patch.object(TungstenCni, "poll_cmd")
    def test_Run(self, mock_poll, mock_get, mock_delete, mock_add, mock_version, _):
        self.tungsten_json = self._build_tungsten_json('/tmp/cni.log',
                                                       'WARNING',
                                                       'mesos',
                                                       'veth',
                                                       'eth0')
        old_stdin = sys.stdin
        sys.stdin = StringIO()
        sys.stdin.write(self.tungsten_json)
        sys.stdin.seek(0)
        tungsten_cni = TungstenCni()
        sys.stdin = old_stdin
        mock_cni_tungsten_cni = Mock()
        tungsten_cni.cni = mock_cni_tungsten_cni

        mock_cni_tungsten_cni.command = Cni.CNI_CMD_VERSION
        tungsten_cni.Run()
        mock_version.assert_called_once_with()

        mock_cni_tungsten_cni.command = Cni.CNI_CMD_ADD
        tungsten_cni.Run()
        mock_add.assert_called_once_with()

        mock_cni_tungsten_cni.command = Cni.CNI_CMD_DELETE
        tungsten_cni.Run()
        mock_delete.assert_called_once_with()

        mock_cni_tungsten_cni.command = TungstenCni.CONTRAIL_CNI_CMD_GET
        tungsten_cni.Run()
        mock_get.assert_called_once_with()

        mock_cni_tungsten_cni.command = TungstenCni.CONTRAIL_CNI_CMD_POLL
        tungsten_cni.Run()
        mock_poll.assert_called_once_with()

        mock_cni_tungsten_cni.command = "unknown"
        self.assertRaises(Error, tungsten_cni.Run)

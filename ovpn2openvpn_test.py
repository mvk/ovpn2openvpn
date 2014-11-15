#!/usr/bin/env python
from __future__ import print_function
__author__ = 'stubborn'

import ovpn2openvpn
import pytest
import os
import StringIO
import __builtin__


def test_read_data_from_fpath(monkeypatch):
    def mock_open_good(name, mode=None, buffering=None):
        out = StringIO.StringIO()
        out.write(expected)
        out.flush()
        out.seek(0)
        return out

    def mock_open_raiser(name, mode=None, buffering=None):
        raise OSError("Shit!")

    expected = "this is some data\n"

    monkeypatch.setattr(__builtin__, 'open', mock_open_good)
    actual = ovpn2openvpn.read_data_from_fpath("kukureku")
    assert expected == actual

    monkeypatch.setattr(__builtin__, 'open', mock_open_raiser)
    try:
        ovpn2openvpn.read_data_from_fpath("whatever here")
        assert False
    except OSError: ## mock raises this one
        assert True


def test_write_data_to_fpath(monkeypatch):
    expected = "this is some data\n"
    buf = StringIO.StringIO()

    def mocky_open(name, mode=None, buffering=None):
        return buf

    def mocky_close(whatever):
        pass
    monkeypatch.setattr(__builtin__, 'open', mocky_open)
    monkeypatch.setattr(StringIO.StringIO, 'close', mocky_close)

    ovpn2openvpn.write_data_to_fpath(expected, "lalala")
    buf.flush()
    buf.seek(0)
    actual = buf.read()
    assert expected == actual


def test_gen_fpath_name():
    #os.path.join(out_dir, ".".join([name, extension]))
    dname = "/kuku/path"
    name = "kiwi"
    ext = "kawa"
    expected = "/".join([dname, ".".join([name, ext])])
    actual = ovpn2openvpn.gen_fpath_name(dname, name, extension=ext)
    assert expected == actual

    expected = "/".join([dname, ".".join([name, "pem"])])
    actual = ovpn2openvpn.gen_fpath_name(dname, name)
    assert expected == actual

    try:
        ovpn2openvpn.gen_fpath_name(None, None)
        assert False
    except Exception:
        assert True


def test_ensure_out_dir(monkeypatch):
    def exists_true(path):
        return True

    def exists_false(path):
        return False

    def patch_makedirs_ok(path, mode=None):
        pass

    def patch_makedirs_raiser(path, mode=None):
        raise ValueError("shit!")

    monkeypatch.setattr(os.path, "exists", exists_true)
    try:
        ovpn2openvpn.ensure_out_dir("ksksks")
        assert True
    except Exception:
        assert False

    monkeypatch.setattr(os.path, "exists", exists_false)
    monkeypatch.setattr(os, "makedirs", patch_makedirs_ok)
    try:
        ovpn2openvpn.ensure_out_dir("ksksks")
        assert True
    except Exception:
        assert False

    monkeypatch.setattr(os, "makedirs", patch_makedirs_raiser)
    try:
        ovpn2openvpn.ensure_out_dir("ksksks")
        assert False
    except Exception:
        assert True


def test_get_tag_range_safe():
    start_tag = "<tagga>"
    end_tag = "</tagga>"
    expected = (3, 9)
    l = ["sksks"]*10
    l.insert(expected[0], start_tag)
    l.insert(expected[1], end_tag)

    actual = ovpn2openvpn.get_tag_range_safe(l, start_tag, end_tag)
    assert expected == actual

    l = ["sksks"]*10
    for i in expected:
        l.insert(i, start_tag)
    try:
        ovpn2openvpn.get_tag_range_safe(l, start_tag, end_tag)
        assert False
    except ValueError, ve:
        expected_msg = "Tag: {start_tag} appears at:".format(**locals())
        expected_msg += " " + str(expected[0]) + ", " + str(expected[1])
        assert expected_msg == ve.message

    l = ["sksks",]*10
    for i in expected:
        l.insert(i, end_tag)
    try:
        ovpn2openvpn.get_tag_range_safe(l, start_tag, end_tag)
        assert False
    except ValueError, ve:
        start_idx = -1
        end_idx = expected[0]
        expected_msg = " ".join([
            "error processing",
            start_tag + ".",
            "illegal range:",
            "=".join(["start_idx", str(start_idx)]),
            "is not before",
            "=".join(["end_idx", str(end_idx)]),
        ])
        assert expected_msg == ve.message

    l = ["sksks"]*10
    l.insert(expected[0], end_tag)
    l.insert(expected[1], start_tag)

    try:
        ovpn2openvpn.get_tag_range_safe(l, start_tag, end_tag)
        assert False
    except ValueError, ve:
        start_idx = -1
        end_idx = expected[0]
        expected_msg = " ".join([
            "error processing",
            start_tag + ".",
            "illegal range:",
            "=".join(["start_idx", str(start_idx)]),
            "is not before",
            "=".join(["end_idx", str(end_idx)]),
        ])
        assert expected_msg == ve.message


def test_parse_args():
    myargs = []
    args = ovpn2openvpn.parse_args(myargs)
    expected = ovpn2openvpn.default_in_conf
    actual = args.in_conf
    assert expected == actual
    expected = ovpn2openvpn.default_out_conf
    actual = args.out_conf
    assert expected == actual
    expected = ovpn2openvpn.default_out_folder
    actual = args.out_folder
    assert expected == actual

    expected = "/kuku/kasksk.conf"
    myargs = ["-i", expected]
    args = ovpn2openvpn.parse_args(myargs)
    actual = args.in_conf
    assert expected == actual
    myargs = ["-o", expected]
    args = ovpn2openvpn.parse_args(myargs)
    actual = args.out_conf
    assert expected == actual
    expected = "/kuku/kasksk.conf.d"
    myargs = ["-f", expected]
    args = ovpn2openvpn.parse_args(myargs)
    actual = args.out_folder
    assert expected == actual

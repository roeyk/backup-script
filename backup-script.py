#!/usr/bin/env python

# (c) 2014 Roey Katz
# Licensed under the terms of Gnu General Public License, revision 3.

# system imports
import sys
import time
import argparse
import os,os.path
from os.path import basename

# third-part imports
from plumbum import local
from plumbum.cmd import sudo,mount,umount

# global commands
btrfs = local["btrfs"]

# global vars
snapshots_repo_path = "/media/btrfs/"
snapshots_backup_path = "/media/backup/"
datetime_stamp = time.strftime("%Y%m%d-%H%M", time.gmtime())

def do_snapshot():
    """Perform snapshot"""
    
    for vol in build_snapshots_dict():
        snapshot_cmd(snapshots_repo_path, vol)

def snapshot_cmd(snapshot_repo_path, vol):
    """call btrfs sub snap to create a new snapshot"
    
    new_snapshot_path = os.path.join(snapshots_repo_path, vol, vol + "." + datetime_stamp)
    subvol_base = os.path.join(snapshots_repo_path, '@'+(vol if vol != 'toplevel' else ''))
    
    # call btrfs to take snapshots
    
    cmd = sudo[btrfs["sub","snap","-r", subvol_base, new_snapshot_path]]
    print cmd    
        
def do_backup():
    """Perform a backup"""
    
    snapshots = build_snapshots_dict()

    for vol in snapshots:
        try:
            backup_cmd(snapshots_repo_path, snapshots_backup_path, vol)
        except: 
            import traceback
            traceback.print_exc()

def backup_cmd(snapshots_repo_path, snapshots_backup_path, vol):
    """call btrfs send/receive to back up the last snapshot in the
    snapshots repository, relative to the last snapshot found on the
    backup device (if one is found)"""

    new_snapshot_backup_path = os.path.join(snapshots_backup_path, vol)

    # obtain name of latest snapshot on the backup device
    vol_snapshots_path = os.path.join(snapshots_backup_path, vol)
    last_backedup_snapshot = sorted(os.listdir(vol_snapshots_path))[-1]  
    
    last_snapshot_tuple = []    

    # if we found a backed-up snapshot on the backup device, then make this backup relative to it
    if last_backedup_snapshot != []:
        last_backedup_snapshot_path = os.path.join(vol_snapshots_path, last_backedup_snapshot)
        last_snapshot_tuple = ["-p", last_backedup_snapshot_path]        
        last_snapshot_tupe.append(last_backedup_snapshot_path)

    # call btrfs send/receive
    cmd = sudo[btrfs["send",last_snapshot_tuple]] | sudo[btrfs["receive",new_snapshot_backup_path]]
    print cmd

def mount_snapshots_repo():
    """Mount snapshots repository"""
    
    cmd = sudo[mount["-osubvolid=0","/dev/sda1","/media/btrfs"]]
    print cmd
    
def umount_snapshots_repo():
    """Unmount snapshots repository"""
    
    cmd = sudo[umount["/media/btrfs"]]
    print cmd
    
def build_snapshots_dict():
    """Build a dictionary of all snapshots, with volume names as keys and lists of snapshot paths as values"""
    
    snapshots = {} 

    btrfs_output = sudo[btrfs["sub", "list", "-a", "/"]]().splitlines()
    
    for l in btrfs_output:
        try:
            snapshot_path = l.split("<FS_TREE>")[1]
            volume, path = snapshot_path.split('.')
            snapshots[volume].append(path)
            
        except KeyError:   # we encountered a new volume
            snapshots[volume] = []
        except ValueError:  # line was not an entry line
               pass
           
    out_dict = {basename(vol):sorted(snapshots[vol]) for vol in snapshots}
    return out_dict


def main(args):
    """ snapshots and backups"""
    
    if args.snapshot:
        do_snapshot()
        
    if args.backup:
        do_backup()


# if run as a script, then process command-line arguments
if __name__=='__main__':

    # parse arguments
    parser = argparse.ArgumentParser(description='Snapshot and backup utility for BTRFS using send/receive.')
    parser.add_argument('-b','--backup', action='store_true', help='perform backup')
    parser.add_argument('-s','--snapshot', action='store_true', help='perform snapshot')
    args = parser.parse_args()

    # run main program
    main(args)

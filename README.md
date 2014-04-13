backup-script
=============

BTRFS backup script in Python

An easy automated snapshotting and send/receive backups with BTRFS filesystems

This command works in complement with the snapshotter-script. It should be run like this example of every four hours:

  sudo crontab -u root -e
  m h  dom mon dow   command
  1 * * * * /usr/bin/backup-script.py --snapshot
  * */4 * * * /usr/bin/backup-script.py --snapshot  --backup

Both backup host and backup drive should have mount options -noatime,compress.
This script assumes that:

  - /media exists
  - /media/btrfs has been mounted with the command
    sudo mount -o subvolid=0 /dev/sdN /media/btrfs.
  - backup drive has "toplevel", "home" and "arch" top-level directories
 
This script generates the following the following disk layout:


    media/

      btrfs/ (holds catalogue of snapshots)
        @home/
        @arch/
        @toplevel/
        home/
          home.20140415/
          home.20140416/
          ...
        arch/
          arch.20140415/
          arch.20140416/
          ...
        toplevel/
          toplevel.20140415/
          toplevel.20140416/
          ...

        backup/ (points to backup device.  Backups get stored here.)
          home/
            home.20140415/
            home.20140416/
            ...
          arch/
            arch.20140415/
            arch.20140416/
            ...
          toplevel/
            toplevel.20140415/
            toplevel.20140416/
            ...
